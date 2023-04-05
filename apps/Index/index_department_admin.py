from flask import render_template, request, session, redirect, url_for
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import departmentAdmin


@index_bp.route('/departmentAdmin_index', methods=["POST", "GET"], endpoint='department_admin_index')
def department_admin_index():
    if request.method == 'GET':
        if "username" in session:
            username = session['username']
            depAdmin = departmentAdmin.query.filter_by(departmentAdminId=username).first()
            return render_template('index/departmentAdmin_index.html', departmentAdmin=depAdmin)
        else:
            return redirect(url_for('login.login'))
    else:
        return "not post now"
