from cmath import log
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import re
import datetime
from passlib.hash import sha256_crypt
from db_CRUT import execute_read_query, execute_query

app = Flask(__name__)

app.secret_key = 'super secret key'
# app.permanent_session_lifetime = datetime.timedelta(seconds=60)
mysql = MySQL(app)


# Connect DB
def create_connection(host, user, password, db):
    connection = False
    try:
        app.config['MYSQL_HOST'] = host
        app.config['MYSQL_USER'] = user
        app.config['MYSQL_PASSWORD'] = password
        app.config['MYSQL_DB'] = db
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        print("Connection to MySQL DB successful")
        connection = True
        return connection

    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e


connect_db = create_connection('localhost', 'root', 'admin', 'appdroid')


@app.route('/', methods=['GET', 'POST'])
def check_user():
    check_sql = f'''SELECT id, phone_has_color.image, phone.brand, phone.model, phone.price, color_title
            FROM phone, phone_has_color where phone_has_color.count>0 and phone_has_color.phone_id = phone.id group by phone.model'''
    phone = execute_read_query(connect_db, check_sql)
    print(phone)

    if 'admin' in session and session.get('logged_in'):
        if session['admin']:
            return render_template('home.html')
        else:
            return render_template('home2.html', user_session=session.get('logged_in'), phone=phone)
    else:
        print(session.get('logged_in'))
        print("Сессия не активна.")
        return render_template('home2.html', phone=phone)


# Registration
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    msg = ''
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        nickname = request.form['nickname']
        password = sha256_crypt.hash(request.form['password'])

        check_sql = f'''select * from user where nickname = "{nickname}"'''
        account = execute_read_query(connect_db, check_sql)

        if account:
            msg = 'Этот никнейм уже занят.'
        elif len(request.form['nickname']) < 4:
            msg = 'Никнейм должен содержать не менее 4 символов.'
        elif not re.match(r'[A-Za-z0-9]', nickname):
            msg = 'Никнейм может содержать только латинские буквы.'
        elif not re.match(r'[А-Яа-я]', first_name or last_name):
            msg = 'Имя и фамилия могут содержать только кириллицу.'
        elif first_name[0].islower() or last_name[0].islower():
            msg = 'Имя и фамилия должны начинаться с заглавных букв.'
        elif len(request.form['password']) < 8:
            msg = 'Пароль должен содержать не менее 8 символов.'
        else:
            write_sql = f'''insert into user (`first_name`,`last_name`,`nickname`,`password`, `admin`) 
            values ('{first_name}', '{last_name}', '{nickname}', '{password}', '{0}')'''
            execute_query(connect_db, write_sql)
            return redirect(url_for('login'))
    return render_template('registration.html', msg=msg)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.referrer != request.url_root + 'login') and (request.referrer != request.url_root + 'reg'):
        session['request'] = request.referrer
    print(session.get('request'))
    msg = ''
    if request.method == 'POST' and 'nickname' in request.form and 'password' in request.form:
        nickname = request.form['nickname']
        password = request.form['password']

        check_sql = f'''select * from user where nickname = "{nickname}"'''
        login_user = execute_read_query(connect_db, check_sql)
        if login_user == tuple():
            msg = 'Неверный никнейм или пароль.'
        else:
            login_user = login_user[0]
            if sha256_crypt.verify(password, login_user['password']):
                if login_user['admin']:
                    session['logged_in'] = True
                    session['id'] = login_user['id']
                    session['first_name'] = login_user['first_name']
                    session['nickname'] = login_user['nickname']
                    session['admin'] = login_user['admin']
                    return redirect(url_for('check_user'))
                else:
                    session['logged_in'] = True
                    session['first_name'] = login_user['first_name']
                    session['nickname'] = login_user['nickname']
                    session['id'] = login_user['id']
                    session['admin'] = login_user['admin']
                    if session.get('request') is not None:
                        return redirect(session.get('request'))
                    return redirect(url_for('check_user'))
            else:
                msg = 'Неверный никнейм или пароль.'
    return render_template('login.html', msg=msg)


@app.route("/logout")
def logout():
    session.clear()
    session['request'] = request.referrer
    return redirect(session.get('request'))


