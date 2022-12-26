from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
import re
import datetime
from passlib.hash import sha256_crypt
from db_CRUT import execute_read_query, execute_query

app = Flask(__name__)

app.secret_key = 'super secret key'
# app.permanent_session_lifetime = datetime.timedelta(seconds=60)
mysql = MySQL(app)


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
# connect_db = create_connection('localhost', 'root', 'admin', 'appdroid')


@app.route('/', methods=['GET', 'POST'])
def check_user():
    check_sql = f'''SELECT id, phone_has_color.image, phone.brand, phone.model, phone.price, color_id
            FROM phone, phone_has_color where phone_has_color.count>0 and phone_has_color.phone_id = phone.id group by phone.model'''
    phone = execute_read_query(connect_db, check_sql)

    panel_phones = f'''select * from phone order by brand'''
    panel_phones = execute_read_query(connect_db, panel_phones)

    # panel_colors = f'''select title from color where id in
    # (select color_id from phone_has_color where phone_id = );'''
    # panel_colors = [execute_read_query(connect_db, panel_colors)]
    # print(panel_colors)

    if 'admin' in session and session.get('logged_in'):
        if session['admin']:
            return render_template('home.html', user_session=session.get('logged_in'),
                                   admin=session['admin'], panel_phones=panel_phones,)
            # panel_colors=panel_colors)

    return render_template('home2.html', user_session=session.get('logged_in'), phone=phone)


