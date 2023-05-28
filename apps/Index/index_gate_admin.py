from datetime import datetime, timedelta

from flask import render_template, request, session, redirect, url_for, jsonify
from flask import Blueprint
from sqlalchemy import func, or_, Integer, case

from apps.Index.__init__ import index_bp
from apps.models.check_model import gateAdmin, Attendance, Staff, Sum
from exts import db


def login_required(route_part):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if route_part + 'gateAdmin_username' in session:
                return func(*args, **kwargs)
            else:
                return redirect(url_for('login.login'))

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.route_part = route_part
        return wrapper

    return decorator


@login_required('gateAdmin_username')
@index_bp.route('/<gateAdmin_username>/gate_index', methods=["POST", "GET"], endpoint='gate_admin_index')
def department_admin_index(gateAdmin_username):
    if session.get(gateAdmin_username+'gateAdmin_username') is not None:
        if request.method == 'GET':
            username = gateAdmin_username
            gate_admin = gateAdmin.query.filter_by(gateAdminId=username).first()
            return render_template('index/gate_index.html', gateAdmin=gate_admin)
        else:
            return "not post now"
    else:
        return redirect(url_for('login.login'))




@login_required('<gateAdmin_username>')
@index_bp.route('/<gateAdmin_username>/open_box_gate', methods=['POST', 'GET'], endpoint='open_box_gate')
def open_box_admin(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:

        username = gateAdmin_username
        gate_admin = gateAdmin.query.filter_by(gateAdminId=username).first()

        return render_template('gate_admin_all/box.html', gateAdmin=gate_admin )
    else:
        return redirect(url_for('login.login'))


@login_required('gateAdmin_username')
@index_bp.route('<gateAdmin_username>/get_message_today_staff_gate', methods=['POST', 'GET'],
                endpoint='get_message_today_staff_gate')
def get_message_today_staff_gate(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:

        # 统计创造日期为今天且attendState字段等于指定数值的记录数量
        today = datetime.now().date()
        attend_specified_state = [1, 4, 6]
        attend_record_count = db.session.query(func.count(Attendance.attendanceId))\
            .filter(func.DATE(Attendance.attendDate) == today, Attendance.attendState.in_(attend_specified_state)).scalar()

        absence_specified_state = [2, 5, 7, 8, 9]
        absence_record_count = db.session.query(func.count(Attendance.attendanceId)) \
            .filter(func.DATE(Attendance.attendDate) == today,
                    Attendance.attendState.in_(absence_specified_state)).scalar()

        staffnumber = 0
        staffs = Staff.query.all()
        for staff in staffs:
            if staff.staffState:
                staffnumber = staffnumber + 1

        out_holiday_record_count = db.session.query(func.count(Attendance.attendanceId)) \
            .filter(func.DATE(Attendance.attendDate) == today,
                    or_(Attendance.outState == True, Attendance.holidayState == True)).scalar()


        status = 'success'
        return jsonify(
            {'status': status, 'staff_number': staffnumber, 'staff_absence': absence_record_count , 'staff_attend': attend_record_count, 'staff_out_holiday':out_holiday_record_count})
    else:
        return redirect(url_for('login.login'))




@login_required('gateAdmin_username')
@index_bp.route('<gateAdmin_username>/get_month_data_a_gate', methods=['POST', 'GET'], endpoint='get_month_data_a_gate')
def get_month_data_a(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:

        attend_data = [0] * 12
        absence_data = [0] * 12
        holiday_data = [0] * 12
        out_data = [0] * 12

        attend = db.session.query(
            func.substring(Sum.sumId, 6, 2).label('month'),
            func.cast(func.sum(Sum.attendFrequency), Integer).label('total_frequency')
        ).group_by(
            func.substring(Sum.sumId, 6, 2)
        ).order_by(
            func.substring(Sum.sumId, 6, 2)
        ).all()
        absence = db.session.query(
            func.substring(Sum.sumId, 6, 2).label('month'),
            func.cast(func.sum(Sum.absenceFrequency), Integer).label('total_frequency')
        ).group_by(
            func.substring(Sum.sumId, 6, 2)
        ).order_by(
            func.substring(Sum.sumId, 6, 2)
        ).all()
        holiday = db.session.query(
            func.substring(Sum.sumId, 6, 2).label('month'),
            func.cast(func.sum(Sum.holidayFrequency), Integer).label('total_frequency')
        ).group_by(
            func.substring(Sum.sumId, 6, 2)
        ).order_by(
            func.substring(Sum.sumId, 6, 2)
        ).all()
        out = db.session.query(
            func.substring(Sum.sumId, 6, 2).label('month'),
            func.cast(func.sum(Sum.outFrequency), Integer).label('total_frequency')
        ).group_by(
            func.substring(Sum.sumId, 6, 2)
        ).order_by(
            func.substring(Sum.sumId, 6, 2)
        ).all()

        for row in attend:
            month = int(row.month)
            total_frequency = int(row.total_frequency)
            attend_data[month - 1] = total_frequency  # 由于索引从 0 开始，所以需要将月份减 1

        for row in absence:
            month = int(row.month)
            total_frequency = int(row.total_frequency)
            absence_data[month - 1] = total_frequency  # 由于索引从 0 开始，所以需要将月份减 1

        for row in out:
            month = int(row.month)
            total_frequency = int(row.total_frequency)
            out_data[month - 1] = total_frequency  # 由于索引从 0 开始，所以需要将月份减 1

        for row in holiday:
            month = int(row.month)
            total_frequency = int(row.total_frequency)
            holiday_data[month - 1] = total_frequency  # 由于索引从 0 开始，所以需要将月份减 1

        status = 'success'
        return jsonify(
            {'status': status, 'attend_data': attend_data, 'absence_data': absence_data, 'out_data': out_data,
             'holiday_data': holiday_data})
    else:
        return redirect(url_for('login.login'))


@login_required('gateAdmin_username')
@index_bp.route('<gateAdmin_username>/get_week_data_a_gate', methods=['POST', 'GET'], endpoint='get_week_data_a_gate')
def get_week_data_a_gate(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:

        attend_data = [0] * 7
        absence_data = [0] * 7
        holiday_data = [0] * 7
        out_data = [0] * 7

        # 获取当前日期
        today = datetime.now().date() + timedelta(days=1)
        # 计算一周前的日期
        week_ago = today - timedelta(days=7)
        # 初始化日期数据列表
        date_data = []
        # 遍历日期范围
        current_date = week_ago
        while current_date < today:
            # 提取月份和日期，并连接成字符串形式
            formatted_date = current_date.strftime("%m-%d")
            # 将字符串形式的日期添加到列表中
            date_data.append(formatted_date)
            # 增加一天，继续下一个日期
            current_date += timedelta(days=1)

        attend_absence_query = db.session.query(
            func.date(Attendance.attendDate).label('date'),
            func.sum(case([(Attendance.attendState == 6, Attendance.attendState)], else_=0)
                     ).label('attend_sum'),
            func.sum(case([(Attendance.attendState == 8, Attendance.attendState)], else_=0)
                     ).label('absence_sum'),
            func.sum(func.cast(Attendance.outState, Integer)).label('out_sum'),
            func.sum(func.cast(Attendance.holidayState, Integer)).label('holiday_sum')
        ).filter(
            Attendance.attendDate >= week_ago,
            Attendance.attendDate <= today
        ).group_by(
            func.date(Attendance.attendDate)
        ).all()

        for row in attend_absence_query:
            date_index = (row.date - week_ago).days
            attend_data[date_index] = int(row.attend_sum) // 6
            absence_data[date_index] = int(row.absence_sum) // 8
            out_data[date_index] = int(row.out_sum)
            holiday_data[date_index] = int(row.holiday_sum)

        status = 'success'
        return jsonify(
            {'status': status, 'attend_data': attend_data, 'absence_data': absence_data, 'out_data': out_data,
             'holiday_data': holiday_data, 'date_data': date_data})
    else:
        return redirect(url_for('login.login'))