@app.route("/details/<int:id>/<string:color_title>", methods=['GET', 'POST'])
def details(id, color_title):
    check_sql = f'''select * from phone, color, phone_has_color 
        where phone_has_color.count>0 
        and phone.id=phone_has_color.phone_id 
        and color.title=phone_has_color.color_title
        and phone.id={id} and phone_has_color.color_title='{color_title}' '''
    phone = execute_read_query(connect_db, check_sql)

    phone_count = f'''select phone_has_color.count from phone_has_color 
        where phone_has_color.phone_id={id} and phone_has_color.color_title='{color_title}' '''
    phone_count = execute_read_query(connect_db, phone_count)
    print(phone_count)

    colors_count = f'''select count(model) as count from phone where model = '{phone[0]["model"]}' '''
    colors_count = int(execute_read_query(connect_db, colors_count)[0]["count"])
    # print(colors_count)

    if phone == tuple():
        return redirect(url_for('check_user'))

    in_cart = None
    if session.get('id'):
        id_active_order = f'''select id from appdroid.order where user_id = {session['id']} 
                    and active = 1'''
        id_active_order = execute_read_query(connect_db, id_active_order)
        if id_active_order != tuple():

            in_cart = f'''select appdroid.order.id, appdroid.order.user_id, order_has_phone.order_id, 
            order_has_phone.phone_id, order_has_phone.phone_color, order_has_phone.count from appdroid.order, order_has_phone 
            where order_has_phone.order_id={id_active_order[0]['id']} and appdroid.order.user_id={session['id']} 
            and order_has_phone.phone_id={id} and order_has_phone.phone_color='{color_title}' '''
            in_cart = execute_read_query(connect_db, in_cart)
            if in_cart != tuple():
                in_cart_count = int(in_cart[0]['count'])
            else:
                in_cart_count = 1
            print(in_cart)

            if in_cart != tuple():
                in_cart = in_cart[0]['phone_id']
                # print(id_active_order)
                print("ЕСТЬ В КОРЗИНЕ")
                phones_count = f'''select sum(order_has_phone.count) as phones_count from order_has_phone 
                            where order_id={id_active_order[0]['id']} and phone_id={id}'''
                phones_count = execute_read_query(connect_db, phones_count)
                phones_count = int(phones_count[0]['phones_count'])
                return render_template("details.html", user_session=session.get('logged_in'),
                                       user_session_id=session.get('id'),
                                       phone=phone,
                                       in_cart=in_cart, phones_count=phones_count,
                                       colors_count=colors_count, phone_count=phone_count,
                                       in_cart_count=in_cart_count)

    return render_template("details.html", user_session=session.get('logged_in'),
                           phone=phone, in_cart=in_cart,
                           colors_count=colors_count, phone_count=phone_count)


@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    id_active_order = f'''select id from appdroid.order where user_id = {session['id']} 
    and active = 1'''
    id_active_order = execute_read_query(connect_db, id_active_order)

    if id_active_order == tuple():  # ЗАКАЗА НЕТ
        # print('НЕТ ЗАКАЗА')

        create_active_order = f'''insert into appdroid.order (`user_id`, `active`) 
        values ('{session['id']}', 1)'''
        execute_query(connect_db, create_active_order)
        # print('ЗАКАЗ СОЗДАН')

        id_active_order = f'''select id from appdroid.order where user_id = {session['id']} 
            and active = 1'''
        id_active_order = execute_read_query(connect_db, id_active_order)

        phone_id = request.form.get('phone_id')
        phone_color = request.form.get('phone_color')

        count = request.form.get('count')  # ДЛЯ КОЛИЧЕСТВА ТОВАРОВ
        # print(count)

        if phone_id and count and request.method == "POST":
            to_cart = f'''insert into order_has_phone (`order_id`, `phone_id`, `phone_color`, `count`, `add_date`)
                values ('{id_active_order[0]['id']}', '{phone_id}', '{phone_color}', '{count}', now())'''
            execute_query(connect_db, to_cart)

            # print('ДОБАВЛЕН В КОРЗИНУ')
        return redirect(request.referrer)

    if id_active_order != tuple():  # ЗАКАЗ ЕСТЬ
        # print('ЗАКАЗ ЕСТЬ')

        phone_id = request.form.get('phone_id')
        phone_color = request.form.get('phone_color')
        count = request.form.get('count')  # ДЛЯ КОЛИЧЕСТВА ТОВАРОВ
        # print(count)

        if phone_id and request.method == "POST":
            to_cart = f'''insert into order_has_phone (`order_id`, `phone_id`, `phone_color`, `count`, `add_date`)
                            values ('{id_active_order[0]['id']}', '{phone_id}', '{phone_color}', '{count}', now())'''
            execute_query(connect_db, to_cart)

            # print('ДОБАВЛЕН В КОРЗИНУ')
        return redirect(request.referrer)


