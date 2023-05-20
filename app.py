import time
import calendar
from datetime import datetime, time, timedelta

from flask import render_template, request, current_app
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from apps import create_app
from apps.models.check_model import Staff, attendanceAps, Set, Attendance, staffInformation, Sum, Works, Holidays, Outs
from exts import db
from flask_apscheduler import APScheduler

scheduler = APScheduler()

app = create_app(scheduler)
manager = Manager(app)

# 创建数据库的命令
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)








@scheduler.task('cron', id='attendance', hour=16, minute=17, second=25)
def execute_task():
    # 定时函数的逻辑
    with scheduler.app.app_context():
        set_all = Set.query.all()
        for set in set_all:
            attendance = Attendance()
            current_date = datetime.now().date()
            attendance.attendanceId = current_date.strftime('%Y-%m-%d') + set.staffId
            attendance.staffId = set.staffId
            current_date_year = datetime.now().date().strftime("%Y")
            current_date_month = datetime.now().date().strftime("%m")
            sum_Id = current_date_year + '-' + current_date_month + '-' + set.staffId
            sum = Sum.query.filter(sum_Id == Sum.sumId).first()
            staff_information = staffInformation.query.filter(set.staffId == staffInformation.staffId).first()

            # 在对休假日期与出差日期的设置中已经保证了其不会出现日期重叠
            # 如果休假/出差日期 与 正常出勤日期重叠， 则只执行休假/出差的情况即可
            # 休假/出差
            if set.endHolidayDate >= current_date >= set.beginHolidayDate:
                attendance.holidayState = True
                staff_information.staffCheckState = 12
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
                sum.holidayFrequency = sum.holidayFreqency + 1

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
                db.session.add(attendance)


            elif set.endOutDate >= current_date >= set.beginOutDate:
                # 出差
                attendance.outState = True
                staff_information.staffCheckState = 11
                # 设置出差状态
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

                # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                work = Works.query.filter(set.staffId == Works.staffId).first()
                if work.workTime is None:
                    work.workTime = float_time
                else:
                    work.workTime = work.workTime + float_time

                # 给年度出差总时长添加出差时长
                out = Outs.query.filter(Outs.staffId == set.staffId).first()
                if out.outTime is None:
                    out.outTime = float_time
                else:
                    out.outTime = out.outTime + float_time
                db.session.add(attendance)


            # 正常出勤
            elif set.endAttendDate >= current_date >= set.beginAttendDate:
                attendance.workTime = time(hour=0, minute=0, second=0)
                db.session.add(attendance)
                # 工作时长置零  等待签到

                # 设置签到/签退的函数， 在应签到时间后一个小时和应签退时间后一个小时 设置两个函数
                attendTime = set.attendTime.time()
                endTime = set.endTime.time()

                dt_attend = datetime.combine(datetime.min, attendTime)
                dt_plus_one_hour_attend = dt_attend + timedelta(hours=1)
                result_attend_time = dt_plus_one_hour_attend.time()
                result_attend_datetime = datetime.combine(current_date, result_attend_time)
                # A 函数执行时间  设置为签到时间之后的一个小时的时间点

                @scheduler.task(trigger='date', run_date=result_attend_datetime, args=[attendance.attendanceId], id=attendance.attendanceId+'attend')
                def execute_attend(attendanceId):
                    # 检测是否迟到
                    with scheduler.app.app_context():
                        attendance = Attendance.query.filter(attendanceId == Attendance.attendanceId).first()
                        staff = Staff.query.filter(attendance.staffId == Staff.staffId).first()
                        if attendance.attendState == 0:
                            attendance.attendState = 2
                            # 记录为迟到
                            staff_information = staffInformation.query.filter(
                                staffInformation.staffId == attendance.staffId).first()
                            staff_information.staffCheckState = 23
                            # 今日迟到（未出勤）

                            # 给本月的统计记录添加一次迟到
                            current_date_year = datetime.now().date().strftime("%Y")
                            current_date_month = datetime.now().date().strftime("%m")
                            sum_Id = current_date_year + '-' + current_date_month + '-' + staff.staffId
                            sum = Sum.query.filter(sum_Id == Sum.sumId).first()
                            # 迟到次数 + 1
                            sum.lateFrequency = sum.lateFrequency + 1

                            db.session.commit()

                dt_end = datetime.combine(datetime.min, endTime)
                dt_plus_one_hour_end = dt_end + timedelta(hours=1)
                result_end_time = dt_plus_one_hour_end.time()
                result_end_datetime = datetime.combine(current_date, result_end_time)
                # B函数执行时间 设置为签退时间之后的一个小时的时间点

                @scheduler.task(trigger='date', run_date=result_end_datetime, args=[attendance.attendanceId], id=attendance.attendanceId + "end")
                def execute_end(attendanceId):
                    with scheduler.app.app_context():
                        attendance = Attendance.query.filter(attendanceId == Attendance.attendanceId).first()
                        staff_information = staffInformation.query.filter(
                            staffInformation.staffId == attendance.staffId).first()
                        set = Set.query.filter(attendance.staffId == Set.staffId).first()
                        current_date_year = datetime.now().date().strftime("%Y")
                        current_date_month = datetime.now().date().strftime("%m")
                        sum_Id = current_date_year + '-' + current_date_month + '-' + staff_information.staffId
                        sum = Sum.query.filter(sum_Id == Sum.sumId).first()

                        # 在应签退时间+1小时这个时间点的定时函数上，职工状态不可能为 0；
                        # 只能为 1 出勤忘记签退  2 迟到    已经签到的做正常签退处理，未签到的做缺勤处理
                        # 4： 1的临时出门一直没回来； 5：2的临时出门一直没回来          做早退处理
                        # 对6（1完成考勤）的职工不做处理
                        # 7和3\8 就是自己这个定时函数生成的自然不需要判断

                        # 出勤 有签到（或者临时出门但是回来了）  没有签退， 做正常签退的工时计算
                        if attendance.attendState == 1:
                            set_end_time = set.endTime.time()
                            current_date = datetime.now().date()
                            dt1 = datetime.combine(current_date, set_end_time)
                            dt2 = datetime.combine(current_date, attendance.attendTime)
                            time_diff = dt1 - dt2
                            # 获取总秒数
                            total_seconds = time_diff.total_seconds()
                            # 计算时、分、秒的差异
                            hours = int(total_seconds // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            seconds = int(total_seconds % 60)
                            attendance.workTime = time(hours, minutes, seconds)

                            # 向staff_information中记录 考勤状态：
                            staff_information.staffCheckState = 14
                            attendance.attendState = 6

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
                            sum.attendFrequency  = sum.attendFrequency + 1

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time

                        # 2 迟到    已经签到的做正常签退处理，未签到的做缺勤处理
                        elif attendance.attendState == 2:
                            # 没有签到的迟到===缺勤处理
                            if attendance.attendTime is None:
                                attendance.workTime = time(0, 0, 0)
                                attendance.attendState = 8
                                staff_information.staffCheckState = 20
                                # 缺勤次数 + 1
                                sum.absenceFrequency = sum.absenceFrequency + 1
                                # 迟到次数 - 1
                                sum.lateFrequency = sum.lateFrequency - 1
                            # 迟到 但是 有签到时间 做正常签退处理
                            else:
                                set_end_time = set.endTime.time()
                                current_date = datetime.now().date()
                                dt1 = datetime.combine(current_date, set_end_time)
                                dt2 = datetime.combine(current_date, attendance.attendTime)
                                time_diff = dt1 - dt2
                                # 获取总秒数
                                total_seconds = time_diff.total_seconds()
                                # 计算时、分、秒的差异
                                hours = int(total_seconds // 3600)
                                minutes = int((total_seconds % 3600) // 60)
                                seconds = int(total_seconds % 60)
                                attendance.workTime = time(hours, minutes, seconds)

                                # 向staff_information中记录 考勤状态：
                                staff_information.staffCheckState = 26
                                attendance.attendState = 2
                                # 迟到的次数已经在前一个定时函数中完成对sum中的迟到次数加一操作了

                                # 将今天的工作时间存入本月工作时间记录
                                float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                                # 转换为以小时为整数的浮点数
                                float_time = round(float_time, 3)
                                # 保留3位小数

                                if sum.workSumTime is not None:
                                    sum.workSumTime = sum.workSumTime + float_time
                                else:
                                    sum.workSumTime = float_time

                                # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                                work = Works.query.filter(set.staffId == Works.staffId).first()
                                if work.workTime is None:
                                    work.workTime = float_time
                                else:
                                    work.workTime = work.workTime + float_time

                        # 正常签到之后，他又临时出门了 然后一直没回公司 按早退处理
                        elif attendance.attendState == 4:
                            sum.earlyFreqency = sum.earlyFrequency + 1
                            # 统计早退次数 + 1
                            attendance.attendState = 3
                            # 考勤记录状态设置为 正常签到的早退
                            staff_information.staffCheckState = 22
                            # 职工信息中的考勤状态为 正常签到早退
                            leave_end_time = attendance.leaveTime
                            # 取出临时离开的时间作为结束时间
                            current_date = datetime.now().date()
                            dt1 = datetime.combine(current_date, leave_end_time)
                            dt2 = datetime.combine(current_date, attendance.attendTime)
                            time_diff = dt1 - dt2
                            # 获取总秒数
                            total_seconds = time_diff.total_seconds()
                            # 计算时、分、秒的差异
                            hours = int(total_seconds // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            seconds = int(total_seconds % 60)
                            attendance.workTime = time(hours, minutes, seconds)

                            # 将今天的工作时间存入本月工作时间记录
                            float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                            # 转换为以小时为整数的浮点数
                            float_time = round(float_time, 3)
                            # 保留3位小数

                            if sum.workSumTime is not None:
                                sum.workSumTime = sum.workSumTime + float_time
                            else:
                                sum.workSumTime = float_time

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time

                        # 迟到签到之后，他又临时出门了，然后一直没回公司，按迟到|早退处理
                        elif attendance.attendState == 5:
                            sum.earlyFreqency = sum.earlyFrequency + 1
                            # 统计早退次数 + 1
                            attendance.attendState = 7
                            staff_information.staffCheckState = 24
                            # 状态为正常签到早退
                            leave_end_time = attendance.leaveTime
                            # 取出临时离开的时间作为结束时间
                            current_date = datetime.now().date()
                            dt1 = datetime.combine(current_date, leave_end_time)
                            dt2 = datetime.combine(current_date, attendance.attendTime)
                            time_diff = dt1 - dt2
                            # 获取总秒数
                            total_seconds = time_diff.total_seconds()
                            # 计算时、分、秒的差异
                            hours = int(total_seconds // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            seconds = int(total_seconds % 60)
                            attendance.workTime = time(hours, minutes, seconds)

                            # 将今天的工作时间存入本月工作时间记录
                            float_time = attendance.workTime.hour + attendance.workTime.minute / 60 + attendance.workTime.second / 3600
                            # 转换为以小时为整数的浮点数
                            float_time = round(float_time, 3)
                            # 保留3位小数

                            if sum.workSumTime is not None:
                                sum.workSumTime = sum.workSumTime + float_time
                            else:
                                sum.workSumTime = float_time

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time

                        # 保存数据库
                        db.session.commit()

        # 执行过exectue_task这个给每个用户每天添加考勤记录的定时函数后
        # 把执行时间存入数据库
        aps_function = attendanceAps.query.filter('attendance' == attendanceAps.attendanceApsId).first()
        if aps_function is None:
            aps_function = attendanceAps()
            aps_function.attendanceApsId = 'attendance'
            aps_function.execute_time = datetime.now()
            db.session.add(aps_function)
        else:
            aps_function.execute_time = datetime.now()


        jobs = scheduler.get_jobs()
        # 打印已添加的定时任务信息
        for job in jobs:
            print("Job ID:", job.id)
            print("Next execution time:", job.next_run_time)
            print("Trigger type:", job.trigger)
            print("---")

        # 数据库保存attendance、aps
        db.session.commit()


def has_executed_today(attendanceApsId):
    # 检查当天是否已经执行过定时函数的逻辑，例如查询数据库记录等
    # 返回 True 表示已执行过，返回 False 表示尚未执行过
    with scheduler.app.app_context():
        current_date = datetime.now().date()
        aps_function = attendanceAps.query.filter(
            attendanceApsId == attendanceAps.attendanceApsId).first()
        if aps_function is None:
            return False
        if current_date == aps_function.execute_time.date():
            return True
        else:
            return False

@manager.app.before_first_request
def check_and_execute_task():
    current_time = datetime.now().time()
    target_time = time(hour=13, minute=44)  # 固定时间为每天的 9:20 AM

    if current_time > target_time:
        # 检查当天是否已经执行过定时函数
        if not has_executed_today('attendance'):
            # 执行定时函数的逻辑
            execute_task()
        else:
            print('dddddddddddddddddddddd添加考勤记录的函数已经执行过了ddddddddddddddddddddddd')
    else:
        # 当前时间早于固定时间，跳过检测
        print('dddddddddddddddddddddd时间过早此时ddddddddddddddddddddddd')
        pass

@scheduler.task('cron', id='sum', hour=14, minute=19)
def check_and_sum_task():
    # 检测所有职工的本月的sum记录是否已经生成，如果没有则添加生成
    current_time = datetime.now()
    current_date_year = datetime.now().date().strftime("%Y")
    current_date_month = datetime.now().date().strftime("%m")
    with app.app_context():
        staff_all = Staff.query.all()
        for staff in staff_all:
            sum_Id = current_date_year + '-' + current_date_month + '-' + staff.staffId
            # 按照年/月/职工ID 生成一个独一无二的 sumID
            sum = Sum.query.filter(sum_Id == Sum.sumId).first()
            if sum is None:
                sum = Sum()
                sum.sumId = sum_Id
                sum.staffId = staff.staffId

                days_in_month = calendar.monthrange(current_time.year, current_time.month)[1]
                standardWorkTime = 8 * days_in_month
                sum.standardWorkSumTime = standardWorkTime
                # 设置本月统计记录中的本月标准的应出勤天数

                db.session.add(sum)
                db.session.commit()


if __name__ == '__main__':
    print(app.url_map)
    print(app.secret_key)
    manager.run()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error/404.html'), 404

# python app.py  (app.run())
# python app.py runserver -h host -p port (manager.run())


# 绑定命令到script
# exts
# |-- __init__py
#       |
#           db = SQLAlchemy()
#
# def create_app():
#     app = Flask(__name__)
#     db.init_app(app)
#
#
# migrate = Migrate(app=app, db=db)
# manager.add_command('命令名', MigrateCommand)
#

# 使用命令
# python app.py db init --------> 产生一个文件夹 migrations
#                                 此文件夹中存在versions 文件夹
#                                 用来保存各种更改

# python app.py db migrate --------> 在字段更改后，执行此命令产生一个新版py文件
# python app.py db upgrade --------> 让更改生效，执行新的py文件，但是会产生错误，
# 因为py文件中总为createtable而不是alter修改，所以会产生一个新的表
#
