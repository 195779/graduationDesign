from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField,  IntegerField, TextAreaField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, Length, ValidationError, InputRequired



class LoginForm(FlaskForm):
    username = StringField('userName', validators=[DataRequired(message=u'职工ID不能为空')])
    # DataRequired(message=None) 验证数据是否有效
    password = PasswordField('passWord', validators=[DataRequired(), Length(8, 128)])
    # Length(min=-1,max--1,message=None) 验证输入值的长度是否在给定范围内
    submit = SubmitField('登录')
    # SubmitField 提交按钮


class StaffForm(FlaskForm):
    staffName = StringField('职工姓名', validators=[DataRequired(), Length(1, 20)])
    staffImage = FileField('职工头像')
    staffGender = StringField('职工性别', validators=[DataRequired(), Length(1, 20)])
    staffHomeTown = StringField('职工籍贯', validators=[DataRequired(), Length(1, 20)])
    staffBirthday = StringField('职工出生日期', validators=[DataRequired()])
    staffPhoneNumber = StringField('职工联系方式', validators=[DataRequired(), Length(11, 11)])
    staffEmail = StringField('职工Email地址', validators=[DataRequired(), Length(1, 30)])
    staffAddress = TextAreaField('职工住址', validators=[DataRequired()])
    staffCountry = StringField('职工国籍')
    staffNation = StringField('职工民族')
    staffRemark = TextAreaField('备注信息')
    submit = SubmitField('提交')






