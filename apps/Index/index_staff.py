from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import Staff
from exts import db
from form import EditPasswordForm


@index_bp.route('/staff_index', methods=["POST", "GET"], endpoint='staff_index')
def department_admin_index():
    if request.method == 'GET':
        if "username" in session:
            username = session.get('username')
            staff = Staff.query.filter_by(staffId=username).first()
            image_filename = "static/data/data_headimage_staff/" + username + '/head.jpg'
            form_editPassword = EditPasswordForm()

            edit_password = None
            if session.get('edit_password') is not None:
                edit_password = session.get('edit_password')
                session.pop('edit_password')

            return render_template('index/staff_index.html', staff=staff, url_image=image_filename,
                                edit_password=edit_password,
                                form_password=form_editPassword)
        else:
            return redirect(url_for('login.login'))
    else:
        return "not post now"


@index_bp.route('/edit_password', methods=['POST', 'GET'], endpoint='edit_password')
def edit_password():
    form = EditPasswordForm()
    if request.method == 'POST':

        previous_url = request.referrer
        if previous_url is None:
            previous_url = url_for('login.login')

        if form.validate_on_submit():
            staff = Staff.query.filter(session.get('username') == Staff.staffId).first()
            if staff.staffPassWord == form.staffPassword.data:
                staff.staffPassWord = form.new_staffPassword2.data
                db.session.commit()
                session['edit_password'] = '密码修改成功'
            else:
                session['edit_password'] = '原密码输入错误'
        else:
            session['edit_password'] = '申请提交失败'
        return redirect(previous_url)
