import os

from flask import render_template, request, session, redirect, url_for, abort, jsonify
from flask import Blueprint

from apps.Index.index_admin import login_required
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff, faceValue, Set, Outs, Works, Holidays, Adds
from exts import db


@login_required('<admin_username>')
@admin_bp.route("/<admin_username>/<departmentId>", methods=['POST', "GET"])
def staff_manage(admin_username, departmentId):
    if session.get(admin_username+'admin_username') is not None:
            if len(departmentId) == 3:
                adminId = admin_username
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
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/openFaceState', methods=['POST'], endpoint='openFaceState')
def openFaceState(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
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
    else:
        return redirect(url_for('login.login'))

@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/closeFaceState', methods=['POST'], endpoint='closeFaceState')
def closeFaceState(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
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
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/setAttendance', methods=['POST'], endpoint='setAttendance')
def setAttendance(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        attendance = request.json
        if len(attendance) != 2:
            result = {'status': 'error', 'message': '发送数据长度不等于2：有误'}
        else:

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
    else:
        return redirect(url_for('login.login'))


# 编辑职工职务信息
@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/edit_message', methods=['POST'], endpoint='edit_message')
def edit_message(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
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
        if os.path.isdir(old_filename):
            os.rename(old_filename, new_filename)

        return jsonify({'message': '职工职务信息已保存'}), 200
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/getDepartments', methods=["GET", "POST"], endpoint='getDepartments')
def getDepartments(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        departments = Departments.query.all()
        department_results = []
        for department in departments:
            department_results.append(department.departmentName + "," + department.departmentId)

        options = department_results
        return jsonify(options)
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/getPositions', methods=["GET", "POST"], endpoint='getPositions')
def getPositions(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        positions = Position.query.all()
        position_results = []
        for position in positions:
            position_results.append(position.positionName + "," + position.positionId + "," + str(position.positionLevel))

        options = position_results
        return jsonify(options)
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/add_staff', methods=['POST'], endpoint='add_staff')
def add_staff(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        employee_id = request.form['add_employee-id']
        employee_name = request.form['add_employee-name']
        department_name = request.form['add_department']
        employee_gender = request.form['add_gender']
        position_name = request.form['position']
        employee_password = request.form['add_employee-password']

        # 职工ID、密码
        staff = Staff()
        staff_information = staffInformation()
        staff.staffId = employee_id
        staff.staffPassWord = employee_password
        staff_information.staffId = employee_id

        # 职工姓名
        staff_information.staffName = employee_name

        # 职工性别
        if employee_gender == '0':
            employee_gender = '男'
        else:
            employee_gender = '女'

        staff_information.staffGender = employee_gender

        # 职工职务
        position = Position.query.filter(position_name == Position.positionName).first()
        staff_information.staffPositionId = position.positionId

        # 隶属部门
        department = Departments.query.filter(department_name == Departments.departmentName).first()
        staff_information.staffDepartmentId = department.departmentId

        # 初始化人脸字段为空
        staff_face = faceValue()
        staff_face.staffId = employee_id

        # 初始化考勤设置
        staff_set = Set()
        staff_set.staffId = employee_id

        # 初始化工作状态
        staff_works = Works()
        staff_works.staffId = employee_id

        # 初始化假期状态
        staff_holidays = Holidays()
        staff_holidays.staffId = employee_id

        # 初始化加班状态
        staff_adds = Adds()
        staff_adds.staffId = employee_id

        # 初始化出差状态
        staff_outs = Outs()
        staff_outs.staffId = employee_id

        # 提交保存
        db.session.add_all([staff, staff_information, staff_face, staff_set, staff_works,
                            staff_holidays, staff_adds, staff_outs])
        db.session.commit()

        return jsonify({'message': '职工职务信息已保存'}), 200
    else:
        return redirect(url_for('login.login'))


@login_required('<admin_username>')
@admin_bp.route('/<admin_username>/get_message', methods=['GET', 'POST'], endpoint='get_message')
def get_message(admin_username):
    if session.get(admin_username + 'admin_username') is not None:
        data = request.get_json()
        staffId = data.get('staff_Id')
        result_id = ['staff_id', 'staff_name', 'staff_gender', 'staff_department', 'staff_position', 'staff_face_status',
                    'staff_face_authority', 'staff_email', 'staff_phone', 'staff_attendance_status', 'staff_birthday',
                    'staff_country', 'staff_nation', 'staff_hometown', 'staff_address', 'staff_remark']
        staff_information = staffInformation.query.filter(staffId == staffInformation.staffId).first()
        position = Position.query.filter(staff_information.staffPositionId == Position.positionId).first()
        department = Departments.query.filter(staff_information.staffDepartmentId == Departments.departmentId).first()

        staff_id = staffId
        staff_name = staff_information.staffName
        staff_gender = staff_information.staffGender
        staff_department = department.departmentName
        staff_position = position.positionName
        staff_face_status = staff_information.faceValueState
        staff_face_authority = staff_information.staffGetFaceState
        staff_email = staff_information.staffEmailAddress
        staff_phone = staff_information.staffPhoneNumber
        staff_attendance_status = staff_information.staffCheckState
        staff_birthday = staff_information.staffBirthday
        staff_country = staff_information.staffCountry
        staff_nation = staff_information.staffNation
        staff_hometown = staff_information.staffOrigin
        staff_address = staff_information.staffAddress
        staff_remark = staff_information.staff_Remark
        result_message = [staff_id, staff_name, staff_gender, staff_department, staff_position, staff_face_status,
                        staff_face_authority, staff_email, staff_phone, staff_attendance_status, staff_birthday,
                        staff_country, staff_nation, staff_hometown, staff_address, staff_remark]

        options = dict(zip(result_id,result_message))

        return jsonify(options)
    else:
        return redirect(url_for('login.login'))
