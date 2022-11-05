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
    check_sql = f'''SELECT id, image, phone.brand, phone.model, phone.price, color_title
            FROM phone, phone_has_color where count>0 and phone_has_color.phone_id = phone.id group by phone.model'''
    phone = execute_read_query(connect_db, check_sql)
    print(phone)

    if 'admin' in session and session.get('logged_in'):
        if session['admin']:
            return render_template('home.html', msg=session['first_name'])
        else:
            return render_template('home2.html', msg=session['first_name'], user_session=session.get('logged_in'), phone=phone)
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
                    return redirect(url_for('check_user'))
            else:
                msg = 'Неверный никнейм или пароль.'
    return render_template('login.html', msg=msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('check_user'))


@app.route("/details/<int:id>", methods=['GET', 'POST'])
def details(id):
    check_sql = f'''select * from phone, color, phone_has_color 
        where phone.count>0 
        and phone.id=phone_has_color.phone_id 
        and color.title=phone_has_color.color_title
        and phone.id={id} group by model '''
    phone = execute_read_query(connect_db, check_sql)
    page_title = execute_read_query(connect_db, check_sql)[0]
    print(phone)
    print(session.get('logged_in'))
    return render_template("details.html", user_session=session.get('logged_in'), phone=phone, page_title=page_title)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    return render_template("cart.html", user_session=session.get('logged_in'))


if __name__ == '__main__':
    app.run(debug=True)
