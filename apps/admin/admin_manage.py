from flask import render_template, request, session, redirect, url_for, abort, jsonify
from flask import Blueprint
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff
from exts import db


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


@admin_bp.route('/openFaceState', methods=['POST'], endpoint='openFaceState')
def openFaceState():
    selected_persons = request.json
    if len(selected_persons) == 0:
        result = {"status": "error", "message": "未选中职工"}
    else:
        for person in selected_persons:
            print(str(type(person)), "dddddddddddddddddddddddddddddddddddddddddddddd")
            staff_information = staffInformation.query.filter(person == staffInformation.staffId).first()
            staff_information.staffGetFaceState = True
        db.session.commit()
        result = {"status": "success", "message": "已选中的职工人脸录入权限已打开"}

    return jsonify(result), 200


@admin_bp.route('/closeFaceState', methods=['POST'], endpoint='closeFaceState')
def closeFaceState():
    selected_persons = request.json
    if len(selected_persons) == 0:
        result = {"status": "error", "message": "未选中职工"}
    else:
        for person in selected_persons:
            print(str(type(person)), "dddddddddddddddddddddddddddddddddddddddddddddd")
            staff_information = staffInformation.query.filter(person == staffInformation.staffId).first()
            staff_information.staffGetFaceState = False
        db.session.commit()
        result = {"status": "success", "message": "已选中的职工人脸录入权限已关闭"}

    return jsonify(result), 200


@admin_bp.route('/setAttendance', methods=['POST'], endpoint='setAttendance')
def setAttendance():
    attendance = request.json
    if len(attendance) != 2:
        result = {'status': 'error', 'message': '发送数据长度不等于2：有误'}
    else:
        message = ''

        staffId = attendance[0]
        attendance_state = attendance[1]

        staff_information = staffInformation.query.filter(staffId == staffInformation.staffId).first()




        result = {'status': 'success', 'message': message}
    return jsonify(result),200
