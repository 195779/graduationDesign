from datetime import datetime, date, time

from sqlalchemy import text

from exts import db


class Admin(db.Model):
    # 系统管理员登录
    __table_name__ = "admin"
    adminId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, comment="系统管理员ID、主键、不为空、不重复")
    adminPassWord = db.Column(db.String(20), server_default=text("'123456'"), comment='系统管理员密码 不允许为空')
    loginTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='上次登录时间')

    # id + password 完成登录（布置验证码的事情待办）
    # 全部使用String类型，字符长度不允许超过20

    def __str__(self):
        return self.adminId + "'s ID"


class Staff(db.Model):
    # 职工登录
    __table_name__ = "staff"
    staffId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, comment='职工ID 主键、不允许为空、不重复')
    staffPassWord = db.Column(db.String(20), server_default=text("'123456'"), comment='职工密码 不为空')
    loginTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='上次登录时间')
    staffState = db.Column(db.Boolean, server_default='1', comment='就职状态（默认设置为在职TRUE） 不为空')

    # id + password 完成登录（布置验证码的事情待办）

    # 1对1关系中uselist设置为false
    staff_information = db.relationship("staffInformation", backref='staff', uselist=False)
    # 职工登录ID--职工信息 1对1 两个外键：ID、State
    staff_face_value = db.relationship('faceValue', backref='staff', uselist=False)
    # 职工登录ID--职工人脸信息 1对1 一个外键：ID
    staff_set = db.relationship('Set', backref='staff', uselist=False)
    # 职工登录ID--职工考勤/请假/出差/加班设置 1对1关系 一个外键：ID
    staff_attendance = db.relationship('Attendance', backref='staff', lazy='dynamic')
    # 职工登录ID--职工考勤记录（每天每个职工一条） 1对N关系 一个外键：ID
    staff_add_record = db.relationship('OvertimeRecord', backref='staff', lazy='dynamic')
    # 职工登录ID--职工加班记录 1对N关系，一个外键：ID
    staff_work = db.relationship("Works", backref='staff', uselist=False)
    # 职工登录ID--职工工作状态 1对1关系 一个外键：ID
    staff_holiday = db.relationship("Holidays", backref='staff', uselist=False)
    # 职工登录ID--职工休假状态（每个职工始终对应一条假期信息） 1对1关系 一个外键：ID
    staff_add = db.relationship("Adds", backref='staff', uselist=False)
    # 职工登录ID--职工加班状态 1对1关系 一个外键：ID
    staff_out = db.relationship("Outs", backref='staff', uselist=False)
    # 职工登录ID--职工出差状态 1对1关系， 一个外键：ID
    staff_sum = db.relationship("Sum", backref='staff', lazy='dynamic')
    # 职工登录ID--综合统计记录 1对N关系 一个外键：ID
    staff_apply = db.relationship("systemApply", backref='staff', lazy='dynamic')
    # 职工登录ID--职工留言记录 1对N关系 一个外键：ID
    staff_holiday_apply = db.relationship("holidayApply", backref='staff', lazy='dynamic')
    # 职工登录ID--职工申请休假记录 1对N关系 一个外键：ID

    def __str__(self):
        return self.staffId + "'s staffID"

class Position(db.Model):
    __table_name = 'position'
    positionId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, comment='岗位ID')
    positionName = db.Column(db.String(20), unique=True, comment='岗位名称')
    positionLevel = db.Column(db.Integer, comment='岗位等级')

    position_staff_informations = db.relationship('staffInformation', backref='position', lazy='dynamic')
    # 岗位---职工信息 1对多

    def __str__(self):
        return self.positonId + "'s positionID"


class Departments(db.Model):
    __tablename__ = 'departments'
    departmentId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, comment='部门ID/主键/不为空/不重复')
    departmentName = db.Column(db.String(20), nullable=False, comment='部门名称')

    departments_staff_informations = db.relationship('staffInformation', backref='departments', lazy='dynamic')
    # 部门---职工信息 1对多
    departments_departmentAdmin = db.relationship('departmentAdmin', backref='departments', lazy='dynamic')
    # 部门---部门管理员 1 对 多

    def __str__(self):
        return self.departmentId + "'s departmentID"


class departmentAdmin(db.Model):
    # 部门管理员登录
    __tale_name__ = "department_admin"
    departmentAdminId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True)
    departmentAdminPassWord = db.Column(db.String(20), server_default=text("'123456'"))
    admin_departmentId = db.Column(db.String(20), db.ForeignKey('departments.departmentId', onupdate='CASCADE'),
                        comment="部门ID，外键")
    loginTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    # id + password 完成登录（布置验证码的事情待办）
    # 全部使用String类型，字符长度不允许超过20

    def __str__(self):
        return self.departmentAdminId + "'s departmentAdminID"


