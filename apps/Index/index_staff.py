from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint

from apps.Index.__init__ import index_bp
from apps.models.check_model import Staff
from exts import db
from form import EditPasswordForm


# 登录验证装饰器
def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'staff_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('<staff_username>')
@index_bp.route('/<staff_username>/staff_index', methods=["POST", "GET"], endpoint='staff_index')
def staff_index(staff_username):
    if session.get(staff_username+'staff_username') is not None:
        if request.method == 'GET':
            staff = Staff.query.filter_by(staffId=staff_username).first()
            image_filename = "static/data/data_headimage_staff/" + staff_username + '/head.jpg'
            form_editPassword = EditPasswordForm()
            edit_password = None
            if session.get(staff_username + 'edit_password') is not None:
                edit_password = session.get(staff_username + 'edit_password')
                session.pop(staff_username + 'edit_password')

            return render_template('index/staff_index.html', staff=staff, url_image=image_filename,
                            edit_password=edit_password,
                            form_password=form_editPassword)
    else:
        return redirect(url_for('login.login'))


@login_required('<staff_username>')
@index_bp.route('/<staff_username>/edit_password', methods=['POST', 'GET'], endpoint='edit_password')
def edit_password(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
        form = EditPasswordForm()
        if request.method == 'POST':

            previous_url = request.referrer
            if previous_url is None:
                previous_url = url_for('login.login')

            if form.validate_on_submit():
                staff = Staff.query.filter(staff_username == Staff.staffId).first()
                if staff.staffPassWord == form.staffPassword.data:
                    staff.staffPassWord = form.new_staffPassword2.data
                    db.session.commit()
                    session[staff_username + 'edit_password'] = '密码修改成功'
                else:
                    session[staff_username + 'edit_password'] = '原密码输入错误'
            else:
                session[staff_username + 'edit_password'] = '申请提交失败'
            return redirect(previous_url)
    else:
        return redirect(url_for('login.login'))




@login_required('<staff_username>')
@index_bp.route('/<staff_username>/open_box', methods=['POST', 'GET'], endpoint='open_box')
def open_box(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
        staff = Staff.query.filter_by(staffId=staff_username).first()
        image_filename = "static/data/data_headimage_staff/" + staff_username + '/head.jpg'
        form_editPassword = EditPasswordForm()
        edit_password = None
        if session.get(staff_username + 'edit_password') is not None:
            edit_password = session.get(staff_username + 'edit_password')

            session.pop(staff_username + 'edit_password')
        return render_template('staff_all/box.html', staff=staff, url_image=image_filename,
                               edit_password=edit_password,
                               form_password=form_editPassword)
    else:
        return redirect(url_for('login.login'))