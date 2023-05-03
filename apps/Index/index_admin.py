from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import Admin, Departments


@index_bp.route('/admin_index', methods=["POST", "GET"], endpoint='admin_index')
def admin_index():
    if request.method == 'GET':
        if 'username' in session:
            username = session.get('username')
            admin = Admin.query.filter_by(adminId=username).first()
            return render_template('index/admin_index.html', admin=admin)
        else:
            return redirect(url_for('login.login'))
    else:
        return "not post now"


@index_bp.route('/departments', endpoint='departments')
def get_departments():
    departments = Departments.query.all()
    Id_data = []
    Name_data = []
    for department in departments:
        Id_data.append(department.departmentId)
        Name_data.append(department.departmentName)
    Data = dict(zip(Id_data, Name_data))
    return Data


@index_bp.route('/departments2', endpoint='departments2')
def get_departments2():
    departments = Departments.query.all()
    Id_data = []
    Name_data = []
    for department in departments:
        Id_data.append(department.departmentId)
        Name_data.append(department.departmentName)
    Data = dict(zip(Id_data, Name_data))
    return Data


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