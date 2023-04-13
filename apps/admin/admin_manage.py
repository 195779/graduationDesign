from flask import render_template, request, session, redirect, url_for, abort
from flask import Blueprint
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff


@admin_bp.route("/staff_manage", methods=['POST', "GET"], endpoint='staff_manage')
def staff_manage():
    if session['username'] is None:
        abort(404)
    else:
        adminId = session['username']
        admin = Admin.query.filter(Admin.adminId == adminId).first()
        staffList = Staff.query.all()
        staffInformationList = staffInformation.query.all()
        return 0