import os

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
            return ''


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

        staffId = attendance[1]
        attendance_state = attendance[0]

        staff_information = staffInformation.query.filter(staffId == staffInformation.staffId).first()

        if attendance_state == 'state_break':

            staff_information.staffCheckState = 0
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-grey' id='" + staffId + "State'><i class='glyphicon glyphicon-headphones' ></i> 非工作时间"

        elif attendance_state == 'today_work':

            staff_information.staffCheckState = 10
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤"

        elif attendance_state == 'today_out':

            staff_information.staffCheckState = 11
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-orange' id='" + staffId + "State'><i class='glyphicon glyphicon-globe' ></i> 今日出差"

        elif attendance_state == 'today_holiday':

            staff_information.staffCheckState = 12
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-blue' id='" + staffId + "State'><i class='glyphicon glyphicon-shopping-cart' ></i> 今日休假"

        elif attendance_state == 'add_work':

            staff_information.staffCheckState = 13
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-leaf' ></i> 加班出勤"

        elif attendance_state == 'today_not_work':

            staff_information.staffCheckState = 20
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-red' id='" + staffId + "State'><i class='glyphicon glyphicon-remove-circle' ></i> 今日缺勤"

        elif attendance_state == 'today_late':

            staff_information.staffCheckState = 21
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-red' id='" + staffId + "State'><i class='glyphicon glyphicon-hourglass' ></i> 今日迟到"

        elif attendance_state == 'today_early':

            staff_information.staffCheckState = 22
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-red' id='" + staffId + "State'><i class='glyphicon glyphicon-glass' ></i> 今日早退"

        elif attendance_state == 'add_not_work':

            staff_information.staffCheckState = 23
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-red' id='" + staffId + "State'><i class='glyphicon glyphicon-warning-sign' ></i> 加班缺勤"

        elif attendance_state == 'add_late':

            staff_information.staffCheckState = 24
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-red' id='" + staffId + "State'><i class='glyphicon glyphicon-bell' ></i> 加班迟到"

        elif attendance_state == 'add_early':

            staff_information.staffCheckState = 25
            # 其他表的更新操作

            # 如果正确完成更新
            db.session.commit()
            message = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-cutlery' ></i> 加班早退"

        else:
            message = 'error: 不存在正确的attendance_state'
        result = {'status': 'success', 'message': message}
    return jsonify(result), 200


# 编辑职工职务信息
@admin_bp.route('/edit_message', methods=['POST'], endpoint='edit_message')
def edit_message():
    employee_id_new = request.form['employee-id']
    employee_name_new = request.form['employee-name']
    department_name = request.form['department']
    position_name = request.form['position']
    employment_status = request.form['employment-status']
    employee_id_old = request.form['staffId_old']

    # 职工ID
    staff = Staff.query.filter(employee_id_old == Staff.staffId).first()
    staff_information = staffInformation.query.filter(employee_id_old == staffInformation.staffId).first()
    staff.staffId = employee_id_new

    # 职工姓名
    staff_information.staffName = employee_name_new

    # 在职状态
    if employment_status == '1':
        staff.staffState = True
    else:
        staff.staffState = False

    # 职工职务
    position = Position.query.filter(position_name == Position.positionName).first()
    staff_information.staffPositionId = position.positionId

    # 隶属部门
    department = Departments.query.filter(department_name == Departments.departmentName).first()
    staff_information.staffDepartmentId = department.departmentId

    # 提交保存
    db.session.commit()

    # 修改头像图片保存的文件夹名称
    old_filename = "static/data/data_headimage_staff/" + employee_id_old
    new_filename = "static/data/data_headimage_staff/" + employee_id_new
    os.rename(old_filename, new_filename)

    return jsonify({'message': '职工职务信息已保存'}), 200


@admin_bp.route('/getDepartments', methods=["GET", "POST"], endpoint='getDepartments')
def getDepartments():
    departments = Departments.query.all()
    department_results = []
    for department in departments:
        department_results.append(department.departmentName + "," + department.departmentId)

    options = department_results
    return jsonify(options)


@admin_bp.route('/getPositions', methods=["GET", "POST"], endpoint='getPositions')
def getPositions():
    positions = Position.query.all()
    position_results = []
    for position in positions:
        position_results.append(position.positionName + "," + position.positionId + "," + str(position.positionLevel))

    options = position_results
    return jsonify(options)






