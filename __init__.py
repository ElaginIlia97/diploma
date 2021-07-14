from flask_login import LoginManager
from db_config import db
from db_config import app
from datetime import timedelta

# Объявление параметров библиотеки flask_login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Загрузка блюпринтов
from auth import auth as auth_blueprint
from main import main as main_blueprint
app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)

# Объявление базы данных
with app.app_context():
    db.create_all()

# Параметры сессии, запуск сервера
if __name__ == "__main__":
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=20)
    app.run(debug=True)