class gateAdmin(db.Model):
    # 闸机管理员登录
    __tale_name__ = "department_admin"
    gateAdminId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True)
    gateAdminPassWord = db.Column(db.String(20), server_default=text("'123456'"))
    loginTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # id + password 完成登录（布置验证码的事情待办）
    # 全部使用String类型，字符长度不允许超过20

    def __str__(self):
        return self.gateAdminId + "'s gateAdminID"





class staffInformation(db.Model):
    # 职工信息
    __table_name__ = 'staff_information'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, nullable=False, unique=True,
                        comment="职工ID，外键、主键、不为空、不重复")
    staffName = db.Column(db.String(20), server_default=text("'未命名'"), comment='姓名 不允许为空')
    staffGetFaceState = db.Column(db.Boolean, server_default='0', comment='职工录入人脸图片权限')
    staffGender = db.Column(db.String(20), server_default=text("'性别未知'"),
                            comment=' 性别 不允许为空 设置String字符串，')
    staffCountry = db.Column(db.String(20), nullable=True, comment='国籍')
    staffNation = db.Column(db.String(20), nullable=True, comment='民族')
    staffOrigin = db.Column(db.String(20), nullable=True, comment='籍贯')
    staffBirthday = db.Column(db.Date(), nullable=True, comment='出生日期')
    staffPhoneNumber = db.Column(db.String(11), nullable=True, comment='手机号')
    staffEmailAddress = db.Column(db.String(30), nullable=True, comment='邮箱地址')
    staffState = db.Column(db.Boolean,  server_default='1', comment='在职状态 不允许为空')
    staffPositionId = db.Column(db.String(20), db.ForeignKey('position.positionId', onupdate='CASCADE'), nullable=False, comment='岗位ID')
    staffDepartmentId = db.Column(db.String(20), db.ForeignKey('departments.departmentId', onupdate='CASCADE'), nullable=False, comment='部门ID')
    staff_create_updateDate = db.Column(db.DateTime(), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='信息创建时间/更新时间')
    staff_create_updateId = db.Column(db.String(20), nullable=True, comment='创建/更新ID')
    informationState = db.Column(db.Boolean,  server_default='0', comment='职工信息完善状态')
    faceValueState = db.Column(db.Boolean, server_default='0', comment='职工人脸信息完善状态')
    staffAddress = db.Column(db.Text, comment='家庭住址')
    staffCheckState = db.Column(db.Integer, server_default=text('0'), nullable=True, comment='今日尚未出勤：0  出勤：{今日出勤（工作中）：10  今日出勤（临时外出）16 , 今日出差：11 ,  今日休假： 12  ,'
                                                                                            ' 加班出勤（工作中）： 13 ,  今日出勤（已完成工作） 14  加班出勤（已完成工作）15 } ; '
                                                    '  缺勤：{今日缺勤：20 , 今日迟到（工作中）：21 ;  今日出勤|早退：22; 今日迟到（未出勤）23  今日迟到|早退 24  今日迟到（临时外出）25  今日迟到（已完成工作）26  ' 
                                                    ' 今日加班缺勤：30  ;  今日加班迟到（工作中）：31  ; 今日加班迟到（未出勤）32 ;  }')
    staff_Remark = db.Column(db.Text, comment="备注/Text任意长度字符类型")

    def __str__(self):
        return self.staffId + "'s information"


class faceValue(db.Model):
    __table_name__ = 'face_value'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, nullable=False, unique=True,
                        comment='职工ID 外键、主键、非空、不重复')
    staffFaceValue = db.Column(db.Text, comment='人脸特征向量/Text任意长度字符类型')

    def __str__(self):
        return self.staffId + "'s FaceValue"


class Set(db.Model):
    __table_name__ = 'set'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, nullable=False, unique=True,
                        comment='职工ID 外键、主键、非空、不重复')

    attendTime = db.Column(db.DateTime, default=datetime(1900, 1, 1, 0, 0, 0),
                           comment='应签到时间+1900-1-1')
    endTime = db.Column(db.DateTime, default=datetime(1900, 1, 1, 0, 0, 0),
                        comment='应签退时间+1900-1-1')
    beginAttendDate = db.Column(db.Date(), default=date(1900, 1, 1), comment='考勤起始日期')
    endAttendDate = db.Column(db.Date(), default=date(1900, 1, 1), comment='考勤结束日期')

    holidayState = db.Column(db.Boolean,  server_default='0', comment='请假状态/默认没有请假FALSE/不能为空')
    beginHolidayDate = db.Column(db.Date(), comment='请假起始日期')
    endHolidayDate = db.Column(db.Date(), comment='请假结束日期')
    outState = db.Column(db.Boolean,   server_default='0', comment='出差状态/默认没有出差FALSE/不能为空')
    beginOutDate = db.Column(db.Date(), comment='出差起始日期')
    endOutDate = db.Column(db.Date(), comment='出差结束日期')
    addState = db.Column(db.Boolean,   server_default='0', comment='加班状态/默认没有加班FALSE/不能为空')
    beginAddTime = db.Column(db.DateTime, comment='加班起始具体时间（年月日时分秒）/ 不设置结束时间，以结束后打卡时间为准')
    updateTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='设置更新时间')
    updateId = db.Column(db.String(20), nullable=True, comment='更新者id')

    def __str__(self):
        return self.staffId + "'s Set"


