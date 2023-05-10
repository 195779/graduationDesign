from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import Admin, Departments


def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'admin_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('<admin_username>')
@index_bp.route('/<admin_username>/admin_index', methods=["POST", "GET"], endpoint='admin_index')
def admin_index(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        if request.method == 'GET':
            username = admin_username
            admin = Admin.query.filter_by(adminId=username).first()
            return render_template('index/admin_index.html', admin=admin)
        else:
            return redirect(url_for('login.login'))
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@index_bp.route('/<admin_username>/departments', endpoint='departments')
def get_departments(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        departments = Departments.query.all()
        Id_data = []
        Name_data = []
        for department in departments:
            Id_data.append(department.departmentId)
            Name_data.append(department.departmentName)
        Data = dict(zip(Id_data, Name_data))
        return Data
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@index_bp.route('/<admin_username>/departments2', endpoint='departments2')
def get_departments2(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        departments = Departments.query.all()
        Id_data = []
        Name_data = []
        for department in departments:
            Id_data.append(department.departmentId)
            Name_data.append(department.departmentName)
        Data = dict(zip(Id_data, Name_data))
        return Data
    else:
        return redirect(url_for('login.login'))

"""  
执行重定向redirect函数函数后 跳转执行下面的user_index函数，
则打开index页面之后，
一直在重复动作：访问数据库、get请求skin_config.html(而实际上我的templates里并没有这个html)一直这样重复，但是页面还在index页面，
于是index.html页面一直在重复添加index的内容
导致页面越来越长，然后直到内存占用过多页面崩溃
return redirect(url_for('index.usr_index', username=username))
                 |
                 |
                 *
@index_bp.route('/<string:username>', methods=["POST", "GET"], endpoint='user_index')
def user_index(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        return render_template('index/admin_index.html', user=user)
    else:
        return "not post now"
"""
