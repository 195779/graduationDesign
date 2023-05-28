from datetime import datetime

from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint
from apps.Index.__init__ import index_bp
from apps.models.check_model import departmentAdmin, Departments, Staff, staffInformation, Attendance, Position


def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'depAdmin_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('<depAdmin_username')
@index_bp.route('/<depAdmin_username>/departmentAdmin_index', methods=["POST", "GET"], endpoint='department_admin_index')
def department_admin_index(depAdmin_username):
    if session.get(depAdmin_username+'depAdmin_username') is not None:
        if request.method == 'GET':
            username = depAdmin_username
            depAdmin = departmentAdmin.query.filter_by(departmentAdminId=username).first()
            department = Departments.query.filter(depAdmin.admin_departmentId == Departments.departmentId).first()
            attendances = []
            staff_informations = staffInformation.query.filter(staffInformation.staffDepartmentId == department.departmentId).all()
            department = Departments.query.filter(Departments.departmentId == department.departmentId).first()
            for staff_information in staff_informations:
                attendances_staff = Attendance.query.filter(Attendance.staffId == staff_information.staffId).all()
                for attendance_staff in attendances_staff:
                    attendances.append(attendance_staff)

            attendance_data = []
            for attendance in attendances:
                staffId = attendance.staffId
                staff_information = staffInformation.query.filter(staffInformation.staffId == staffId).first()
                position = Position.query.filter(staff_information.staffPositionId == Position.positionId).first()

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
                                        'attendance_date': attendance_date,
                                        'attendance_editId': attendance_editId,
                                        'attendance_editTime': attendance_editTime,
                                        'attendance_outState': attendance_outState,
                                        'attendance_holidayState': attendance_holidayState})

            return render_template('index/departmentAdmin_index.html', departmentAdmin=depAdmin, dep=department, attendances=attendance_data)
        else:
            return "not post now"
    else:
        return redirect(url_for('login.login'))



@login_required('<depAdmin_username>')
@index_bp.route('/<depAdmin_username>/search_attendance_dep', methods=['POST', 'GET'], endpoint='search_attendance_dep')
def search_attendance_dep(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        message = request.json
        departmentId = str(message.get('departmentId'))
        departmentId = '00' + departmentId
        state = message.get('state')
        start_date = message.get('beginDate')
        end_date = message.get('endDate')

        staff_informations = staffInformation.query.filter(staffInformation.staffDepartmentId == departmentId).all()
        department = Departments.query.filter(Departments.departmentId == departmentId).first()

        attendance_data = []
        attendances = []
        message_return = ''

        if start_date == '' or end_date == '':
            message_return = message_return + '存在至少一个时间为空，当前查询结果未按时间检索'

            if state == '*':
                message_return = message_return + ' | 未选择检索类型，当前查询结果包含全部考勤状态'
                for staff_information in staff_informations:
                    attendances_staff = Attendance.query.filter(Attendance.staffId == staff_information.staffId).all()
                    for attendance_staff in attendances_staff:
                        attendances.append(attendance_staff)
            else:

                for staff_information in staff_informations:
                    attendances_staff = Attendance.query.filter(Attendance.attendState == int(state),
                                                                Attendance.staffId == staff_information.staffId).all()
                    for attendance_staff in attendances_staff:
                        attendances.append(attendance_staff)

        else:
            beginDate = datetime.strptime(start_date, '%Y-%m-%d')
            endDate = datetime.strptime(end_date, '%Y-%m-%d')
            if beginDate > endDate:
                status = 'error'
                message_return = message_return + '查询的起始日期大于结束时间： 错误！'
                return jsonify({'status': status, 'message': message_return, 'data': attendance_data})
            elif state == '*':

                message_return = message_return + ' | 未选择检索类型，当前查询结果包含全部考勤状态'
                for staff_information in staff_informations:
                    attendances_staff = Attendance.query.filter(Attendance.attendDate.between(beginDate, endDate),
                                                                Attendance.staffId == staff_information.staffId).all()
                    for attendance_staff in attendances_staff:
                        attendances.append(attendance_staff)

            else:

                for staff_information in staff_informations:
                    attendances_staff = Attendance.query.filter(Attendance.attendDate.between(beginDate, endDate),
                                                                Attendance.attendState == int(state),
                                                                Attendance.staffId == staff_information.staffId).all()
                    for attendance_staff in attendances_staff:
                        attendances.append(attendance_staff)

        if attendances:
            status = 'success'
            message_return = message_return + '已经获取到指定条件下的考勤记录'
            for attendance in attendances:
                staffId = attendance.staffId
                staff_information = staffInformation.query.filter(staffInformation.staffId == staffId).first()
                position = Position.query.filter(staff_information.staffPositionId == Position.positionId).first()

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
@index_bp.route('/<depAdmin_username>/get_message_dep', methods=['GET', 'POST'], endpoint='get_message_dep')
def get_message_dep(depAdmin_username):
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
@index_bp.route('/<depAdmin_username>/open_box_dep', methods=['POST', 'GET'], endpoint='open_box_dep')
def open_box(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
        username = depAdmin_username
        depAdmin = departmentAdmin.query.filter_by(departmentAdminId=username).first()
        department = Departments.query.filter(depAdmin.admin_departmentId == Departments.departmentId).first()


        return render_template('dep_all/box.html', dep=department, departmentAdmin=depAdmin)
    else:
        return redirect(url_for('login.login'))