import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation, Position, Departments, Works
from apps import get_faces_from_camera
from apps import features_extraction
from exts import db


@staff_bp.route('/staff_profile', methods=["GET", "POST"], endpoint="staff_profile")
def staff_profile():
    username = session['username']
    if username:
        staff = Staff.query.filter(Staff.staffId == username).first()
        staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()
        staffPositionId = staff_information.staffPositionId
        staffDepartmentId = staff_information.staffDepartmentId
        staffPostion = Position.query.filter(Position.positionId == staffPositionId).first()
        staffDepartment = Departments.query.filter(Departments.departmentId == staffDepartmentId).first()
        return render_template('staff_all/staff_profile.html',
                               staff=staff, staff_information=staff_information, Postion=staffPostion, Department=staffDepartment)
    else:
        return render_template('login/login.html')