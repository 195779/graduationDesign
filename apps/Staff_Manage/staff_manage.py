from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from apps.Staff_Manage.__init__ import staff_bp
from apps.models.check_model import Admin


@staff_bp.route('/<int:id>')
def staff_show(id):
    if "username" in session:
        username = session['username']
        user = Admin.query.filter_by(username=username).first()

        return render_template('staff_all/staff_message_mange.html', user=user)

    return render_template("error/404.html")