class Attendance(db.Model):
    __table_name__ = 'attendance'
    attendanceId = db.Column(db.String(50), primary_key=True, unique=True, nullable=False,
                            comment='出勤记录ID/主键/不重复/不为空/！！以当天Date日期+职工ID合成String作为出勤记录ID存入！！')
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), unique=False, nullable=False,
                        comment='职工ID/外键/允许重复（1对多）/不为空')
    attendTime = db.Column(db.Time(), comment='签到打卡时间')
    endTime = db.Column(db.Time(), comment='签退打卡时间')
    leaveTime = db.Column(db.Time(), comment='临时离开的时间')
    workTime = db.Column(db.Time(), comment='工作时间')
    editId = db.Column(db.String(20), comment='上次修改者ID/在生成考勤记录的定时函数中将此ID赋予一个默认值')
    editTime = db.Column(db.DateTime(), comment='上次保存数据库的时间')
    attendDate = db.Column(db.DateTime(), server_default=text('CURRENT_TIMESTAMP'), comment='记录日期')
    attendImage = db.Column(db.LargeBinary(65536), nullable=True, comment='签到拍照打卡截图')
    endImage = db.Column(db.LargeBinary(65536), nullable=True, comment='签退拍照打卡截图')
    attendState = db.Column(db.Integer, server_default=text('0'), comment='签到状态/默认为0未打卡/不为空/出勤1/迟到2/缺勤3')
    endState = db.Column(db.Integer, server_default=text('0'), comment='签退状态/默认为0未打卡/不为空/早退2/晚签退3')
    outState = db.Column(db.Boolean, server_default='0',
                        comment='出差状态/不设置为外键/每次生成每天的出勤记录之前检查set表的个人状态,如果出差，在此记录状态，工作时间设置八小时，其余空白/出差总时长相应增加/出差次数+1')
    holidayState = db.Column(db.Boolean, server_default='0',
                            comment='请假状态/不设置为外键/每次生成每天的出勤记录之前检查set表的个人状态 如果请假，在此记录状态，工作时间设置0，其余空白，请假次数+1/假期剩余总时长对应相减/')

    def __str__(self):
        return self.attendanceId + ' is  the ' + self.staffId + "in the attendance's date which is " + str(self.attendDate)


class Works(db.Model):
    __table_name__ = 'works'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, unique=True, nullable=False,
                        comment='职工ID/外键/主键/不重复/不为空')
    workState = db.Column(db.Integer, server_default=text('0'),  comment='工作状态')
    workTime = db.Column(db.Float, server_default=text('0.0'),  comment='工作总时长')

    def __str__(self):
        return self.staffId + " is : " + str(self.workState) + "in WorkState"


class Holidays(db.Model):
    __table_name__ = 'holidays'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, unique=True, nullable=False,
                        comment='职工ID/外键/主键/不重复/不为空')
    holidayState = db.Column(db.Boolean, server_default='0', comment='休假状态')
    holidayTime = db.Column(db.Float, server_default=text('0.0'), comment='剩余假期总时长')

    def __str__(self):
        return self.staffId + ' is : ' + str(self.holidayState) + "in holidayState"


class Adds(db.Model):
    __table_name__ = 'adds'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, nullable=False, unique=True,
                        comment='职工ID/主键/外键/不为空/不重复')
    addState = db.Column(db.Boolean, server_default='0', comment='加班状态')
    addTime = db.Column(db.Float, server_default=text('0.0'), comment='加班总时长')

    def __str__(self):
        return self.staffId + "is : " + str(self.addState) + "in addState"


class Outs(db.Model):
    __table_name__ = 'outs'
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), primary_key=True, nullable=False, unique=True,
                        comment='职工ID/主键/外键/不重复/不为空')
    outState = db.Column(db.Boolean, server_default='0', comment='职工出差状态')
    outTime = db.Column(db.Float, server_default=text('0.0'), comment='职工出差总时长')

    def __str__(self):
        return self.staffId + "is : " + str(self.outState) + "in outState"