# Registration
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        nickname = request.form['nickname']
        password = sha256_crypt.hash(request.form['password'])

        check_sql = f'''select * from user where nickname = "{nickname}"'''
        account = execute_read_query(connect_db, check_sql)

        if account:
            flash('Этот никнейм уже занят.')
        elif len(request.form['nickname']) < 4:
            flash('Никнейм должен содержать не менее 4 символов.')
        elif not re.match(r'[A-Za-z0-9]', nickname):
            flash('Никнейм может содержать только латинские буквы.')
        elif not re.match(r'[А-Яа-я]', first_name or last_name):
            flash('Имя и фамилия могут содержать только кириллицу.')
        elif first_name[0].islower() or last_name[0].islower():
            flash('Имя и фамилия должны начинаться с заглавных букв.')
        elif len(request.form['password']) < 8:
            flash('Пароль должен содержать не менее 8 символов.')
        else:
            write_sql = f'''insert into user (`first_name`,`last_name`,`nickname`,`password`, `admin`) 
            values ('{first_name}', '{last_name}', '{nickname}', '{password}', '{0}')'''
            execute_query(connect_db, write_sql)
            return redirect('login')
    return render_template('registration.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.referrer != request.url_root + 'login') and (request.referrer != request.url_root + 'reg'):
        session['request'] = request.referrer

    if request.method == 'POST' and 'nickname' in request.form and 'password' in request.form:
        nickname = request.form['nickname']
        password = request.form['password']

        check_sql = f'''select * from user where nickname = "{nickname}"'''
        login_user = execute_read_query(connect_db, check_sql)
        if login_user == tuple():
            flash('Неверный никнейм или пароль.')
        else:
            login_user = login_user[0]
            if sha256_crypt.verify(password, login_user['password']):
                session['logged_in'] = True
                session['id'] = login_user['id']
                session['first_name'] = login_user['first_name']
                session['nickname'] = login_user['nickname']
                session['admin'] = login_user['admin']
                if login_user['admin']:
                    return redirect('/')
                else:
                    return redirect('/')
            else:
                flash('Неверный никнейм или пароль.')
                return redirect('login')
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()

    session['request'] = request.referrer
    return redirect(session.get('request'))


@app.route("/details/<int:id>/<int:color_id>", methods=['GET', 'POST'])
def details(id, color_id):
    check_sql = f'''select * from phone, color, phone_has_color 
        where phone_has_color.count>0 
        and phone.id=phone_has_color.phone_id 
        and color.id=phone_has_color.color_id
        and phone.id={id} and phone_has_color.color_id='{color_id}' '''
    phone = execute_read_query(connect_db, check_sql)
    print(phone)
    phone_count = f'''select phone_has_color.count from phone_has_color 
        where phone_has_color.phone_id={id} and phone_has_color.color_id='{color_id}' '''
    phone_count = execute_read_query(connect_db, phone_count)
    phone_count = int(phone_count[0]['count'])
    print(phone_count)

    colors_count = f'''select count(phone_id) as count from phone_has_color where phone_id = '{phone[0]["id"]}' '''
    colors_count = int(execute_read_query(connect_db, colors_count)[0]["count"])

    if phone == tuple():
        return redirect(url_for('check_user'))

    in_cart = None
    if session.get('id'):
        id_active_order = f'''select id from order where user_id = {session['id']} 
                    and active = 1'''
        id_active_order = execute_read_query(connect_db, id_active_order)
        if id_active_order != tuple():

            in_cart = f'''select order.id, order.user_id, order_has_phone.order_id, 
            order_has_phone.phone_id, order_has_phone.phone_color, order_has_phone.count from order, order_has_phone 
            where order_has_phone.order_id={id_active_order[0]['id']} and order.user_id={session['id']} 
            and order_has_phone.phone_id={id} and order_has_phone.phone_color='{color_id}' '''
            in_cart = execute_read_query(connect_db, in_cart)
            if in_cart != tuple():
                in_cart_count = int(in_cart[0]['count'])
            else:
                in_cart_count = 1
            print(in_cart)

            if in_cart != tuple():
                in_cart = in_cart[0]['phone_id']
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
    id_active_order = f'''select id from order where user_id = {session['id']} 
    and active = 1'''
    id_active_order = execute_read_query(connect_db, id_active_order)

    if id_active_order == tuple():  # ЗАКАЗА НЕТ
        # print('НЕТ ЗАКАЗА')

        create_active_order = f'''insert into order (`user_id`, `active`) 
        values ('{session['id']}', 1)'''
        execute_query(connect_db, create_active_order)
        # print('ЗАКАЗ СОЗДАН')

        id_active_order = f'''select id from order where user_id = {session['id']} 
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

            print('ДОБАВЛЕН В КОРЗИНУ')
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
        id_active_order = f'''select id from order where user_id = {session.get('id')} 
            and active = 1'''
        id_active_order = execute_read_query(connect_db, id_active_order)
        if id_active_order != tuple():
            check_sql = f'''SELECT phone.id, OS, year, RAM, memory, phone_has_color.image, phone.brand, 
                        phone.model, phone.price, phone_has_color.color_id, order_has_phone.count
                        FROM phone, phone_has_color, order_has_phone, color 
                        where phone.id=order_has_phone.phone_id 
                        and phone_has_color.phone_id = phone.id 
                        and order_has_phone.phone_color = phone_has_color.color_id and
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
    id_active_order = f'''select id from order where user_id = {session.get('id')} 
                    and active = 1'''
    id_active_order = execute_read_query(connect_db, id_active_order)

    phone_id = request.form.get('phone_id')
    phone_color = request.form.get('phone_color')

    delete_phone = f'''DELETE FROM order_has_phone
    WHERE order_has_phone.order_id={id_active_order[0]['id']} and phone_id={phone_id} and phone_color='{phone_color}' '''
    execute_query(connect_db, delete_phone)
    return redirect(request.referrer)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    id_payment_order = request.form.get('id_payment_order')
    if id_payment_order is not None and session.get('id'):
        change_active_order = f'''delete from order where id={id_payment_order} and user_id={session.get('id')}'''
        execute_query(connect_db, change_active_order)

        return render_template("payment.html", user_session=session.get('logged_in'))

    return redirect(url_for('check_user'))


@app.route("/colors", methods=['GET', 'POST'])
def colors():
    print(request.referrer)
    model = request.form.get('phone_model')
    phone_colors = f'''select * from phone, color, phone_has_color where model='{model}' 
        and phone.id=phone_has_color.phone_id 
        and color.id=phone_has_color.color_id'''
    phone_colors = execute_read_query(connect_db, phone_colors)
    print(phone_colors)

    return render_template("colors.html", user_session=session.get('logged_in'),
                           phone_colors=phone_colors)


@app.route('/search/')
def search():
    return render_template("login.html")


@app.route('/add_phone', methods=['GET', 'POST'])
def add_info():
    brand = request.form.get('brand')
    model = request.form.get('model')
    OS = request.form.get('OS')
    year = request.form.get('year')
    price = request.form.get('price')
    diagonal = request.form.get('diagonal')
    NFC = request.form.get('NFC')
    RAM = request.form.get('RAM')
    memory = request.form.get('memory')
    SIM = request.form.get('SIM')
    cores = request.form.get('cores')
    color = request.form.get('color')
    image = request.form.get('image')
    count = request.form.get('count')

    phone_created = f'''select model from phone where model = "{model}" '''
    phone_created = execute_read_query(connect_db, phone_created)

    if phone_created:
        flash('Этот смартфон уже добавлен.')
        return redirect('/add')
    else:
        add_phone = f'''insert into phone (`brand`,`model`,`OS`,`year`, `price`,
            `diagonal`,`NFC`,`RAM`,`memory`, `SIM`, `cores`) 
            values ('{brand}', '{model}', '{OS}', '{year}', '{price}', '{diagonal}', '{NFC}', 
            '{RAM}','{memory}', '{SIM}', '{cores}') '''
        print(type(year))
        print(type(diagonal))
        phone_id = execute_query(connect_db, add_phone)

        color_created = f'''select id, title from color where title = '{color}' '''
        color_created = execute_read_query(connect_db, color_created)
        if color_created:
            color_id = color_created[0]['id']
        else:
            add_color = f'''insert into color (`title`) values ('{color}') '''
            color_id = execute_query(connect_db, add_color)

        phone_has_color = f'''insert into phone_has_color (`phone_id`,`color_id`,`count`,`image`)
                            values ('{phone_id}', '{color_id}', '{int(count)}', '{image}') '''
        execute_query(connect_db, phone_has_color)
        flash("Смартфон успешно добален.")
        return redirect('/add')


@app.route('/add', methods=['GET', 'POST'])
def product_list():

    return render_template("add_phone.html", user_session=session.get('logged_in'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    phone_info = f'''select * from phone where id = {id}'''
    phone_info = execute_read_query(connect_db, phone_info)

    return render_template("edit_phone.html", user_session=session.get('logged_in'), phone_info=phone_info)


@app.route('/edit_phone', methods=['GET', 'POST'])
def edit_phone():
    phone_id = request.form.get('phone_id')
    brand = request.form.get('brand')
    model = request.form.get('model')
    OS = request.form.get('OS')
    year = request.form.get('year')
    price = request.form.get('price')
    diagonal = request.form.get('diagonal')
    NFC = request.form.get('NFC')
    RAM = request.form.get('RAM')
    memory = request.form.get('memory')
    SIM = request.form.get('SIM')
    cores = request.form.get('cores')

    update_info = f'''UPDATE `phone` SET `brand` = '{brand}', `model` = '{model}', `OS` = '{OS}',
        `year` = '{year}', `price` = '{price}', `diagonal` = '{diagonal}', `NFC` = '{NFC}', `RAM` = '{RAM}',
        `memory` = '{memory}', `SIM` = '{SIM}', `cores` = '{cores}' WHERE id = '{phone_id}' '''
    execute_query(connect_db, update_info)

    flash("Изменения сохранены.")
    return redirect(request.referrer)


@app.route('/edit_color/<int:id>', methods=['GET', 'POST'])
def phone_colors(id):
    color_info = f'''select * from color where id in
                        (select color_id from phone_has_color where phone_id = {id}) order by title'''
    color_info = execute_read_query(connect_db, color_info)

    if request.method == 'POST' and request.form.get('image'):
        color = request.form.get('color')
        image = request.form.get('image')
        count = request.form.get('count')

        color_created = f'''select id, title from color where title = '{color}' '''
        color_created = execute_read_query(connect_db, color_created)
        if color_created:
            color_id = color_created[0]['id']
        else:
            add_color = f'''insert into color (`title`) values ('{color}') '''
            color_id = execute_query(connect_db, add_color)

        add_color = f'''INSERT INTO `phone_has_color` (`phone_id`, `color_id`, `count`, `image`) 
                VALUES ('{id}', '{color_id}', '{count}', '{image}'); '''
        execute_query(connect_db, add_color)
        flash("Цвет добавлен.")
        return redirect(request.referrer)

    if request.method == 'POST' and request.form.get('delete_color'):
        color_id = request.form.get('delete_color')

        delete_color = f'''DELETE FROM `phone_has_color` 
                WHERE (`phone_id` = '{id}') and (`color_id` = '{color_id}');'''
        execute_query(connect_db, delete_color)
        flash("Цвет удален.")
        return redirect(request.referrer)

    return render_template("add_color.html", user_session=session.get('logged_in'), color_info=color_info)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_phone(id):
    phone = f'''select brand, model from `phone` WHERE (`id` = '{id}')'''
    phone = execute_read_query(connect_db, phone)
    phone = f"{phone[0]['brand']} " \
            f"{phone[0]['model']}"

    deleting_phone = f'''DELETE FROM `phone` WHERE (`id` = '{id}')'''
    execute_query(connect_db, deleting_phone)
    flash(f"{phone} удален.")
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
