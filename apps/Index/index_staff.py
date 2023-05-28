from datetime import datetime

from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint

from apps.Index.__init__ import index_bp
from apps.models.check_model import Staff, Set, staffInformation, Departments, Position, Attendance
from exts import db
from form import EditPasswordForm


# 登录验证装饰器
def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'staff_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('<staff_username>')
@index_bp.route('/<staff_username>/staff_index', methods=["POST", "GET"], endpoint='staff_index')
def staff_index(staff_username):
    if session.get(staff_username+'staff_username') is not None:
        if request.method == 'GET':
            staff = Staff.query.filter_by(staffId=staff_username).first()
            staff_information = staffInformation.query.filter(staffInformation.staffId == staff_username).first()
            dep = Departments.query.filter(Departments.departmentId == staff_information.staffDepartmentId).first()
            staff_position = Position.query.filter(Position.positionId == staff_information.staffPositionId).first()
            image_filename = "static/data/data_headimage_staff/" + staff_username + '/head.jpg'
            form_editPassword = EditPasswordForm()
            edit_password = None
            if session.get(staff_username + 'edit_password') is not None:
                edit_password = session.get(staff_username + 'edit_password')
                session.pop(staff_username + 'edit_password')



            set = Set.query.filter(Set.staffId == staff_username).first()
            species_a = []
            species_a.append({'name':'出勤起止日期', 'beginDate':set.beginAttendDate, 'endDate':set.endAttendDate})
            species_a.append({'name':'休假起止日期', 'beginDate':set.beginHolidayDate, 'endDate':set.endHolidayDate})
            species_a.append({'name':'出差起止日期', 'beginDate':set.beginOutDate, 'endDate':set.endOutDate})

            if set.beginAddTime is not None:
                species_a.append({'name': '加班起始日期', 'beginDate': set.beginAddTime.date(), 'endDate':'仅限当天|无结束日期'})
            else:
                species_a.append({'name': '加班起始日期', 'beginDate': '暂无', 'endDate': '仅限当天|无结束日期'})

            species_b = []
            if set.attendTime  is not None:
                species_b.append({'name': '出勤起止时刻', 'begintime': set.attendTime.time(), 'endtime': set.endTime.time()})
            else:
                species_b.append(
                    {'name': '出勤起止时刻', 'begintime': '暂无', 'endtime': set.endTime.time()})
            species_b.append({'name': '休假起止时刻', 'begintime': '暂无', 'endtime': '暂无'})
            species_b.append({'name': '出差起止时刻', 'begintime': '暂无', 'endtime': '暂无'})
            if set.beginAddTime is not None:
                species_b.append({'name': '加班起始时刻', 'begintime': set.beginAddTime.time(), 'endtime':'不规定结束时刻'})
            else:
                species_b.append(
                    {'name': '加班起始时刻', 'begintime': '暂无', 'endtime': '不规定结束时刻'})



            attendances = Attendance.query.filter(Attendance.staffId == staff_username).all()
            attendance_data = []
            for attendance in attendances:
                staffId = staff_username
                staffName = staff_information.staffName
                attendanceId = attendance.attendanceId
                departmentName = dep.departmentName
                positionName = staff_position.positionName
                attendance_state = attendance.attendState
                attendance_date = attendance.attendDate
                attendance_editId = attendance.editId
                attendance_editTime = attendance.editTime
                attendance_outState = attendance.outState
                attendance_holidayState = attendance.holidayState
                attendance_data.append({'staffId': staffId, 'staffName': staffName, 'departmentName': departmentName,
                                        'attendanceId': attendanceId,
                                        'positionName': positionName, 'attendance_state': attendance_state,
                                        'attendance_date': attendance_date,
                                        'attendance_editId': attendance_editId,
                                        'attendance_editTime': attendance_editTime,
                                        'attendance_outState': attendance_outState,
                                        'attendance_holidayState': attendance_holidayState})


            return render_template('index/staff_index.html', attendances=attendance_data,staff_position=staff_position,dep=dep, staff_information=staff_information,staff=staff, url_image=image_filename,species_a=species_a, species_b=species_b,
                                   edit_password=edit_password,
                            form_password=form_editPassword)
    else:
        return redirect(url_for('login.login'))



@login_required('<staff_username>')
@index_bp.route('/<staff_username>/get_message', methods=['GET', 'POST'], endpoint='get_message')
def get_message_staff(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
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



@login_required('<staff_username>')
@index_bp.route('/<staff_username>/search_attendance', methods=['POST', 'GET'], endpoint='search_attendance')
def search_attendance_staff(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
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



@login_required('<staff_username>')
@index_bp.route('/<staff_username>/edit_password', methods=['POST', 'GET'], endpoint='edit_password')
def edit_password(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
        form = EditPasswordForm()
        if request.method == 'POST':

            previous_url = request.referrer
            if previous_url is None:
                previous_url = url_for('login.login')

            if form.validate_on_submit():
                staff = Staff.query.filter(staff_username == Staff.staffId).first()
                if staff.staffPassWord == form.staffPassword.data:
                    staff.staffPassWord = form.new_staffPassword2.data
                    db.session.commit()
                    session[staff_username + 'edit_password'] = '密码修改成功'
                else:
                    session[staff_username + 'edit_password'] = '原密码输入错误'
            else:
                session[staff_username + 'edit_password'] = '申请提交失败'
            return redirect(previous_url)
    else:
        return redirect(url_for('login.login'))




@login_required('<staff_username>')
@index_bp.route('/<staff_username>/open_box', methods=['POST', 'GET'], endpoint='open_box')
def open_box(staff_username):
    if session.get(staff_username + 'staff_username') is not None:
        staff = Staff.query.filter_by(staffId=staff_username).first()
        image_filename = "static/data/data_headimage_staff/" + staff_username + '/head.jpg'
        form_editPassword = EditPasswordForm()
        edit_password = None
        if session.get(staff_username + 'edit_password') is not None:
            edit_password = session.get(staff_username + 'edit_password')
            session.pop(staff_username + 'edit_password')


        return render_template('staff_all/box.html', staff=staff, url_image=image_filename,
                               edit_password=edit_password,
                               form_password=form_editPassword)
    else:
        return redirect(url_for('login.login'))