@app.route("/cart")
def user_cart():
    if session.get('id'):
        id_active_order = f'''select id from appdroid.order where user_id = {session.get('id')} 
            and active = 1'''
        id_active_order = execute_read_query(connect_db, id_active_order)
        if id_active_order != tuple():
            check_sql = f'''SELECT id, OS, year, RAM, memory, phone_has_color.image, phone.brand, 
                        phone.model, phone.price, phone_has_color.color_title, order_has_phone.count
                        FROM phone, phone_has_color, order_has_phone, color 
                        where id=order_has_phone.phone_id 
                        and phone_has_color.phone_id = phone.id 
                        and order_has_phone.phone_color = phone_has_color.color_title and
                        order_has_phone.order_id={id_active_order[0]['id']} group by image 
                        order by add_date desc'''
            phone = execute_read_query(connect_db, check_sql)

            cart_bill = f'''select sum(price*order_has_phone.count) as bill from phone, order_has_phone 
            where order_has_phone.order_id={id_active_order[0]['id']} 
            and order_has_phone.phone_id=phone.id'''
            cart_bill = execute_read_query(connect_db, cart_bill)
            if cart_bill[0]['bill'] is not None:
                cart_bill = int(cart_bill[0]['bill'])
                phones_count = f'''select sum(order_has_phone.count) as phones_count from order_has_phone 
                where order_id={id_active_order[0]['id']}'''
                phones_count = execute_read_query(connect_db, phones_count)
                phones_count = int(phones_count[0]['phones_count'])

                return render_template("cart.html", user_session=session.get('logged_in'),
                                       phone=phone, cart_bill=cart_bill, phones_count=phones_count,
                                       id_active_order=id_active_order[0]['id'])

    return render_template("cart.html", user_session=session.get('logged_in'))


@app.route('/delete_from_cart', methods=['GET', 'POST'])
def delete_from_cart():
    id_active_order = f'''select id from appdroid.order where user_id = {session.get('id')} 
                    and active = 1'''
    id_active_order = execute_read_query(connect_db, id_active_order)
    # print(id_active_order[0]['id'])

    phone_id = request.form.get('phone_id')
    phone_color = request.form.get('phone_color')
    # print(phone_id)

    delete_phone = f'''DELETE FROM order_has_phone
    WHERE order_has_phone.order_id={id_active_order[0]['id']} and phone_id={phone_id} and phone_color='{phone_color}' '''
    execute_query(connect_db, delete_phone)
    return redirect(request.referrer)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    id_payment_order = request.form.get('id_payment_order')
    if id_payment_order is not None and session.get('id'):
        change_active_order = f'''delete from appdroid.order where id={id_payment_order} and user_id={session.get('id')}'''
        execute_query(connect_db, change_active_order)

        return render_template("payment.html", user_session=session.get('logged_in'))

    return redirect(url_for('check_user'))


@app.route("/colors", methods=['GET', 'POST'])
def colors():
    print(request.referrer)
    model = request.form.get('phone_model')
    phone_colors = f'''select * from phone, color, phone_has_color where model='{model}' 
        and phone.id=phone_has_color.phone_id 
        and color.title=phone_has_color.color_title'''
    phone_colors = execute_read_query(connect_db, phone_colors)
    print(phone_colors)

    return render_template("colors.html", user_session=session.get('logged_in'),
                           phone_colors=phone_colors)


@app.route('/search/')
def search():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)
