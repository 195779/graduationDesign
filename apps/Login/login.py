from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from sqlalchemy import select

from apps.Login.__init__ import login_bp
from form import LoginForm
from exts import db
from apps.models.check_model import Admin


@login_bp.route('/', methods=["POST", "GET"], endpoint='login')
def login_index():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            # 查询
            admin = Admin.query.filter_by(adminId=username).first()

            query = db.select(Admin).where(Admin.adminId == username)
            admin_test = db.session.execute(query).scalars()
            print('管理员', admin_test.first().adminPassWord)
            print(str(type(admin_test)))

            if not admin:
                flash("不存在该用户")
                return render_template('login/login.html', form=form)
            if admin.adminPassWord == password:
                session['username'] = username
                return redirect(url_for("index.user_index"))
        else:
            flash("密码输入错误")
            return render_template('login/login.html', form=form)
    if request.method == "GET":
        return render_template('login/login.html', form=form)
