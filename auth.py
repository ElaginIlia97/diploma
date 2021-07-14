from flask import flash, Blueprint, redirect, url_for, render_template, request, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  login_required, current_user, login_user, logout_user
from models.user import User,  Role
from db_config import db, admin_permission
from flask_wtf import FlaskForm
from wtforms.fields.core import SelectMultipleField
import pytz
from flask_principal import Identity, AnonymousIdentity, \
     identity_changed

# Объявления данной страницы в виде блюпринта
auth = Blueprint('auth', __name__)

# Создание формы с ролями пользователя страницы администратора
class UserForm(FlaskForm):
    roles = SelectMultipleField('role', [], render_kw={'class': 'selectpicker w-75', 
                                                        'title': 'Роли не указаны'})

# Базовая страница при включении сервера
@auth.route("/")
def home():
    return redirect(url_for('auth.signup'))

# Страница регистрации при использовании метода запроса GET
@auth.route("/signup")
def signup():
    return render_template('signup.html')

# Страница регистрации при использовании метода запроса POST
@auth.route("/signup", methods=['POST'])
def signup_post():
    # Загрузка данных из формы
    name = request.form['username']
    email = request.form['email']
    type = request.form['user_type']
    password = request.form['password']
 
    # Проверка наличия пользователя
    user = User.query.filter_by(email=email).first()

    if user :
        flash('User already existed in database')
        return redirect(url_for('auth.signup'))

    new_user = User(name, email, type, generate_password_hash(password, method="sha256"))

    # Добавления пользователя в Базу Данных
    new_user.roles.append(Role.query.filter_by(name='user').first())
    db.session.add(new_user)
    db.session.commit()

    # Переход на страницу входа
    return redirect(url_for('auth.login'))

# Страница входа
@auth.route("/login", methods=["GET", "POST"])
def login():

    # Проверка метода запроса POST
    if request.method == "POST":

        # Объвление сессии для пользователя
        session.permanent = True

        # Получение данных из формы
        name = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=name).first()

        # Проверка данных пользователя
        if not user or not check_password_hash(user.password, password):
            flash('Wrong Username or Password')
            return redirect(url_for('auth.login'))

        # Авторизация пользователя для библиотеки flask-login
        login_user(user)

        # Авторизация пользователя для библиотеки flask-admin
        identity_changed.send(current_app._get_current_object(),
                                    identity=Identity(user.id))
        return redirect(url_for('main.main_page'))
    else:
        return render_template('login.html', Title = 'Login')

# Страница выхода
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return redirect(url_for('auth.login'))

# Страница администратора
@auth.route('/admin')
def admin():

    admin = False

    # Проверка соответствующей роли
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    try:
        with admin_permission.require(http_exception=401):
            admin = True
    except:
        return redirect(url_for('main.main_page'))
    if admin:
        # Выгрузка всех имеющихся пользователей кроме того, кто загружает страницу
        users = [user for user in User.query.filter(User.id != current_user.id).all()]

        local_timezone = pytz.timezone('Etc/GMT-14')

        # Формирование данных таблицы пользователей
        user_forms = []
        for user in User.query.filter(User.id != current_user.id).all():
            user_form = UserForm()
            user_form.roles.choices = [(role.id, role.name) for role in Role.query.all()]
            user_form.roles.default = [(role.id) for role in User.query.filter_by(id = user.id).first().roles]
            user_form.process()
            user_forms.append(user_form)

        return render_template('admin.html', users = users, user_forms = user_forms, local_timezone = local_timezone)


        
        