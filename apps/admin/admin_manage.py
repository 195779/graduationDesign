from flask import render_template, request, session, redirect, url_for, abort
from flask import Blueprint
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff


@admin_bp.route("/<departmentId>", methods=['POST', "GET"])
def staff_manage(departmentId):
    if session.get('username') is None or departmentId is None:
        abort(404)
    else:
        if len(departmentId) == 3:
            adminId = session.get('username')
            admin = Admin.query.filter(adminId == Admin.adminId).first()
            department = Departments.query.filter(departmentId == Departments.departmentId).first()
            print("ddddddddddddddddddddddddddddddd" + departmentId)
            return render_template('admin_all/department_message_manage.html', Dep=department, admin=admin)
        else:
            return 'what happened?'

