import re
from flask.helpers import make_response
from sqlalchemy.sql.elements import Null
from db_config import db, admin_permission, app
from flask import Flask, Blueprint, redirect, render_template, request, url_for, jsonify
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from wtforms.fields.core import SelectMultipleField
from models.user import User, Role
from models.directory import MethodType, MlTask, Method, DataCharact, MlTool, DataMethod
from flask_wtf import FlaskForm
from wtforms import SelectField
import pytz

from datetime import datetime, timezone

main = Blueprint('main', __name__)

# Временная зона
local_timezone = pytz.timezone('Etc/GMT-14')

# Форма для странички администратора
def admin_user_form():
    user_forms = []
    for user in User.query.filter(User.id != current_user.id).all():

        user_form = AdminUserForm()
        user_form.roles.choices = [(role.id, role.name) for role in Role.query.all()]
        user_form.roles.default = [(role.id) for role in User.query.filter_by(id = user.id).first().roles]
        user_form.process()
        user_forms.append(user_form)
    return user_forms

def admin_users():
    return [user for user in User.query.filter(User.id != current_user.id).all()]

# Форма указания списка пользователей
class UserForm(FlaskForm):
    have_users = SelectField('have_user', choices=[('1', 'Доступ только для меня'), ('2', 'Группа пользователей')], render_kw={'class': 'selectpicker', 'title': '...'})
    users = SelectMultipleField('user', [], render_kw={'class': 'selectpicker w-75', 'data-live-search': 'true', 'title': 'Никто не выбран'})

# Форма предварительная (До внесения данных в систему)
class TaskForm(FlaskForm):
    task_type = SelectField('task_type', [], render_kw={'class': 'selectpicker', 'title': '...'})
    classific_classes = SelectField('classif_class', choices=[('1', '2 класса'), ('2', 'Больше 2 классов')], render_kw={'title': '...', 'class': 'selectpicker w-75 classification_task'})
    regres_fields = SelectField('regres_fields', choices=[('1', 'до 5 полей'), ('2', 'от 5 до 10 полей'), ('3', 'более 10 полей')], render_kw={'title': '...', 'class': 'selectpicker w-75 regression_task'})

# Для страницы Администратора
class AdminUserForm(FlaskForm):
    roles = SelectMultipleField('role', [], render_kw={'class': 'selectpicker w-75', 'title': 'Роли не указаны'})

# Для указания характеристик данных
class DataCharactForm(FlaskForm):
    outliers = SelectField('outlier', [], render_kw={'class': 'selectpicker', 'title': '...'})
    data_rows = SelectField('data_row', [], render_kw={'class': 'selectpicker', 'title': '...'})
    data_features = SelectField('data_feature', [], render_kw={'class': 'selectpicker', 'title': '...'})
    class_imbalance = SelectField('class_imbalance', [], render_kw={'class': 'selectpicker', 'title': '...'})
    categorical_data = SelectField('categorical_data', [], render_kw={'class': 'selectpicker', 'title': '...'})
    blank_data = SelectField('blank_data', [], render_kw={'class': 'selectpicker', 'title': '...'})


@main.route('/main', methods=["POST", "GET"])
def main_page():

    # Только зарегистрированные пользователи могут пользоваться страничкой
    if not current_user.is_authenticated:
        # В случае если пользователь не зарегистрирован, то его переадресуют на страничку входа 
        return redirect(url_for('auth.login'))
    else:
        classific_choises = ['2 класса', 'Больше 2 классов']

        # Нижний код будет запускаться если Постятся данные
        if request.method == "POST":
            have_users = int(request.form['have_users'])
            users = request.form.getlist('users')
            task_description = request.form['task_description']
            task_type = int(request.form['task_type'])
            outliers = DataCharact.query.filter_by(id = int(request.form['outliers'])).first().name
            data_rows = DataCharact.query.filter_by(id = int(request.form['data_rows'])).first().name
            data_features = DataCharact.query.filter_by(id = int(request.form['data_features'])).first().name
            categorical_data = DataCharact.query.filter_by(id = int(request.form['categorical_data'])).first().name
            blank_data = DataCharact.query.filter_by(id = int(request.form['blank_data'])).first().name
            recommend_method = request.form['recommend_method']
            recommend_tool = request.form['recommend_tool']
            link = request.form['link']
            new_task = None

            if task_type == 1:
                new_task = MlTask(description=task_description, ml_type=task_type, outliers = outliers, data_rows=data_rows, data_features=data_features,
                                    class_imbalance=Null, categorical_data=categorical_data, blank_data=blank_data, recommend_method=recommend_method,
                                    recomment_tool=recommend_tool, link=link)
            elif task_type == 2:
                class_imbalance = DataCharact.query.filter_by(id = int(request.form['class_imbalance'])).first().name
                new_task = MlTask(description=task_description, ml_type=task_type, outliers = outliers, data_rows=data_rows, data_features=data_features,
                                    class_imbalance=class_imbalance, categorical_data=categorical_data, blank_data=blank_data, recommend_method=recommend_method,
                                    recomment_tool=recommend_tool, link=link)
            else:
                return f'Ошибка <h1>{task_type}</h1>'

            if have_users == 2:
                new_task.users.extend([User.query.filter_by(id=user).first() for user in users])
                new_task.users.append(current_user)
            else:
                new_task.users.append(current_user)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('main.main_page'))   
        # В случае если метод "GET"
        else:
            # Заполнение форм, про данные
            data_charact_form = DataCharactForm()
            data_charact_form.outliers.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 1).all()]
            data_charact_form.data_rows.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 2).all()]
            data_charact_form.data_features.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 3).all()]
            data_charact_form.class_imbalance.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 4).all()]
            data_charact_form.categorical_data.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 5).all()]
            data_charact_form.blank_data.choices = [(charact.id, charact.name) for charact in DataCharact.query.filter_by(form_class = 6).all()]

            user_form = UserForm()
            # Добавляю пользователей в Опции исключая текущего пользователя (нельзя добавить самого себя)
            user_form.users.choices = [(user.id, user.name) for user in User.query.filter(User.id != current_user.id).all()]

            task_form = TaskForm()
            task_form.task_type.choices = [(task_type.id, task_type.name) for task_type in MethodType.query.all()]

            return render_template('main.html', user_form=user_form, task_form=task_form, data_charact_form=data_charact_form)


