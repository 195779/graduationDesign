from flask import render_template, request, session, redirect, url_for
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import gateAdmin


def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'gateAdmin_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('gateAdmin_username')
@index_bp.route('/<gateAdmin_username>/gate_index', methods=["POST", "GET"], endpoint='gate_admin_index')
def department_admin_index(gateAdmin_username):
    if session.get(gateAdmin_username+'gateAdmin_username') is not None:
        if request.method == 'GET':
            username = gateAdmin_username
            gate_admin = gateAdmin.query.filter_by(gateAdminId=username).first()
            return render_template('index/gate_index.html', gateAdmin=gate_admin)
        else:
            return "not post now"
    else:
        return redirect(url_for('login.login'))
