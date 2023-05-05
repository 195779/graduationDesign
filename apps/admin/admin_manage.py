from flask import render_template, request, session, redirect, url_for, abort, jsonify
from flask import Blueprint
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff


@admin_bp.route("/<departmentId>", methods=['POST', "GET"])
def staff_manage(departmentId):
    if session.get('username') is None or departmentId is None:
        abort(404)
    else:
        if len(departmentId) == 3:
            adminId = session.get('username')
            admin = Admin.query.filter(adminId == Admin.adminId).first()
            department = Departments.query.filter(departmentId == Departments.departmentId).first()

            staffId_list = []
            staff_list = []
            staff_position_list = []
            staff_information_list = staffInformation.query.filter(
                staffInformation.staffDepartmentId == departmentId).all()
            for staff_information in staff_information_list:
                staffId_list.append(staff_information.staffId)

                staff = Staff.query.filter(Staff.staffId == staff_information.staffId)
                staff_list.append(staff)

                staff_position = Position.query.filter(staff_information.staffPositionId == Position.positionId).first()
                staff_position_list.append(staff_position)



            return render_template('admin_all/department_message_manage.html', Dep=department, admin=admin,
                                staff_list=staff_list, staff_information_list=staff_information_list,
                                staff_position_list=staff_position_list)
        else:
            return 'what happened?'


@admin_bp.route('/setState', methods=['POST'], endpoint='setState')
def setState():
    selected_persons = request.json
    #
    result = {"status": "success", "message": "Selected persons updated successfully."}
    return jsonify(result), 200
