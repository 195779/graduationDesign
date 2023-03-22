from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField('userName', validators=[DataRequired()])
    # DataRequired(message=None) 验证数据是否有效
    password = PasswordField('passWord', validators=[DataRequired(), Length(8, 128)])
    # Length(min=-1,max--1,message=None) 验证输入值的长度是否在给定范围内
    submit = SubmitField('登录')
    # SubmitField 提交按钮
