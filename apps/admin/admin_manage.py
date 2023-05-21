import os
from datetime import datetime, time

from flask import render_template, request, session, redirect, url_for, abort, jsonify
from flask import Blueprint

from apps.Index.index_admin import login_required
from apps.admin.__init__ import admin_bp
from apps.models.check_model import Admin, Departments, Position, staffInformation, Staff, faceValue, Set, Outs, Works, \
    Holidays, Adds, Attendance, Sum
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
        global  status
        global  message
        status = 'error'
        message = '！！! 不可修改 ！！！'
        attendance_receive = request.json
        if len(attendance_receive) != 2:
            result = {'status': 'error', 'message': '发送数据长度不等于2：有误'}
        else:

            staffId = attendance_receive[1]
            attendance_state = attendance_receive[0]

            staff_information = staffInformation.query.filter(staffId == staffInformation.staffId).first()
            set = Set.query.filter(staffId == Set.staffId).first()
            current_date = datetime.now().date()
            current_datetime = datetime.now()
            attendanceId = current_date.strftime('%Y-%m-%d') + set.staffId
            attendance = Attendance.query.filter(attendanceId == Attendance.attendanceId).first()
            current_date_year = datetime.now().date().strftime("%Y")
            current_date_month = datetime.now().date().strftime("%m")
            sum_Id = current_date_year + '-' + current_date_month + '-' + set.staffId
            sum = Sum.query.filter(sum_Id == Sum.sumId).first()
            holiday = Holidays.query.filter(staffId == Holidays.staffId).first()
            work = Works.query.filter(staffId == Works.staffId).first()
            out = Outs.query.filter(Outs.staffId == staffId).first()


            # 先检测今日是否存在考勤记录： 检测attendance的记录是否存在
            if attendance is not None:

                # 要求修改为 '今日出勤'
                if attendance_state == 'today_work':

                    # 原本状态为：今日缺勤 | 要求修改为 今日出勤
                    if attendance.attendState == 8 and staff_information.staffCheckState == 20:
                        # 设置应签到/签退时间为今日考勤记录的起始/结束时间
                        attendance.attendTime = set.attendTime.time()
                        attendance.endTime = set.endTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username

                        # 计算出勤时间
                        dt1 = datetime.combine(current_date, attendance.endTime)
                        dt2 = datetime.combine(current_date, attendance.attendTime)
                        time_diff = dt1 - dt2
                        # 获取总秒数
                        total_seconds = time_diff.total_seconds()
                        # 计算时、分、秒的差异
                        hours = int(total_seconds // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        attendance.workTime = time(hours, minutes, seconds)

                        # 修改考勤状态为今日已经完成出勤
                        attendance.attendState = 6
                        staff_information.staffCheckState = 14

                        # 将今天的工作时间存入本月工作时间记录
                        float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数

                        if sum.workSumTime is not None:
                            sum.workSumTime = sum.workSumTime + float_time
                        else:
                            sum.workSumTime = float_time

                        # 正常出勤次数 + 1
                        sum.attendFrequency = sum.attendFrequency + 1
                        # 缺勤次数     - 1
                        sum.absenceFrequency = sum.absenceFrequency - 1

                        # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                        if work.workTime is None:
                            work.workTime = float_time
                        else:
                            work.workTime = work.workTime + float_time

                    # 原本状态为 今日迟到（工作中） | 要求修改为  今日出勤(工作中）
                    if attendance.attendState == 2 and staff_information.staffCheckState == 21:
                        # 修改考勤记录的状态为 1 正常出勤
                        attendance.attendState = 1
                        # 修改职工综合信息中的考勤状态为 正常出勤(工作中)
                        staff_information.staffCheckState = 10
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 原本状态为 今日出勤|早退     |  要求修改为  今日出勤(已经完成工作)
                    if attendance.attendState == 3 and staff_information.staffCheckState == 22:
                        # 记录旧的早退的时间
                        old_endTime = attendance.endTime
                        # 设置应签退时间为今日考勤记录的结束时间
                        attendance.endTime = set.endTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username

                        # 计算需要新添加的出勤时间
                        dt1 = datetime.combine(current_date, attendance.endTime)
                        dt2 = datetime.combine(current_date, old_endTime)
                        dt3 = datetime.combine(current_date, attendance.attendTime)
                        new_part_time_diff = dt1 - dt2
                        new_time_diff = dt1 - dt3

                        # 获取总秒数（新增部分）
                        new_part_total_seconds = new_part_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增部分)
                        new_part_hours = int(new_part_total_seconds // 3600)
                        new_part_minutes = int((new_part_total_seconds % 3600) // 60)
                        new_part_seconds = int(new_part_total_seconds % 60)

                        # 获取总秒数（新增之后整体）
                        new_total_seconds = new_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增整体)
                        new_hours = int(new_total_seconds // 3600)
                        new_minutes = int((new_total_seconds % 3600) // 60)
                        new_seconds = int(new_total_seconds % 60)

                        new_part_workTime = time(new_part_hours, new_part_minutes, new_part_seconds)
                        new_workTime = time(new_hours, new_minutes, new_seconds)
                        # 更新考勤记录中的工作时间
                        attendance.workTime = new_workTime

                        # 修改考勤状态为今日已经完成出勤
                        attendance.attendState = 6
                        staff_information.staffCheckState = 14

                        # 将今天的新增的工作时间存入本月工作时间记录
                        float_time = new_part_workTime.hour + new_part_workTime.minute / 60 + new_part_workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数

                        if sum.workSumTime is not None:
                            sum.workSumTime = sum.workSumTime + float_time
                        else:
                            sum.workSumTime = float_time

                        # 正常出勤次数 + 1
                        sum.attendFrequency = sum.attendFrequency + 1
                        # 早退次数     - 1
                        sum.earlyFrequency = sum.earlyFrequency - 1

                        # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                        if work.workTime is None:
                            work.workTime = float_time
                        else:
                            work.workTime = work.workTime + float_time

                    # 原本状态为 今日迟到|未出勤   |  要求修改为  今日出勤(工作中）
                    if attendance.attendState == 2 and staff_information.staffCheckState == 23:
                        # 修改考勤记录的状态为 1 正常出勤
                        attendance.attendState = 1
                        # 修改职工综合信息中的考勤状态为 正常出勤(工作中)
                        staff_information.staffCheckState = 10
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 原本状态为 今日迟到|临时外出 |  要求修改为   今日出勤(临时外出)
                    if attendance.attendState == 5 and staff_information.staffCheckState == 25:
                        # 考勤记录的考勤状态改为 4 正常出勤|临时外出
                        attendance.attendState = 4
                        # 职工综合信息的考勤状态改为 16 今日出勤（临时外出）
                        staff_information.staffCheckState = 16
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 今日迟到（已经完成工作）     |  要求修改为   今日出勤（已经完成工作）
                    if attendance.attendState == 2 and staff_information.staffCheckState == 26:
                        # 记录旧的迟到的签到时间
                        old_attendTime = attendance.attendTime
                        # 设置应签到时间为今日考勤记录的签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username

                        # 计算需要新添加的出勤时间
                        dt1 = datetime.combine(current_date, attendance.endTime)
                        dt2 = datetime.combine(current_date, old_attendTime)
                        dt3 = datetime.combine(current_date, attendance.attendTime)
                        new_part_time_diff = dt2 - dt3
                        new_time_diff = dt1 - dt3

                        # 获取总秒数（新增部分）
                        new_part_total_seconds = new_part_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增部分)
                        new_part_hours = int(new_part_total_seconds // 3600)
                        new_part_minutes = int((new_part_total_seconds % 3600) // 60)
                        new_part_seconds = int(new_part_total_seconds % 60)

                        # 获取总秒数（新增之后整体）
                        new_total_seconds = new_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增整体)
                        new_hours = int(new_total_seconds // 3600)
                        new_minutes = int((new_total_seconds % 3600) // 60)
                        new_seconds = int(new_total_seconds % 60)

                        new_part_workTime = time(new_part_hours, new_part_minutes, new_part_seconds)
                        new_workTime = time(new_hours, new_minutes, new_seconds)
                        # 更新考勤记录中的工作时间
                        attendance.workTime = new_workTime

                        # 修改考勤状态为今日已经完成出勤
                        attendance.attendState = 6
                        staff_information.staffCheckState = 14

                        # 将今天的新增的工作时间存入本月工作时间记录
                        float_time = new_part_workTime.hour + new_part_workTime.minute / 60 + new_part_workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数

                        if sum.workSumTime is not None:
                            sum.workSumTime = sum.workSumTime + float_time
                        else:
                            sum.workSumTime = float_time

                        # 正常出勤次数 + 1
                        sum.attendFrequency = sum.attendFrequency + 1
                        # 迟到次数     - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                        # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                        if work.workTime is None:
                            work.workTime = float_time
                        else:
                            work.workTime = work.workTime + float_time

                    # 原本状态为 今日迟到|早退     |  要求修改为   今日出勤（已经完成工作）
                    if attendance.attendState == 7 and staff_information.staffCheckState == 24:
                        # 记录旧的早退的时间
                        old_endTime = attendance.endTime
                        # 记录旧的迟到签到时间
                        old_attendTime  = attendance.attendTime
                        # 设置应签退/签到时间为今日考勤记录的签到/签退时间
                        attendance.endTime = set.endTime.time()
                        attendance.attendTime = set.attendTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = admin_username

                        # 计算需要新添加的出勤时间
                        dt1 = datetime.combine(current_date, attendance.endTime)
                        dt2 = datetime.combine(current_date, old_endTime)
                        dt3 = datetime.combine(current_date, old_attendTime)
                        dt4 = datetime.combine(current_date, attendance.attendTime)
                        new_part_time_diff = (dt3-dt4) + (dt1-dt2)
                        new_time_diff = dt1 - dt4

                        # 获取总秒数（新增部分）
                        new_part_total_seconds = new_part_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增部分)
                        new_part_hours = int(new_part_total_seconds // 3600)
                        new_part_minutes = int((new_part_total_seconds % 3600) // 60)
                        new_part_seconds = int(new_part_total_seconds % 60)

                        # 获取总秒数（新增之后整体）
                        new_total_seconds = new_time_diff.total_seconds()
                        # 计算时、分、秒的差异(新增整体)
                        new_hours = int(new_total_seconds // 3600)
                        new_minutes = int((new_total_seconds % 3600) // 60)
                        new_seconds = int(new_total_seconds % 60)

                        new_part_workTime = time(new_part_hours, new_part_minutes, new_part_seconds)
                        new_workTime = time(new_hours, new_minutes, new_seconds)
                        # 更新考勤记录中的工作时间
                        attendance.workTime = new_workTime

                        # 修改考勤状态为今日已经完成出勤
                        attendance.attendState = 6
                        staff_information.staffCheckState = 14

                        # 将今天的新增的工作时间存入本月工作时间记录
                        float_time = new_part_workTime.hour + new_part_workTime.minute / 60 + new_part_workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数

                        if sum.workSumTime is not None:
                            sum.workSumTime = sum.workSumTime + float_time
                        else:
                            sum.workSumTime = float_time

                        # 正常出勤次数 + 1
                        sum.attendFrequency = sum.attendFrequency + 1
                        # 早退次数     - 1
                        sum.earlyFrequency = sum.earlyFrequency - 1
                        # 迟到次数     - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                        # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                        if work.workTime is None:
                            work.workTime = float_time
                        else:
                            work.workTime = work.workTime + float_time

                    # 如果正确完成更新
                    db.session.commit()
                    message = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤"

                elif attendance_state == 'today_out':
                    # 如果工作时间不为空，则不足八小时的补足八小时，足够8小时的不处理
                    # 考勤记录的考勤记录状态归 0
                    # 对于 已经记录的 正常出勤/迟到/早退/缺勤 的记录 要消去


                    staff_information.staffCheckState = 11
                    # 其他表的更新操作

                    # 如果正确完成更新
                    db.session.commit()
                    message = "class='custom-badge status-orange' id='" + staffId + "State'><i class='glyphicon glyphicon-globe' ></i> 今日出差"

                elif attendance_state == 'today_holiday':
                    # 如果工作时间不为空，则不足八小时的补足八小时，足够8小时的不处理
                    # 考勤记录的考勤记录状态归 0
                    # 对于 已经记录的 正常出勤/迟到/早退/缺勤 的记录 要消去

                    staff_information.staffCheckState = 12
                    # 其他表的更新操作

                    # 如果正确完成更新
                    db.session.commit()
                    message = "class='custom-badge status-blue' id='" + staffId + "State'><i class='glyphicon glyphicon-shopping-cart' ></i> 今日休假"


                else:
                    status = 'error'
                    message = '！！！不存在正确的attendance_state ！！！'
            else:
                status = 'error'
                message = '不存在今日考勤记录：！今日非工作日！'

            result = {'status': status , 'message': message}
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