# Запрос на вывод рекомендации
@main.route('/task_data', methods=['POST'])
def task_json():

    # Список советов для предобработки
    advice_list = ['Для наилучшего результата необходимо избавиться от выбросов','Необходимо избавиться от категориальных данных', 'Пустые значения необходимо удалить', 'Пустые значения необходимо заменить медианой']
    
    res = None
    method_dict = {}

    # Получение json документа
    req = request.get_json()

    key_to_avoid = []

    # Получение списка методов с соответчтвующим типом задачи
    methods = Method.query.filter_by(task_type_id = int(req['task_type'])).order_by(Method.id.desc()).all()

    # Перебор через каждый имеющийся метод
    for method in methods:
        points = 0
        key_to_avoid = []

        # В случае регрессии 
        if int(req['task_type']) == 1:
            key_to_avoid.append('task_type')
            key_to_avoid.append('class_imbalance')
        else:
            key_to_avoid.append('task_type')

        # Перебор приходящего Json документа
        for key, value in req.items():
            if bool(req[key]):

                if key not in key_to_avoid:
                    if bool(DataMethod.query.filter_by(data_charact_id = int(value), method_id = method.id).first()):
                        points += DataMethod.query.filter_by(data_charact_id = int(value), method_id = method.id).first().points
                    else:
                        points += 5

        # Добавление значений в словарь
        method_dict[f'{method.id}'] = points

    advice_req = []

    # Логика добавления подсказок
    if int(req['outliers']) == 1:
        advice_req.append(advice_list[0])
    if int(req['categorical_data']) == 5:
        advice_req.append(advice_list[1])
    if int(req['blank_data']) == 13:
        advice_req.append(advice_list[2])
    if int(req['blank_data']) == 14:
        advice_req.append(advice_list[3])   

    # Выбор метода с максимальным значением       
    max_key = max(method_dict, key=method_dict.get)

    best_method = Method.query.filter_by(id = max_key).first()

    implement = MlTool.query.filter_by(method_id = max_key, level_type_id = current_user.type).first()

    advice = ''

    # Формирование списка рекомендаций
    if len(advice_req) != 0 :
        advice = 'Предобработка: <br>'

        for one in advice_req:
            advice += f'{one} <br>'

    res = make_response(jsonify({
                                'advices': f'{advice}',
                                'best_method': f'На основании введенных данных, для решения поставленной задачи необходимо использовать {str(best_method.name)}',
                                'ml_tool': f'Подходящим инструментом будет {str(implement.name)}',
                                'tool_link': f'{implement.link}'}), 200)
    return res


@main.route('/history')
def history():
    # Только зарегистрированные пользователи могут пользоваться страничкой
    if not current_user.is_authenticated:
        # В случае если пользователь не зарегистрирован, то его переадресуют на страничку входа 
        return redirect(url_for('auth.login'))
    else:
        task = MlTask.query.join(User.tasks).filter(User.id == current_user.id).all()
        #return f'{task[0].id}'
       

        tasks = [(task, MethodType.query.filter_by(id = task.ml_type).first().name) for task in MlTask.query.join(User.tasks).filter(User.id == current_user.id).all()]
        return render_template('history.html', tasks=tasks, local_timezone = local_timezone)

@main.route('/admin/delete/<user_id>', methods=["DELETE"])
def delete_user(user_id):

    user = User.query.filter_by(id = user_id).first()

    # Удаление пользователя
    db.session.delete(user)
    db.session.commit()

    return render_template('admin_user_change.html', users = admin_users(), 
                                            user_forms = admin_user_form(), 
                                            local_timezone = local_timezone)

@main.route('/admin/user_edit', methods=['POST'])
def user_role_edit():
    req = request.get_json()

    user = User.query.filter_by(id = req['user_id']).first()

    user_roles = [role.id for role in user.roles]

    user_add_role = [role for role in req['user_roles'] if role not in user_roles]

    user_delete_role = [role for role in user_roles if role not in req['user_roles']]

    if 2 in user_delete_role:
        user_delete_role.remove(2)

    for role_id in user_add_role:
        user.roles.append(Role.query.filter_by(id=role_id).first())

    for role_id in user_delete_role:
        user.roles.remove(Role.query.filter_by(id=role_id).first())
    db.session.commit()

    return render_template('admin_user_change.html', users = admin_users(), user_forms = admin_user_form(), local_timezone = local_timezone)

@main.route('/testing')
def testing():
    user = User.query.filter(User.id != current_user.id).first()

    local_timezone = pytz.timezone('Etc/GMT-14')

    return(f'{admin_permission.require(http_exception=401)}')

    #New comment

    return (f'{user.create_datetime.astimezone(local_timezone).strftime("%Y-%m-%d %H:%M:%S")}, {user.create_datetime}')
