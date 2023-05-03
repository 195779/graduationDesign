from flask import render_template, request, session, redirect, url_for
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import gateAdmin


@index_bp.route('/gate_index', methods=["POST", "GET"], endpoint='gate_admin_index')
def department_admin_index():
    if request.method == 'GET':
        if "username" in session:
            username = session.get('username')
            gate_admin = gateAdmin.query.filter_by(gateAdminId=username).first()
            return render_template('index/gate_index.html', gateAdmin=gate_admin)
        else:
            return redirect(url_for('login.login'))
    else:
        return "not post now"