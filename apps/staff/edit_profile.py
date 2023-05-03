import base64
from datetime import datetime
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort, jsonify
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation, Position, Departments, Works
from form import StaffForm


def pre_work_mkdir(path_photos_from_camera):
    # 新建文件夹
    if os.path.isdir(path_photos_from_camera):
        pass
    else:
        print(path_photos_from_camera)
        os.mkdir(path_photos_from_camera)


@staff_bp.route('/edit_profile', methods=["GET", "POST"], endpoint='edit_profile')
def edit_profile():
    if 'username' not in session:
        abort(404)
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

                # 更新保存头像
                staffImage = request.files.get('staffImage')
                if staffImage:
                    pre_work_mkdir("static/data/data_headimage_staff/" + username)
                    staffImage.save(os.path.join("static/data/data_headimage_staff/" + username + '/head.jpg'))

                print('post 成功')
                post = 1
                symbol = 1
            else:
                post = 1
                symbol = 0
                print("post 失败")
                print(form.errors)

            filename = "static/data/data_headimage_staff/" + username + '/head.jpg'
            return render_template('staff_all/edit_profile.html', url_image=filename, form=form, staff=staff,
                                staffPosition=staffPosition, post=post, symbol=symbol,
                                staffDepartment=staffDepartment.departmentName, staffInformation=staff_information)

        if request.method == 'GET':
            return render_template('staff_all/edit_profile.html', url_image=filename, form=form, staff=staff,
                                staffPosition=staffPosition,staffDepartment=staffDepartment.departmentName,
                                staffInformation=staff_information)
