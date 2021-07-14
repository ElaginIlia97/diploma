from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, RoleNeed, UserNeed

db = SQLAlchemy()
app = Flask(__name__)

# Создание класса Principal библиотеки flask_principal
principals = Principal(app)

# Создание доступа с одной ролью "admin"
admin_permission = Permission(RoleNeed('admin'))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Объявление параметра identity равному текущему пользователю
    identity.user = current_user

    # Добавление атрибуты id в парметр identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # В случае множества ролей у пользователя добавляются все имеющиеся роли
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

# Добавление параметров соединения к базе данных PostgreSQL
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Password@localhost/elagin_i'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация сервера фраймворка Flask
db.init_app(app)

