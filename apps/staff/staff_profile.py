import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort

from apps.Index.index_staff import login_required
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation, Position, Departments, Works
from apps import get_faces_from_camera
from apps import features_extraction
from exts import db
from form import EditPasswordForm


@login_required('<staff_username>')
@staff_bp.route('/<staff_username>/staff_profile', methods=["GET", "POST"], endpoint="staff_profile")
def staff_profile(staff_username):
    if session.get(staff_username+'staff_username') is not None:
        username = staff_username
        form_editPassword = EditPasswordForm()
        if username:
            image_filename = "static/data/data_headimage_staff/" + username + '/head.jpg'
            staff = Staff.query.filter(Staff.staffId == username).first()
            staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()
            staffPositionId = staff_information.staffPositionId
            staffDepartmentId = staff_information.staffDepartmentId
            staffPostion = Position.query.filter_by(positionId=staffPositionId).first()
            staffDepartment = Departments.query.filter(Departments.departmentId == staffDepartmentId).first()
            return render_template('staff_all/staff_profile.html',
                                staff=staff, staff_information=staff_information, Postion=staffPostion,
                                form_password=form_editPassword,
                                url_image=image_filename, Department=staffDepartment)
        else:
            return render_template('login/login.html')
    else:
        return  redirect(url_for('login.login'))