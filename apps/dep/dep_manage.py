import os

from flask import render_template, request, session, redirect, url_for, jsonify
from datetime import datetime, date, time
from apps.Index.index_department_admin import login_required
from apps.dep.__init__ import depAdmin_bp
from apps.models.check_model import Departments, Position, staffInformation, Adds, Staff, faceValue, Set, Outs, Works, \
    departmentAdmin, Holidays, Attendance, Sum
from exts import db


@login_required('<depAdmin_username>')
@depAdmin_bp.route("/<depAdmin_username>/<departmentId>", methods=['POST', "GET"], endpoint='dep_staff_manage')
def dep_staff_manage(depAdmin_username, departmentId):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        if len(departmentId) == 3:
            depAdminId = depAdmin_username
            depAdmin = departmentAdmin.query.filter(depAdminId == departmentAdmin.departmentAdminId).first()
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

            return render_template('dep_all/dep_manage.html', dep=department, departmentAdmin=depAdmin,
                                   staff_list=staff_list, staff_information_list=staff_information_list,
                                   staff_position_list=staff_position_list)
        else:
            return ''
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/openFaceState', methods=['POST'], endpoint='openFaceState')
def openFaceState(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
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


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/closeFaceState', methods=['POST'], endpoint='closeFaceState')
def closeFaceState(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
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


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/setAttendance', methods=['POST'], endpoint='setAttendance')
def setAttendance(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        global status
        global message
        global message_html
        status = 'error'
        message = '！！! 不可修改 ！！！'
        message_html = ''
        attendance_receive = request.json
        if len(attendance_receive) != 2:
            result = {'status': 'error', 'message': '发送数据长度不等于2：有误', 'message_html': message_html}
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
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（已经完成工作）"
                        message = '已经从 今日缺勤 修改为 今日出勤（已经完成工作）'
                        status = 'success'
                        # 设置应签到/签退时间为今日考勤记录的起始/结束时间
                        attendance.attendTime = set.attendTime.time()
                        attendance.endTime = set.endTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username

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
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（工作中）"
                        message = '已经从 今日迟到（工作中） 修改为 今日出勤（工作中）'
                        status = 'success'
                        # 修改考勤记录的状态为 1 正常出勤
                        attendance.attendState = 1
                        # 修改职工综合信息中的考勤状态为 正常出勤(工作中)
                        staff_information.staffCheckState = 10
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 原本状态为 今日出勤|早退     |  要求修改为  今日出勤(已经完成工作)
                    if attendance.attendState == 3 and staff_information.staffCheckState == 22:
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（已经完成工作）"
                        message = '已经从 今日缺勤（早退） 修改为 今日出勤（已经完成工作）'
                        status = 'success'
                        # 记录旧的早退的时间
                        old_endTime = attendance.endTime
                        # 设置应签退时间为今日考勤记录的结束时间
                        attendance.endTime = set.endTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username

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
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（工作中）"
                        message = '已经从 今日迟到（未出勤） 修改为 今日出勤（工作中）'
                        status = 'success'
                        # 修改考勤记录的状态为 1 正常出勤
                        attendance.attendState = 1
                        # 修改职工综合信息中的考勤状态为 正常出勤(工作中)
                        staff_information.staffCheckState = 10
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 原本状态为 今日迟到|临时外出 |  要求修改为   今日出勤(临时外出)
                    if attendance.attendState == 5 and staff_information.staffCheckState == 25:
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（临时外出）"
                        message = '已经从 今日迟到（临时外出） 修改为 今日出勤（临时外出）'
                        status = 'success'
                        # 考勤记录的考勤状态改为 4 正常出勤|临时外出
                        attendance.attendState = 4
                        # 职工综合信息的考勤状态改为 16 今日出勤（临时外出）
                        staff_information.staffCheckState = 16
                        # 更新修改考勤记录的时间/修改考勤记录的ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username
                        # 设置出勤时间为 set 中设置的应签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 迟到的 sum 记录次数 - 1
                        sum.lateFrequency = sum.lateFrequency - 1

                    # 今日迟到（已经完成工作）     |  要求修改为   今日出勤（已经完成工作）
                    if attendance.attendState == 9 and staff_information.staffCheckState == 26:
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤（已经完成工作）"
                        message = '已经从 今日迟到（已经完成工作） 修改为 今日出勤（已经完成工作）'
                        status = 'success'
                        # 记录旧的迟到的签到时间
                        old_attendTime = attendance.attendTime
                        # 设置应签到时间为今日考勤记录的签到时间
                        attendance.attendTime = set.attendTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username

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
                        message = '已经从 今日迟到（早退） 修改为 今日出勤（已经完成工作）'
                        status = 'success'
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出勤(已经完成工作)"
                        # 记录旧的早退的时间
                        old_endTime = attendance.endTime
                        # 记录旧的迟到签到时间
                        old_attendTime = attendance.attendTime
                        # 设置应签退/签到时间为今日考勤记录的签到/签退时间
                        attendance.endTime = set.endTime.time()
                        attendance.attendTime = set.attendTime.time()
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username

                        # 计算需要新添加的出勤时间
                        dt1 = datetime.combine(current_date, attendance.endTime)
                        dt2 = datetime.combine(current_date, old_endTime)
                        dt3 = datetime.combine(current_date, old_attendTime)
                        dt4 = datetime.combine(current_date, attendance.attendTime)
                        new_part_time_diff = (dt3 - dt4) + (dt1 - dt2)
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

                elif attendance_state == 'today_out':
                    # 如果工作时间不为空，则不足八小时的补足八小时，足够8小时的不处理
                    # 考勤记录的考勤记录状态归 0
                    # 对于 已经记录的 正常出勤/迟到/早退/缺勤 的记录 要消去
                    if attendance.outState:
                        message = '原本考勤状态即为出差状态 | 未做变动'
                        status = 'error'
                    elif attendance.holidayState:
                        message = '原本考勤状态为休假状态 | 现修改为出差状态'
                        status = 'success'
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出差"
                        attendance.outState = False
                        attendance.holidayState = True
                        staff_information.staffCheckState = 11
                        # 设置出差状态
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username
                        # 休假次数 - 1
                        sum.holidayFrequency = sum.holidayFrequency - 1
                        # 出差次数 + 1
                        sum.outFrequency = sum.outFrequency + 1
                        # 将今天的工作时间存入本月工作时间记录
                        float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数
                        # 从年度总剩余休假时长中加上休假时长
                        if holiday.holidayTime is None:
                            holiday.holidayTime = 0 + float_time
                        else:
                            holiday.holidayTime = holiday.holidayTime + float_time
                        # 给年度出差总时长加上出差时长
                        if out.outTime is None:
                            out.outTime = 0 + float_time
                        else:
                            out.outTime = out.outTime + float_time

                    else:
                        if attendance.attendState == 0 or attendance.attendState == 1 or attendance.attendState == 2 or attendance.attendState == 4 or attendance.attendState == 5 or attendance.attendState == 8:
                            attendance.holidayState = True
                            attendance.attendState = 0
                            staff_information.staffCheckState = 11
                            # 更新 考勤记录的修改时间/考勤记录的修改者ID
                            attendance.editTime = current_datetime
                            attendance.editId = depAdmin_username
                            message = '现改为 出差状态'
                            status = 'success'
                            message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日出差"
                            # 设置休假状态
                            attendance.workTime = time(hour=8, minute=0, second=0)
                            # 工作时长直接拉满

                            # 将今天的工作时间存入本月工作时间记录
                            float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                            # 转换为以小时为整数的浮点数
                            float_time = round(float_time, 3)
                            # 保留3位小数
                            if sum.workSumTime is not None:
                                sum.workSumTime = sum.workSumTime + float_time
                            else:
                                sum.workSumTime = float_time

                            # 出差次数 + 1
                            sum.outFrequency = sum.outFrequency + 1

                            if attendance.attendState == 2 or attendance.attendState == 5:
                                sum.lateFrequency = sum.lateFrequency - 1

                            if attendance.attendState == 8:
                                sum.absenceFrequency = sum.absenceFrequency - 1

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time

                            # 从年度总剩余休假时长中减去休假时长
                            holiday = Holidays.query.filter(set.staffId == Holidays.staffId).first()
                            if holiday.holidayTime is None:
                                holiday.holidayTime = 0 - float_time
                            else:
                                holiday.holidayTime = holiday.holidayTime - float_time
                            # 要注意系统管理员要加一条： 给每个新添加的用户设置本年度休假总时长
                        else:
                            message = '原本考勤状态已经完成签到/签退 | 不可再改为出差状态'
                            status = 'error'

                    # 如果正确完成更新
                    db.session.commit()

                elif attendance_state == 'today_holiday':
                    # 如果工作时间不为空，则不足八小时的补足八小时，足够8小时的不处理
                    # 考勤记录的考勤记录状态归 0
                    # 对于 已经记录的 正常出勤/迟到/早退/缺勤 的记录 要消去

                    if attendance.holidayState:
                        message = '原本考勤状态即为休假状态 | 未做变动'
                        status = 'error'
                    elif attendance.outState:
                        message = '原本考勤状态为出差状态 | 现修改为休假状态'
                        status = 'success'
                        message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日休假"
                        attendance.outState = False
                        attendance.holidayState = True
                        staff_information.staffCheckState = 12
                        # 设置休假状态
                        # 更新 考勤记录的修改时间/考勤记录的修改者ID
                        attendance.editTime = current_datetime
                        attendance.editId = depAdmin_username
                        # 休假次数 + 1
                        sum.holidayFrequency = sum.holidayFrequency + 1
                        # 出差次数 - 1
                        sum.outFrequency = sum.outFrequency - 1
                        # 将今天的工作时间存入本月工作时间记录
                        float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                        # 转换为以小时为整数的浮点数
                        float_time = round(float_time, 3)
                        # 保留3位小数
                        # 从年度总剩余休假时长中减去休假时长
                        if holiday.holidayTime is None:
                            holiday.holidayTime = 0 - float_time
                        else:
                            holiday.holidayTime = holiday.holidayTime - float_time
                        # 给年度出差总时长减去出差时长
                        if out.outTime is None:
                            out.outTime = 0 - float_time
                        else:
                            out.outTime = out.outTime - float_time
                    else:
                        if attendance.attendState == 0 or attendance.attendState == 1 or attendance.attendState == 2 or attendance.attendState == 4 or attendance.attendState == 5 or attendance.attendState == 8:
                            attendance.holidayState = True
                            attendance.attendState = 0
                            staff_information.staffCheckState = 12
                            # 更新 考勤记录的修改时间/考勤记录的修改者ID
                            attendance.editTime = current_datetime
                            attendance.editId = depAdmin_username
                            message = '现改为 休假状态'
                            status = 'success'
                            message_html = "class='custom-badge status-green' id='" + staffId + "State'><i class='glyphicon glyphicon-ok-sign' ></i> 今日休假"
                            # 设置休假状态
                            attendance.workTime = time(hour=8, minute=0, second=0)
                            # 工作时长直接拉满

                            # 将今天的工作时间存入本月工作时间记录
                            float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                            # 转换为以小时为整数的浮点数
                            float_time = round(float_time, 3)
                            # 保留3位小数
                            if sum.workSumTime is not None:
                                sum.workSumTime = sum.workSumTime + float_time
                            else:
                                sum.workSumTime = float_time

                            # 休假次数 + 1
                            sum.holidayFrequency = sum.holidayFrequency + 1

                            if attendance.attendState == 2 or attendance.attendState == 5:
                                sum.lateFrequency = sum.lateFrequency - 1

                            if attendance.attendState == 8:
                                sum.absenceFrequency = sum.absenceFrequency - 1

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time

                            # 从年度总剩余休假时长中减去休假时长
                            holiday = Holidays.query.filter(set.staffId == Holidays.staffId).first()
                            if holiday.holidayTime is None:
                                holiday.holidayTime = 0 - float_time
                            else:
                                holiday.holidayTime = holiday.holidayTime - float_time
                            # 要注意系统管理员要加一条： 给每个新添加的用户设置本年度休假总时长
                        else:
                            message = '原本考勤状态已经完成签到/签退 | 不可再改为休假状态'
                            status = 'error'

                    # 如果正确完成更新
                    db.session.commit()

                else:
                    status = 'error'
                    message = '！！无法对当前的考勤状态进行修改！！'
            else:
                status = 'error'
                message = '不存在今日考勤记录：！今日非工作日！'

            result = {'status': status, 'message': message, 'message_html': message_html}
        return jsonify(result), 200
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/get_message', methods=['GET', 'POST'], endpoint='get_message')
def get_message(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        data = request.get_json()
        staffId = data.get('staff_Id')
        result_id = ['staff_id', 'staff_name', 'staff_gender', 'staff_department', 'staff_position',
                     'staff_face_status',
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

        options = dict(zip(result_id, result_message))

        return jsonify(options)
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/<departmentId>/<staff_username>/staff_records', methods=['POST', 'GET'],
                   endpoint='staff_records')
def staff_records(depAdmin_username, departmentId, staff_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        if len(departmentId) == 3:


            depAdminId = depAdmin_username
            staff_information = staffInformation.query.filter(staffInformation.staffId == staff_username).first()
            position = Position.query.filter(Position.positionId == staff_information.staffPositionId).first()
            depAdmin = departmentAdmin.query.filter(depAdminId == departmentAdmin.departmentAdminId).first()
            department = Departments.query.filter(staff_information.staffDepartmentId == Departments.departmentId).first()
            attendances = Attendance.query.filter(Attendance.staffId == staff_username).all()
            attendance_data = []
            for attendance in attendances:
                staffId = staff_username
                staffName = staff_information.staffName
                attendanceId = attendance.attendanceId
                departmentName = department.departmentName
                positionName = position.positionName
                attendance_state = attendance.attendState
                attendance_date = attendance.attendDate
                attendance_editId = attendance.editId
                attendance_editTime = attendance.editTime
                attendance_outState = attendance.outState
                attendance_holidayState = attendance.holidayState
                attendance_data.append({'staffId': staffId, 'staffName': staffName, 'departmentName': departmentName, 'attendanceId': attendanceId,
                                        'positionName': positionName, 'attendance_state': attendance_state, 'attendance_date': attendance_date,
                                        'attendance_editId': attendance_editId, 'attendance_editTime':attendance_editTime,
                                        'attendance_outState': attendance_outState, 'attendance_holidayState': attendance_holidayState})


            return render_template('dep_all/staff_records.html',
            attendances=attendance_data, dep=department, departmentAdmin=depAdmin, staff_information=staff_information)
        else:
            return ''
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/search_attendance', methods=['POST', 'GET'], endpoint='search_attendance')
def search_attendance(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        message = request.json
        staffId = str(message.get('staffId'))
        state = message.get('state')
        start_date = message.get('beginDate')
        end_date = message.get('endDate')

        staff_information = staffInformation.query.filter(staffInformation.staffId == staffId).first()
        position = Position.query.filter(Position.positionId == staff_information.staffPositionId).first()
        department = Departments.query.filter(
            staff_information.staffDepartmentId == Departments.departmentId).first()

        attendance_data = []
        message_return = ''
        status = 'nothing'

        if start_date == '' or end_date == '':
            message_return = message_return +  '存在至少一个时间为空，当前查询结果未按时间检索'

            if state == '*':
                message_return = message_return + ' | 未选择检索类型，当前查询结果包含全部考勤状态'
                attendances = Attendance.query.filter(Attendance.staffId == staffId).all()
            else:
                attendances = Attendance.query.filter(Attendance.staffId == staffId,
                                                  Attendance.attendState == int(state)).all()
        else:
            beginDate =datetime.strptime(start_date, '%Y-%m-%d')
            endDate = datetime.strptime(end_date, '%Y-%m-%d')
            if beginDate > endDate:
                status = 'error'
                message_return = message_return + '查询的起始日期大于结束时间： 错误！'
                return jsonify({'status': status, 'message': message_return, 'data': attendance_data})
            elif state == '*':
                message_return = message_return + ' | 未选择检索类型，当前查询结果包含全部考勤状态'
                attendances = Attendance.query.filter(Attendance.attendDate.between(beginDate, endDate),  Attendance.staffId == staffId).all()
            else:
                attendances = Attendance.query.filter(Attendance.attendDate.between(beginDate, endDate),
                                                      Attendance.staffId == staffId, Attendance.attendState==int(state)).all()

        if attendances:
            status = 'success'
            message_return = message_return + ' | 已经获取到指定条件下的考勤记录'
            for attendance in attendances:
                staffName = staff_information.staffName
                attendanceId = attendance.attendanceId
                departmentName = department.departmentName
                positionName = position.positionName
                attendance_state = attendance.attendState
                attendance_date = attendance.attendDate
                attendance_editId = attendance.editId
                attendance_editTime = attendance.editTime
                attendance_outState = attendance.outState
                attendance_holidayState = attendance.holidayState
                attendance_data.append({'staffId': staffId, 'staffName': staffName, 'departmentName': departmentName,
                                        'attendanceId': attendanceId,
                                        'positionName': positionName, 'attendance_state': attendance_state,
                                        'attendance_date': attendance_date.strftime("%Y-%m-%d %H:%M:%S"),
                                        'attendance_editId': attendance_editId,
                                        'attendance_editTime': attendance_editTime.strftime("%Y-%m-%d %H:%M:%S"),
                                        'attendance_outState': attendance_outState,
                                        'attendance_holidayState': attendance_holidayState})
        else:
            status = 'nothing'
            message_return = '按照当前条件查询下无考勤记录！'

        return jsonify({'status': status, 'message': message_return, 'data': attendance_data})
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/selectPersons', methods=['POST', 'GET'], endpoint='selectPersons')
def selectPersons(depAdmin_username):
    selected_persons = request.json
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        if len(selected_persons) > 0:
            session['selectPersons'] = selected_persons

            persons = ''
            for person in selected_persons:
                persons += person

            message = '已经选中职工' + persons
            result = {'status': 'success', 'message': message}
        else:
            message = '未选中职工'
            result = {'status': 'error', 'message': message}
        return jsonify(result)
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/edit_attend_add_set', methods=['POST'], endpoint='edit_attend_add_set')
def edit_attend_add_set(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:

        # 获取表单数据
        attend_date_start = request.form['start-date-all']
        attend_date_end = request.form['end-date-all']
        attend_datetime_start = request.form['start-datetime-all']
        attend_datetime_end = request.form['end-datetime-all']
        add_date = request.form['add-date-all']
        add_datetime = request.form['add-datetime-all']

        if attend_datetime_start == '' or attend_datetime_end == '' or attend_date_start == '' or attend_date_end == '':
            # 考勤日期/时刻不完备的条件下：
            if add_date == '' or add_datetime == '':
                status = 'error'
                message = '错误：考勤的日期与时刻存在不完备！ +  加班的日期与时刻存在不完备'
                return jsonify({'status': status, 'message': message})
            else:
                # 加班的日期与时刻完备 / 考勤的日期与时刻不完备
                if session.get('selectPersons') is not None:
                    # 如果有已经选中的职工
                    # 转换加班签到时间的数据格式(不应该出现在for循环里)
                    add_date = datetime.strptime(add_date, '%Y-%m-%d').date()
                    add_datetime = datetime.combine(add_date, datetime.strptime(add_datetime, '%H:%M:%S').time())

                    if add_datetime <= datetime.now():
                        message = '设置的加班的具体时间 应大于 当前的具体时间'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    selected_persons = session.get('selectPersons')
                    try:
                        for person in selected_persons:
                            person_set = Set.query.filter(person == Set.staffId).first()
                            # 考勤时间不完备，故不设置

                            # 设置更新记录
                            person_set.updateTime = datetime.now()
                            person_set.updateId = depAdmin_username

                            # 更新加班应签到的具体日期时间
                            person_set.beginAddTime = add_datetime
                            db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '考勤日期与时刻不完备/加班日期与时刻已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})
                else:
                    message = '缺少已经选中的职工，无法完成职工的考勤设置修改'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

        else:
            # 考勤日期/时刻完备 / 加班日期/时刻待定

            # 考勤起始/结束日期 格式转换
            attend_date_start = datetime.strptime(attend_date_start, '%Y-%m-%d').date()
            attend_date_end = datetime.strptime(attend_date_end, '%Y-%m-%d').date()
            if attend_date_start > attend_date_end:
                status = 'error'
                message = '错误：考勤结束日日期 不可大于 起始日期！'
                return jsonify({'status': status, 'message': message})
            if attend_date_start <= date.today():
                status = 'error'
                message = '错误：考勤起始日期 应大于 今日日期！'
                return jsonify({'status': status, 'message': message})

            # 考勤应签到时刻 格式转换
            attend_datetime_start = datetime.strptime(attend_datetime_start, '%H:%M:%S').time()
            attend_datetime_start = datetime.combine(date(1900, 1, 1), attend_datetime_start)
            # 考勤应签退时刻 格式转换
            attend_datetime_end = datetime.strptime(attend_datetime_end, '%H:%M:%S').time()
            attend_datetime_end = datetime.combine(date(1900, 1, 1), attend_datetime_end)
            if attend_datetime_start >= attend_datetime_end:
                status = 'error'
                message = '错误：考勤应签到时刻 应小于 考勤应签退时刻！'
                return jsonify({'status': status, 'message': message})

            # 转换加班签到时间的数据格式 (避免在for循环中转换格式，否则多人情况下一定产生数据类型错误)
            if add_date != '' and add_datetime != '':
                add_date = datetime.strptime(add_date, '%Y-%m-%d').date()
                add_datetime = datetime.combine(add_date, datetime.strptime(add_datetime, '%H:%M:%S').time())
                if add_datetime <= datetime.now():
                    message = '设置的加班的具体时间 应大于 当前的具体时间'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

            # 写入考勤日期/时刻  %   判断加班日期/时刻是否完备
            if session.get('selectPersons') is not None:
                # 如果有已经选中的职工
                selected_persons = session.get('selectPersons')
                status = ''
                message = ''
                try:
                    for person in selected_persons:
                        staff = Staff.query.filter(person == Staff.staffId).first()
                        person_set = Set.query.filter(person == Set.staffId).first()
                        # 写入考勤时间
                        person_set.beginAttendDate = attend_date_start
                        person_set.endAttendDate = attend_date_end
                        person_set.attendTime = attend_datetime_start
                        person_set.endTime = attend_datetime_end

                        # 设置更新记录
                        person_set.updateTime = datetime.now()
                        person_set.updateId = depAdmin_username

                        # 检查是否设置了加班时间和日期
                        if add_date == '' or add_datetime == '':
                            # 未设置加班时间与日期，直接提交上述其他数据
                            db.session.commit()
                            # 正常返回
                            message = '考勤日期/时刻已经写入 + 未传入完备有效的加班时间/日期 + 完成SET的修改保存任务'
                            status = 'success'
                        else:
                            person_set.beginAddTime = add_datetime
                            db.session.commit()
                            # 正常返回
                            message = '考勤日期时刻已经写入 + 加班日期时刻已经写入 ！完成SET的修改保存任务！'
                            status = 'success'
                except Exception as e:
                    message = '存储数据错误'.format(e)
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

                return jsonify({'status': status, 'message': message})
            else:
                message = '缺少已经选中的职工，无法完成职工的考勤设置修改'
                status = 'error'
                return jsonify({'status': status, 'message': message})
    else:
        return redirect(url_for("login.login"))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/edit_holiday_out_set', methods=['POST'], endpoint='edit_holiday_out_set')
def edit_holiday_out_set(depAdmin_username):
    # 规定： 出差日期与休假日期的设置均只能从 修改设置的当天的第二天开始（不满足则弹窗警告）
    # 如果 休假与出差仅涉及 修改设置的当天一天，则手动修改当天 “今日考勤状态” 即可： 对当天的考勤记录进行更新 重新计算当天考勤记录的工作时长字段
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        # 获取表单数据
        holiday_start_date = request.form['holiday-start-date-all']
        holiday_end_date = request.form['holiday-end-date-all']
        out_start_date = request.form['out-start-date-all']
        out_end_date = request.form['out-end-date-all']

        # 设置多位用户的出差日期与休假日期的时候：不能存在日期重叠 !!!!!
        # 即：四个日期均存在的时候，保持 A起始 > B结束（BA） OR   B起始 > A结束（AB）
        # 且AB均满足各自 起始<=结束
        status = ''
        message = ''

        if holiday_start_date == '' or holiday_end_date == '':
            # 在休假日期不完备的条件下
            if out_start_date == '' or out_end_date == '':
                # 在出差日期也不完备的条件下
                status = 'error'
                message = '错误：休假的日期存在不完备！ +  出差的日期存在不完备！'
                return jsonify({'status': status, 'message': message})
            else:
                # 只满足出差日期的条件下
                if session.get('selectPersons') is not None:

                    selected_persons = session.get('selectPersons')

                    # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                    out_start_date = datetime.strptime(out_start_date, '%Y-%m-%d').date()
                    out_end_date = datetime.strptime(out_end_date, '%Y-%m-%d').date()

                    if out_start_date > out_end_date:
                        message = '设置的出差起始日期 应小于等于 出差结束日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    if out_start_date <= datetime.today().date():
                        message = '设置的出差起始日期 应大于 今天的日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    try:
                        for person in selected_persons:
                            set = Set.query.filter(person == Set.staffId).first()
                            # 写入出差起始/结束日期
                            set.beginOutDate = out_start_date
                            set.endOutDate = out_end_date
                            # 设置更新记录
                            set.updateTime = datetime.now()
                            set.updateId = depAdmin_username
                            db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '休假起始/结束日期不完备 + 出差起始/结束日期已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})
                else:
                    status = 'success'
                    # 这里使用success 方便重新更新界面去选中职工
                    # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                    message = '错误：不存在已经选中的职工'
                    return jsonify({'status': status, 'message': message})
        else:
            # 在休假日期完备的条件下
            if out_start_date == '' or out_end_date == '':
                # 但是出差日期不完备的条件下
                if session.get('selectPersons') is not None:

                    selected_persons = session.get('selectPersons')

                    # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                    holiday_start_date = datetime.strptime(holiday_start_date, '%Y-%m-%d').date()
                    holiday_end_date = datetime.strptime(holiday_end_date, '%Y-%m-%d').date()

                    if holiday_start_date > holiday_end_date:
                        message = '设置的休假起始日期 应小于等于 休假结束日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    if holiday_start_date <= datetime.today().date():
                        message = '设置的休假起始日期 应大于 今天的日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    try:
                        for person in selected_persons:
                            set = Set.query.filter(person == Set.staffId).first()

                            # 设置更新记录
                            set.updateTime = datetime.now()
                            set.updateId = depAdmin_username

                            set.beginHolidayDate = holiday_start_date
                            set.endHolidayDate = holiday_end_date

                            db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '出差日期数据不完备 +  休假日期数据已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})

                else:
                    status = 'success'
                    # 这里使用success 方便重新更新界面去选中职工
                    # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                    message = '错误：不存在已经选中的职工'
                    return jsonify({'status': status, 'message': message})
            else:
                # 出差日期与休假日期均完备的情况下
                # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                out_start_date = datetime.strptime(out_start_date, '%Y-%m-%d').date()
                out_end_date = datetime.strptime(out_end_date, '%Y-%m-%d').date()
                # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                holiday_start_date = datetime.strptime(holiday_start_date, '%Y-%m-%d').date()
                holiday_end_date = datetime.strptime(holiday_end_date, '%Y-%m-%d').date()
                if holiday_start_date > holiday_end_date or out_start_date > out_end_date:
                    message = '设置的休假起始日期 应小于等于 休假结束日期  +  设置的出差起始日期 应小于等于 出差结束日期'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})
                else:

                    if holiday_start_date <= datetime.today().date() or out_start_date <= datetime.today().date():
                        message = '设置的休假起始日期 应大于 今天的日期! + 设置的出差日期  应大于  今天的日期！'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    if holiday_start_date <= out_end_date and holiday_end_date >= out_start_date:
                        # 存在重叠日期的话
                        message = '！！！设置的休假起始日期 与 设置的出差起始日期 存在重叠日期！！！'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    else:
                        # 不存在重叠日期的话，将这四个日期一起写入数据库
                        if session.get('selectPersons') is not None:

                            selected_persons = session.get('selectPersons')

                            try:
                                for person in selected_persons:
                                    set = Set.query.filter(person == Set.staffId).first()

                                    # 设置更新记录
                                    set.updateTime = datetime.now()
                                    set.updateId = depAdmin_username

                                    # 写入休假起始/结束日期
                                    set.beginHolidayDate = holiday_start_date
                                    set.endHolidayDate = holiday_end_date
                                    # 写入出差起始/结束日期
                                    set.beginOutDate = out_start_date
                                    set.endOutDate = out_end_date

                                    db.session.commit()
                            except Exception as e:
                                message = '存储数据错误'.format(e)
                                status = 'error'
                                return jsonify({'status': status, 'message': message})

                            # 正常返回
                            message = '出差日期数据完备 +  休假日期数据完备 已经保存！完成SET的修改保存任务！'
                            status = 'success'
                            return jsonify({'status': status, 'message': message})

                        else:
                            status = 'success'
                            # 这里使用success 方便重新更新界面去选中职工
                            # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                            message = '错误：不存在已经选中的职工'
                            return jsonify({'status': status, 'message': message})
    else:
        return redirect(url_for('login.login'))


@login_required("<depAdmin_username>")
@depAdmin_bp.route('/<depAdmin_username>/get_message_holiday_out_set_single', methods=['POST'],
                endpoint='get_message_holiday_out_set_single')
def get_message_holiday_out_set_single(depAdmin_username):
    if session.get(depAdmin_username+'depAdmin_username') is not None:
        data = request.get_json()
        staffId = data.get('staff_Id')
        set = Set.query.filter(staffId == Set.staffId).first()

        result_id = ['holiday-start-date-all-single', 'holiday-end-date-all-single', 'out-start-date-all-single',
                    'out-end-date-all-single']

        staff_holiday_start_date = set.beginHolidayDate.strftime('%Y-%m-%d')
        staff_holiday_end_date = set.endHolidayDate.strftime('%Y-%m-%d')
        staff_out_start_date = set.beginOutDate.strftime('%Y-%m-%d')
        staff_out_end_date = set.endOutDate.strftime('%Y-%m-%d')
        result_message = [staff_holiday_start_date, staff_holiday_end_date, staff_out_start_date, staff_out_end_date]

        options = dict(zip(result_id, result_message))

        return jsonify(options)
    else:
        return redirect(url_for('login.login'))


@login_required("<depAdmin_username>")
@depAdmin_bp.route('/<depAdmin_username>/get_message_attend_add_set_single', methods=['POST'],
                endpoint='get_message_attend_add_set_single')
def get_message_attend_add_set_single(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        data = request.get_json()
        staffId = data.get('staff_Id')
        set = Set.query.filter(staffId == Set.staffId).first()

        result_id = ['start-date-all-single', 'end-date-all-single', 'start-datetime-all-single',
                    'end-datetime-all-single', 'add-date-all-single', 'add-datetime-all-single']

        staff_attend_start_date = set.beginAttendDate.strftime('%Y-%m-%d')
        staff_attend_end_date = set.endAttendDate.strftime('%Y-%m-%d')
        staff_attend_start_datetime = set.attendTime.time().strftime('%H:%M:%S')
        staff_attend_end_datetime = set.endTime.time().strftime('%H:%M:%S')
        staff_add_start_date = set.beginAddTime.date().strftime('%Y-%m-%d')
        staff_add_start_datetime = set.beginAddTime.time().strftime('%H:%M:%S')
        result_message = [staff_attend_start_date, staff_attend_end_date, staff_attend_start_datetime,
                        staff_attend_end_datetime, staff_add_start_date, staff_add_start_datetime]

        options = dict(zip(result_id, result_message))

        return jsonify(options)
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/edit_holiday_out_set_single', methods=['POST'], endpoint='edit_holiday_out_set_single')
def edit_holiday_out_set_single(depAdmin_username):
    # 规定： 出差日期与休假日期的设置均只能从 修改设置的当天的第二天开始（不满足则弹窗警告）
    # 如果 休假与出差仅涉及 修改设置的当天一天，则手动修改当天 “今日考勤状态” 即可： 对当天的考勤记录进行更新 重新计算当天考勤记录的工作时长字段
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        # 获取表单数据
        holiday_start_date = request.form['holiday-start-date-all-single']
        holiday_end_date = request.form['holiday-end-date-all-single']
        out_start_date = request.form['out-start-date-all-single']
        out_end_date = request.form['out-end-date-all-single']
        staffId = request.form['staffId']

        # 设置多位用户的出差日期与休假日期的时候：不能存在日期重叠 !!!!!
        # 即：四个日期均存在的时候，保持 A起始 > B结束（BA） OR   B起始 > A结束（AB）
        # 且AB均满足各自 起始<=结束
        status = ''
        message = ''

        if holiday_start_date == '' or holiday_end_date == '':
            # 在休假日期不完备的条件下
            if out_start_date == '' or out_end_date == '':
                # 在出差日期也不完备的条件下
                status = 'error'
                message = '错误：休假的日期存在不完备！ +  出差的日期存在不完备！'
                return jsonify({'status': status, 'message': message})
            else:
                # 只满足出差日期的条件下
                if staffId is not None:

                    # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                    # 当前为单人
                    out_start_date = datetime.strptime(out_start_date, '%Y-%m-%d').date()
                    out_end_date = datetime.strptime(out_end_date, '%Y-%m-%d').date()

                    if out_start_date > out_end_date:
                        message = '设置的出差起始日期 应小于等于 出差结束日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    if out_start_date <= datetime.today().date():
                        message = '设置的出差起始日期 应大于 今天的日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    try:
                        set = Set.query.filter(staffId == Set.staffId).first()
                        # 写入出差起始/结束日期
                        set.beginOutDate = out_start_date
                        set.endOutDate = out_end_date
                        # 设置更新记录
                        set.updateTime = datetime.now()
                        set.updateId = depAdmin_username
                        db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '休假起始/结束日期不完备 + 出差起始/结束日期已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})
                else:
                    status = 'success'
                    # 这里使用success 方便重新更新界面去选中职工
                    # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                    message = '错误：不存在已经选中的职工'
                    return jsonify({'status': status, 'message': message})
        else:
            # 在休假日期完备的条件下
            if out_start_date == '' or out_end_date == '':
                # 但是出差日期不完备的条件下
                if staffId is not None:

                    # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                    holiday_start_date = datetime.strptime(holiday_start_date, '%Y-%m-%d').date()
                    holiday_end_date = datetime.strptime(holiday_end_date, '%Y-%m-%d').date()

                    if holiday_start_date > holiday_end_date:
                        message = '设置的休假起始日期 应小于等于 休假结束日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    if holiday_start_date <= datetime.today().date():
                        message = '设置的休假起始日期 应大于 今天的日期'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    try:
                        set = Set.query.filter(staffId == Set.staffId).first()

                        # 设置更新记录
                        set.updateTime = datetime.now()
                        set.updateId = depAdmin_username

                        set.beginHolidayDate = holiday_start_date
                        set.endHolidayDate = holiday_end_date

                        db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '出差日期数据不完备 +  休假日期数据已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})

                else:
                    status = 'success'
                    # 这里使用success 方便重新更新界面去选中职工
                    # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                    message = '错误：不存在已经选中的职工'
                    return jsonify({'status': status, 'message': message})
            else:
                # 出差日期与休假日期均完备的情况下
                # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                out_start_date = datetime.strptime(out_start_date, '%Y-%m-%d').date()
                out_end_date = datetime.strptime(out_end_date, '%Y-%m-%d').date()
                # 在进入for循环之前处理好数据格式的转化，防止在循环中重复处理导致数据类型错误
                holiday_start_date = datetime.strptime(holiday_start_date, '%Y-%m-%d').date()
                holiday_end_date = datetime.strptime(holiday_end_date, '%Y-%m-%d').date()
                if holiday_start_date > holiday_end_date or out_start_date > out_end_date:
                    message = '设置的休假起始日期 应小于等于 休假结束日期  +  设置的出差起始日期 应小于等于 出差结束日期'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})
                else:

                    if holiday_start_date <= datetime.today().date() or out_start_date <= datetime.today().date():
                        message = '设置的休假起始日期 应大于 今天的日期! + 设置的出差日期  应大于  今天的日期！'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    if holiday_start_date <= out_end_date and holiday_end_date >= out_start_date:
                        # 存在重叠日期的话
                        message = '！！！设置的休假起始日期 与 设置的出差起始日期 存在重叠日期！！！'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})
                    else:
                        # 不存在重叠日期的话，将这四个日期一起写入数据库
                        if staffId is not None:

                            try:
                                set = Set.query.filter(staffId == Set.staffId).first()

                                # 设置更新记录
                                set.updateTime = datetime.now()
                                set.updateId = depAdmin_username

                                # 写入休假起始/结束日期
                                set.beginHolidayDate = holiday_start_date
                                set.endHolidayDate = holiday_end_date
                                # 写入出差起始/结束日期
                                set.beginOutDate = out_start_date
                                set.endOutDate = out_end_date

                                db.session.commit()
                            except Exception as e:
                                message = '存储数据错误'.format(e)
                                status = 'error'
                                return jsonify({'status': status, 'message': message})

                            # 正常返回
                            message = '出差日期数据完备 +  休假日期数据完备 已经保存！完成SET的修改保存任务！'
                            status = 'success'
                            return jsonify({'status': status, 'message': message})

                        else:
                            status = 'success'
                            # 这里使用success 方便重新更新界面去选中职工
                            # 前端JS函数中规定： success刷新界面； error保留在modal弹窗界面
                            message = '错误：不存在已经选中的职工'
                            return jsonify({'status': status, 'message': message})
    else:
        return redirect(url_for('login.login'))


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/edit_attend_add_set_single', methods=['POST'], endpoint='edit_attend_add_set_single')
def edit_attend_add_set_single(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:

        # 获取表单数据
        attend_date_start = request.form['start-date-all-single']
        attend_date_end = request.form['end-date-all-single']
        attend_datetime_start = request.form['start-datetime-all-single']
        attend_datetime_end = request.form['end-datetime-all-single']
        add_date = request.form['add-date-all-single']
        add_datetime = request.form['add-datetime-all-single']
        staffId = request.form['staffId']

        if attend_datetime_start == '' or attend_datetime_end == '' or attend_date_start == '' or attend_date_end == '':
            # 考勤日期/时刻不完备的条件下：
            if add_date == '' or add_datetime == '':
                status = 'error'
                message = '错误：考勤的日期与时刻存在不完备！ +  加班的日期与时刻存在不完备'
                return jsonify({'status': status, 'message': message})
            else:
                # 加班的日期与时刻完备 / 考勤的日期与时刻不完备
                if staffId is not None:
                    # 如果有已经选中的职工
                    # 转换加班签到时间的数据格式(不应该出现在for循环里//// 此时修改单人/无循环)
                    add_date = datetime.strptime(add_date, '%Y-%m-%d').date()
                    add_datetime = datetime.combine(add_date, datetime.strptime(add_datetime, '%H:%M:%S').time())

                    if add_datetime <= datetime.now():
                        message = '设置的加班的具体时间 应大于 当前的具体时间'
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    try:
                        person_set = Set.query.filter(staffId == Set.staffId).first()
                        # 考勤时间不完备，故不设置

                        # 设置更新记录
                        person_set.updateTime = datetime.now()
                        person_set.updateId = depAdmin_username

                        # 更新加班应签到的具体日期时间
                        person_set.beginAddTime = add_datetime
                        db.session.commit()
                    except Exception as e:
                        message = '存储数据错误'.format(e)
                        status = 'error'
                        return jsonify({'status': status, 'message': message})

                    # 正常返回
                    message = '考勤日期与时刻不完备/加班日期与时刻已经保存！完成SET的修改保存任务！'
                    status = 'success'
                    return jsonify({'status': status, 'message': message})
                else:
                    message = '表单中传入职工信息有误，无法完成职工的考勤设置修改'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

        else:
            # 考勤日期/时刻完备 / 加班日期/时刻待定
            # 考勤起始/结束日期 格式转换
            attend_date_start = datetime.strptime(attend_date_start, '%Y-%m-%d').date()
            attend_date_end = datetime.strptime(attend_date_end, '%Y-%m-%d').date()
            if attend_date_start > attend_date_end:
                status = 'error'
                message = '错误：考勤结束日日期 不可大于 起始日期！'
                return jsonify({'status': status, 'message': message})
            if attend_date_start <= date.today():
                status = 'error'
                message = '错误：考勤起始日期 应大于 今日日期！'
                return jsonify({'status': status, 'message': message})

            # 考勤应签到时刻 格式转换
            attend_datetime_start = datetime.strptime(attend_datetime_start, '%H:%M:%S').time()
            attend_datetime_start = datetime.combine(date(1900, 1, 1), attend_datetime_start)
            # 考勤应签退时刻 格式转换
            attend_datetime_end = datetime.strptime(attend_datetime_end, '%H:%M:%S').time()
            attend_datetime_end = datetime.combine(date(1900, 1, 1), attend_datetime_end)
            if attend_datetime_start >= attend_datetime_end:
                status = 'error'
                message = '错误：考勤应签到时刻 应小于 考勤应签退时刻！'
                return jsonify({'status': status, 'message': message})

            # 转换加班签到时间的数据格式 (避免在for循环中转换格式，否则多人情况下一定产生数据类型错误)
            if add_date != '' and add_datetime != '':
                add_date = datetime.strptime(add_date, '%Y-%m-%d').date()
                add_datetime = datetime.combine(add_date, datetime.strptime(add_datetime, '%H:%M:%S').time())
                if add_datetime <= datetime.now():
                    message = '设置的加班的具体时间 应大于 当前的具体时间'
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

            # 写入考勤日期/时刻  %   判断加班日期/时刻是否完备
            if staffId is not None:
                # 如果职工信息无误
                status = ''
                message = ''
                try:
                    person_set = Set.query.filter(staffId == Set.staffId).first()
                    # 写入考勤时间
                    person_set.beginAttendDate = attend_date_start
                    person_set.endAttendDate = attend_date_end
                    person_set.attendTime = attend_datetime_start
                    person_set.endTime = attend_datetime_end

                    # 设置更新记录
                    person_set.updateTime = datetime.now()
                    person_set.updateId = depAdmin_username

                    # 检查是否设置了加班时间和日期
                    if add_date == '' or add_datetime == '':
                        # 未设置加班时间与日期，直接提交上述其他数据
                        db.session.commit()
                        # 正常返回
                        message = '考勤日期/时刻已经写入 + 未传入完备有效的加班时间/日期 + 完成SET的修改保存任务'
                        status = 'success'
                    else:
                        person_set.beginAddTime = add_datetime
                        db.session.commit()
                        # 正常返回
                        message = '考勤日期时刻已经写入 + 加班日期时刻已经写入 ！完成SET的修改保存任务！'
                        status = 'success'
                except Exception as e:
                    message = '存储数据错误'.format(e)
                    status = 'error'
                    return jsonify({'status': status, 'message': message})

                return jsonify({'status': status, 'message': message})
            else:
                message = '表单传入的职工信息有误 ,无法完成职工的考勤设置修改'
                status = 'error'
                return jsonify({'status': status, 'message': message})
    else:
        return redirect(url_for("login.login"))



