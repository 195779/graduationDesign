import base64
from datetime import datetime
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort, jsonify, \
    json
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation, Position, Departments, Works
from exts import db
from form import StaffForm, EditPasswordForm


def pre_work_mkdir(path_photos_from_camera):
    # 新建文件夹
    if os.path.isdir(path_photos_from_camera):
        pass
    else:
        print(path_photos_from_camera)
        os.mkdir(path_photos_from_camera)


@staff_bp.route('/submit_profile', methods=["POST"], endpoint='submit_profile')
def submit_profile():
    if 'username' not in session:
        abort(404)
    else:
        form = StaffForm()
        username = session.get('username')
        staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()

        if request.method == 'POST':
            if form.validate_on_submit():
                staffName = form.staffName.data
                staffGender = form.staffGender.data
                staffHomeTown = form.staffHomeTown.data
                staffBirthday = form.staffBirthday.data
                staffPhoneNumber = form.staffPhoneNumber.data
                staffEmail = form.staffEmail.data
                staffAddress = form.staffAddress.data
                staffCountry = form.staffCountry.data
                staffNation = form.staffNation.data
                staffRemark = form.staffRemark.data

                # 拿到的时间为 07/12/2001 的格式；更新出生日期
                print("*************************************时间： ", staffBirthday)
                date_obj = datetime.strptime(staffBirthday, '%d/%m/%Y').date()
                print('*********************************转换后的时间：', date_obj)
                staff_information.staffBirthday = date_obj

                # 更新姓名
                staff_information.staffName = staffName
                # 更新性别
                staff_information.staffGender = staffGender
                # 更新籍贯
                staff_information.staffOrigin = staffHomeTown
                # 更新联系方式
                staff_information.staffPhoneNumber = staffPhoneNumber
                # 更新电子邮件地址
                staff_information.staffEmailAddress = staffEmail
                # 更新现住址
                staff_information.staffAddress = staffAddress
                # 更新国籍
                staff_information.staffCountry = staffCountry
                # 更新民族
                staff_information.staffNation = staffNation
                # 更新备注
                staff_information.staff_Remark = staffRemark

                db.session.commit()

                # 更新保存头像
                staffImage = request.files.get('staffImage')
                if staffImage:
                    pre_work_mkdir("static/data/data_headimage_staff/" + username)
                    staffImage.save(os.path.join("static/data/data_headimage_staff/" + username + '/head.jpg'))

                print('post 成功')
                session['post'] = '1'
                session['symbol'] = '1'
            else:
                session['post'] = '1'
                session['symbol'] = '0'
                print("post 失败")
                print(form.errors)

                # 将form对象转换为JSON字符串
                form_data = json.dumps(form.data)
                form_errors = json.dumps(form.errors)
                # 将转换后的数据存储到session中
                session['form_data'] = form_data
                session['form_errors'] = form_errors

            return redirect(url_for('staff_all.edit_profile'))


@staff_bp.route('/edit_profile', methods=["GET"], endpoint='edit_profile')
def edit_profile():
    if 'username' not in session:
        abort(404)
    else:
        if request.method == 'GET':
            form_editPassword = EditPasswordForm()

            # 从session中获取存储的form数据
            form_data = session.get('form_data')
            form_errors = session.get('form_errors')
            # 将JSON字符串转换为form对象
            if form_data is not None:
                form = StaffForm(data=json.loads(form_data))
                form.form_errors = json.loads(form_errors)
                # 清除session中的数据
                session.pop('form_data', None)
                session.pop('form_errors', None)
            else:
                form = StaffForm()

            username = session.get('username')
            staff = Staff.query.filter(Staff.staffId == username).first()
            staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()

            staffPositionId = staff_information.staffPositionId
            staffDepartmentId = staff_information.staffDepartmentId

            staffPosition = Position.query.filter_by(positionId=staffPositionId).first()
            staffDepartment = Departments.query.filter(Departments.departmentId == staffDepartmentId).first()

            filename = "static/data/data_headimage_staff/" + username + '/head.jpg'

            post = '0'
            symbol = '0'
            if session.get('post') and session['symbol']:
                post = session['post']
                symbol = session['symbol']
                session.pop('post')
                session.pop('symbol')

            return render_template('staff_all/edit_profile.html', url_image=filename, form=form, staff=staff,
                                   form_password=form_editPassword, post=post, symbol=symbol,
                                   staffPosition=staffPosition, staffDepartment=staffDepartment.departmentName,
                                   staffInformation=staff_information)
