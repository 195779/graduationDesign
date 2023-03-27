from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from apps.Staff_Manage.__init__ import staff_bp
from apps.models.user_model import User


@staff_bp.route('/<int:id>')
def staff_show(id):
    if "username" in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if id == 1:
            return render_template('staff_manage/staff_manage.html', user=user)
        if id == 2:
            return render_template('staff_manage/staff_manage.html', user=user)
        if id == 3:
            return render_template('staff_manage/staff_manage.html', user=user)
        if id == 4:
            return render_template('staff_manage/staff_manage.html', user=user)
    return render_template("error/404.html")
