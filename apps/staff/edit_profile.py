import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort
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
        username = session['username']
        staff = Staff.query.filter(Staff.staffId == username).first()
        staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()
        staffPositionId = staff_information.staffPositionId
        staffDepartmentId = staff_information.staffDepartmentId
        staffPosition = Position.query.filter_by(positionId=staffPositionId).first()
        staffDepartment = Departments.query.filter(Departments.departmentId == staffDepartmentId).first()
        form.staffAddress.data = staff_information.staffAddress
        filename = "static/data/data_headimage_staff/" + username + '/head.jpg'

        if request.method == 'POST':
            if form.validate_on_submit():
                staffName = form.staffName.data
                staffGender = form.staffGender.data
                # staffImage = form.staffImage.data
                staffHomeTown = form.staffHomeTown.data
                staffBirthday = form.staffBirthday.data
                staffPhoneNumber = form.staffPhoneNumber.data
                staffEmail = form.staffEmail.data
                staffAddress = form.staffAddress.data
                staffCountry = form.staffCountry.data
                staffNation = form.staffNation.data
                staffRemark = form.staffRemark.data
                print("*************************************时间： ", staffBirthday)
                # photos.save(form.staffImage.data, name=filename)
                # url_image = photos.url(form.staffImage.data, name=filename)

                staffImage = request.files.get('staffImage')
                if staffImage:
                    pre_work_mkdir("static/data/data_headimage_staff/" + username)
                    staffImage.save(os.path.join("static/data/data_headimage_staff/" + username +'/head.jpg'))

                # return redirect(url_for('index.staff_index'))

                return render_template('staff_all/edit_profile.html', url_image=filename, staff=staff,
                                    staffPosition=staffPosition, staffDepartment=staffDepartment.departmentName,
                                    staffInformation=staff_information)
            else:
                print("post 失败")
                print(form.errors)
                return redirect(url_for('index.staff_index'))

        if request.method == 'GET':
            print('this is get')
            return render_template('staff_all/edit_profile.html', url_image=filename, form=form, staff=staff, staffPosition=staffPosition,
                                staffDepartment=staffDepartment.departmentName, staffInformation=staff_information)
