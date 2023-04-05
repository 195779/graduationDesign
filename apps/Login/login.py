from datetime import datetime

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from sqlalchemy import select

from apps.Login.__init__ import login_bp
from form import LoginForm
from exts import db
from apps.models.check_model import Admin, Staff, departmentAdmin, gateAdmin


@login_bp.route('/', methods=["POST", "GET"], endpoint='login')
def login_index():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post_username = form.username.data
            post_password = form.password.data
            # 系统管理员编号  admin001、admin002.............八位ID
            # 职工编号       195779、195778、195780..........六位ID
            # 闸机编号       gateAdmin001、gateAdmin002......12位ID
            # 部门管理员编号 depAdmin001、depAdmin002.........11为ID

            # 查询
            if len(post_username) == 8:
                # admin
                user = Admin.query.filter_by(adminId=post_username).first()
                user_username = user.adminId
                user_password = user.adminPassWord
                user_loginTime = datetime.now()
                if not user:
                    flash("系统管理员用户 " + post_username + " 不存在")
                    return render_template('login/login.html', form=form)
                if user_password == post_password:
                    session['username'] = post_username
                    session['loginTime'] = user_loginTime
                    try:
                        # 更新登录时间
                        user.loginTime = user_loginTime
                        db.session.commit()
                    except Exception as e:
                        print("\033[0;37;43mThere is an issue adding contact into db. {0}\033[0m".format(e))
                    return redirect(url_for("index.admin_index"))
                else:
                    flash("系统管理员 " + user_username + " 登录：密码输入错误")
                    return render_template('login/login.html', form=form)
            elif len(post_username) == 6:
                # staff
                user = Staff.query.filter_by(staffId=post_username).first()
                user_username = user.staffId
                user_password = user.staffPassWord
                user_loginTime = datetime.now()
                if not user:
                    flash("企业职工用户 " + post_username + " 不存在")
                    return render_template('login/login.html', form=form)
                if user_password == post_password:
                    session['username'] = post_username
                    session['loginTime'] = user_loginTime
                    try:
                        # 更新登录时间
                        user.loginTime = user_loginTime
                        db.session.commit()
                    except Exception as e:
                        print("\033[0;37;43mThere is an issue adding contact into db. {0}\033[0m".format(e))
                    return redirect(url_for("index.staff_index"))
                    #
                else:
                    flash("企业职工 " + user_username + " 登录：密码输入错误")
                    return render_template('login/login.html', form=form)
            elif len(post_username) == 11:
                # departmentAdmin
                user = departmentAdmin.query.filter_by(departmentAdminId=post_username).first()
                user_username = user.departmentAdminId
                user_password = user.departmentAdminPassWord
                user_loginTime = datetime.now()
                if not user:
                    flash("部门管理员用户 " + post_username + " 不存在")
                    return render_template('login/login.html', form=form)
                if user_password == post_password:
                    session['username'] = post_username
                    session['loginTime'] = user_loginTime
                    try:
                        # 更新登录时间
                        user.loginTime = user_loginTime
                        db.session.commit()
                    except Exception as e:
                        print("\033[0;37;43mThere is an issue adding contact into db. {0}\033[0m".format(e))
                    return redirect(url_for("index.department_admin_index"))
                    #
                else:
                    flash("部门管理员用户 " + user_username + " 登录：密码输入错误")
                    return render_template('login/login.html', form=form)
            elif len(post_username) == 12:
                # gate
                user = gateAdmin.query.filter_by(gateAdminId=post_username).first()
                user_username = user.gateAdminId
                user_password = user.gateAdminPassWord
                user_loginTime = datetime.now()
                if not user:
                    flash("闸机用户 " + post_username + " 不存在")
                    return render_template('login/login.html', form=form)
                if user_password == post_password:
                    session['username'] = post_username
                    session['loginTime'] = user_loginTime
                    try:
                        # 更新登录时间
                        user.loginTime = user_loginTime
                        db.session.commit()
                    except Exception as e:
                        print("\033[0;37;43mThere is an issue adding contact into db. {0}\033[0m".format(e))
                    return redirect(url_for("index.gate_admin_index"))
                    #
                else:
                    flash("闸机用户 " + user_username + " 登录：密码输入错误")
                    return render_template('login/login.html', form=form)
                    #
    if request.method == "GET":
        return render_template('login/login.html', form=form)
