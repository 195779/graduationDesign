from flask import render_template, request, session, redirect, url_for
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import departmentAdmin, Departments, Staff, staffInformation


def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'depAdmin_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('<depAdmin_username')
@index_bp.route('/<depAdmin_username>/departmentAdmin_index', methods=["POST", "GET"], endpoint='department_admin_index')
def department_admin_index(depAdmin_username):
    if session.get(depAdmin_username+'depAdmin_username') is not None:
        if request.method == 'GET':
            username = depAdmin_username
            depAdmin = departmentAdmin.query.filter_by(departmentAdminId=username).first()
            department = Departments.query.filter(depAdmin.admin_departmentId == Departments.departmentId).first()
            staff_information_list = staffInformation.query.filter(department.departmentId == staffInformation.staffDepartmentId).all()
            return render_template('index/departmentAdmin_index.html', departmentAdmin=depAdmin, dep=department)
        else:
            return "not post now"
    else:
        return redirect(url_for('login.login'))
