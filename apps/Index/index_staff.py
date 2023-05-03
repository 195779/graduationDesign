from flask import render_template, request, session, redirect, url_for
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import Staff
from form import EditPasswordForm


@index_bp.route('/staff_index', methods=["POST", "GET"], endpoint='staff_index')
def department_admin_index():
    if request.method == 'GET':
        if "username" in session:
            username = session.get('username')
            staff = Staff.query.filter_by(staffId=username).first()
            image_filename = "static/data/data_headimage_staff/" + username + '/head.jpg'
            return render_template('index/staff_index.html', staff=staff, url_image=image_filename)
        else:
            return redirect(url_for('login.login'))
    else:
        return "not post now"


@index_bp.route('/edit_password', methods=['POST'], endpoint='edit_password')
def edit_password():
    return 0
