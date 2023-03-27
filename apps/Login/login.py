from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from apps.Login.__init__ import login_bp
from form import LoginForm
from exts import db
from apps.models.user_model import User


@login_bp.route('/', methods=["POST", "GET"], endpoint='login')
def login_index():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # 查询
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("不存在该用户")
            return render_template('login/login.html', form=form)
        if user.password == password:
            # return redirect(url_for("index.user_index", username=username))
            session['username'] = username
            return redirect(url_for("index.user_index"))
        else:
            flash("密码输入错误")
            return render_template('login/login.html', form=form)
    if request.method == "GET":
        return render_template('login/login.html', form=form)

