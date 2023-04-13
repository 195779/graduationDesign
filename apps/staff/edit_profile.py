import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation, Position, Departments, Works
from apps import get_faces_from_camera
from apps import features_extraction
from exts import db


@staff_bp.route('/edit_profile', methods=["GET", "POST"], endpoint='edit_profile')
def edit_profile():
    if 'username' not in session:
        abort(404)
    else:
        username = session['username']
        staff = Staff.query.filter(Staff.staffId == username).first()
        staff_information = staffInformation.query.filter(staffInformation.staffId == username).first()
        staffPositionId = staff_information.staffPositionId
        staffDepartmentId = staff_information.staffDepartmentId
        staffPostion = Position.query.filter_by(positionId=staffPositionId).first()
        staffDepartment = Departments.query.filter(Departments.departmentId == staffDepartmentId).first()
        return render_template('staff_all/edit_profile.html', staff=staff)