class OvertimeRecord(db.Model):
    __table_name__ = 'overtime_record'
    addId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True,
                      comment='加班记录/主键/不为空/不重复')
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId',  onupdate='CASCADE'), nullable=False, comment='职工ID/主键/外键/不为空')
    beginAddTime = db.Column(db.DateTime, nullable=True, comment='加班签到时间')
    endAddTime = db.Column(db.DateTime, nullable=True, comment='加班签退时间')
    workTime = db.Column(db.Float, nullable=True, comment='加班工作时间')
    addDate = db.Column(db.Date(), nullable=True, comment='加班记录日期')
    beginAddImage = db.Column(db.LargeBinary(65536), nullable=True, comment='加班签到拍照')
    endAddImage = db.Column(db.LargeBinary(65536), nullable=True, comment='加班签退拍照')
    attendState = db.Column(db.Integer,  server_default=text('0'), comment='加班签到状态')
    endState = db.Column(db.Integer,  server_default=text('0'), comment='加班签退状态')

    def __str__(self):
        return self.staffId + "is one of the overtime_records' ID"


class Sum(db.Model):
    __table_name__ = 'sum'
    sumId = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, comment='统计ID/主键/不为空/不重复')
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), nullable=False,
                        comment='职工ID/外键/不为空')
    holidayFrequency = db.Column(db.Integer, server_default=text('0'),  comment='休假次数')
    attendFrequency = db.Column(db.Integer, server_default=text('0'),  comment='出勤次数')
    lateFrequency = db.Column(db.Integer, server_default=text('0'),  comment='迟到次数')
    earlyFrequency = db.Column(db.Integer, server_default=text('0'),  comment='早退次数')
    absenceFrequency = db.Column(db.Integer, server_default=text('0'),  comment='缺勤次数')
    addFrequency = db.Column(db.Integer, server_default=text('0'),  comment='加班次数')
    outFrequency = db.Column(db.Integer, server_default=text('0'),  comment='出差次数')
    addSumTime = db.Column(db.Float, server_default=text('0.0'),  comment='加班总时长')
    outSumTime = db.Column(db.Float, server_default=text('0.0'),  comment='出差总时长')
    workSumTime = db.Column(db.Float, server_default=text('0.0'),  comment='工作时长')
    standardWorkSumTime = db.Column(db.Float, server_default=text('0.0'),  comment='标准工作时长')

    def __str__(self):
        return self.sumId + "is one of the sum's ID"


class systemApply(db.Model):
    __table_name = 'system_apply'
    applyId = db.Column(db.String(20), primary_key=True, unique=True, nullable=False,
                        comment='留言记录ID/主键/不为空/不重复')
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), nullable=False, comment='职工ID/外键/不为空')
    applyMessage = db.Column(db.Text, nullable=True, comment='留言信息')
    replyMessage = db.Column(db.Text, nullable=True, comment='回复内容')
    applyTime = db.Column(db.DateTime,  server_default=text('CURRENT_TIMESTAMP'), comment='留言时间')
    replyTime = db.Column(db.DateTime, nullable=True, comment='回复时间')
    replyId = db.Column(db.String(20), nullable=True, comment='回复者ID')

    def __str__(self):
        return self.applyId + "is one of the apply's ID"


class holidayApply(db.Model):
    __table_name__ = 'holiday_apply'
    applyId = db.Column(db.String(20), primary_key=True, unique=True, nullable=False,
                        comment='请假记录ID/主键/不为空/不重复')
    staffId = db.Column(db.String(20), db.ForeignKey('staff.staffId', onupdate='CASCADE'), nullable=False, comment='职工ID/外键/不为空')
    applyMessage = db.Column(db.Text, nullable=True, comment='申请信息')
    replyMessage = db.Column(db.Text, nullable=True, comment='批复内容')
    applyTime = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='申请时间')
    replyTime = db.Column(db.DateTime, nullable=True, comment='批复时间')
    replyId = db.Column(db.String(20), nullable=True, comment='批复者ID')
    beginApplyDate = db.Column(db.Date(), nullable=True, comment='申请假期开始时间')
    endApplyDate = db.Column(db.Date(), nullable=True, comment='申请假期结束时间')

    def __str__(self):
        return self.applyId + "is one of the holidayApplyId"


class systemAnnouncement(db.Model):
    __table_name__ = 'system_announcement'
    announcementId = db.Column(db.String(20), nullable=False, unique=True, primary_key=True,
                               comment='公告记录ID/主键/不为空/不重复')
    publishId = db.Column(db.String(20), nullable=True, comment='发布者ID')
    publishTime = db.Column(db.DateTime, nullable=True, comment='发布时间')
    publishMessage = db.Column(db.Text, nullable=True, comment='发布内容')

    def __str__(self):
        return self.publishId + "is one of the systemAnnouncementId"


class attendanceAps(db.Model):
    _table_name = 'attendance_aps'
    attendanceApsId = db.Column(db.String(20), nullable=False, unique=True, primary_key=True,
                                comment='APS 函数ID/主键/非空/唯一值')
    execute_time = db.Column(db.DateTime, nullable=True, comment='上一次执行时间')

