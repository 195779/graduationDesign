import os

from flask import render_template, request, session, redirect, url_for, jsonify

from apps.Index.index_department_admin import login_required
from apps.dep.__init__ import depAdmin_bp
from apps.models.check_model import Departments, Position, staffInformation, Adds, Staff, faceValue, Set, Outs, Works, departmentAdmin, Holidays
from exts import db


@login_required('<depAdmin_username>')
@depAdmin_bp.route("/<depAdmin_username>/<departmentId>", methods=['POST', "GET"], endpoint='dep_staff_manage')
def dep_staff_manage(depAdmin_username, departmentId):
    if session.get(depAdmin_username+'depAdmin_username') is not None:
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
    else:
        return redirect(url_for('login.login'))



@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/get_message', methods=['GET', 'POST'], endpoint='get_message')
def get_message(depAdmin_username):
    if session.get(depAdmin_username + 'depAdmin_username') is not None:
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


@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/<staff_username>/staff_records', methods=['POST', 'GET'], endpoint='staff_records')
def staff_records(depAdmin_username, staff_username):
    if session.get(depAdmin_username+'depAdmin_username') is not None:
        return "the render_template is ..."
    else:
        return redirect(url_for('login.login'))



@login_required('<depAdmin_username>')
@depAdmin_bp.route('/<depAdmin_username>/selectPersons', methods=['POST', 'GET'], endpoint='selectPersons')
def selectPersons(depAdmin_username):
    selected_persons = request.json
    if session.get(depAdmin_username+'depAdmin_username') is not None:
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
    attend_date_start = request.form['start-date-all']
    attend_date_end = request.form['end-date-all']
    attend_datetime_start = request.form['start-datetime-all']
    attend_datetime_end = request.form['end-datetime-all']

    add_date = request.form['add-date-all']
    add_datetime = request.form['add-datetime-all']

    return jsonify({'message': 'test!!!!!!!!!'})
