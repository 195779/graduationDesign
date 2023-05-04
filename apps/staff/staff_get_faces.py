import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort
from apps.staff.__init__ import staff_bp
from apps.models.check_model import Staff, faceValue, staffInformation
from apps import get_faces_from_camera
from apps import features_extraction
from exts import db
from form import EditPasswordForm


def pre_work_mkdir(path_photos_from_camera):
    # 新建文件夹
    if os.path.isdir(path_photos_from_camera):
        pass
    else:
        print(path_photos_from_camera)
        os.mkdir(path_photos_from_camera)


@staff_bp.route('/get_faces', methods=['POST', 'GET'], endpoint='staff_get_faces')
def get_faces():
    '''
        功能:接收前端上传来的人脸图片,完成数据库的保存
        1、取上传来的数据的参数 request.form.get("myimg")
        2、上传的数据是base64格式,调用后端的base64进行解码
        3、存到后台变成图片
        4、调用face_reconginition的load_image-file读取文件
        5、调用 face-recognition的face_encodings对脸部进行编码
        6、利用bson和pickle模块组合把脸部编码数据变成128位bitdata数据
        7、利用mongo.db.myface.insert_one插入数据,存储到mongodb里面
        上面是逻辑,但逻辑发生在post方式上,不发生在get,
        限定一下上面逻辑的发生条件,不是POST方式,就是GET,GET请求页面
        :return:
    '''
    if session.get('username') is None or session.get('num') is None:
        abort(404)
    form_editPassword = EditPasswordForm()
    username = session.get('username')
    staff = Staff.query.filter_by(staffId=username).first()
    staff_information = staffInformation.query.filter_by(staffId=session.get('username')).first()
    image_filename = "static/data/data_headimage_staff/" + username + '/head.jpg'
    if request.method == "POST":
        imgdata = request.form.get("face")
        print(imgdata)
        print('xxxxxxxxxx')
        imgdata = base64.b64decode(imgdata)
        path = "static/data/data_faces_from_camera/" + session.get('username')
        up = get_faces_from_camera.Face_Register()
        if session['num'] == 0:
            pre_work_mkdir(path)
        if session['num'] == 7:
            session['num'] = 0
        session['num'] += 1
        current_face_path = path + "/" + str(session['num']) + '.jpg'
        with open(current_face_path, "wb") as f:
            f.write(imgdata)
        flag = up.single_pocess(current_face_path)
        # 进行上传图片的正确姿势
        if flag != 'right':
            session['num'] -= 1
        print(flag, session['num'])
        return {"result": flag, "code": session['num']}

    return render_template("staff_all/get_faces.html", staff=staff, form_password=form_editPassword,
                        staff_information=staff_information, url_image=image_filename)


@staff_bp.route('/upload_faces', methods=['POST', 'GET'], endpoint='staff_upload_faces')
def upload_faces():
    if session.get('username') is None:
        abort(404)
    try:
        path_images_from_camera = "static/data/data_faces_from_camera/"
        path = path_images_from_camera + session.get('username')
        print(path)
        features_mean_personX = features_extraction.return_features_mean_personX(path)
        features = str(features_mean_personX[0])
        for i in range(1, 128):
            # range(1,128) 遍历 1-127的全部数字 i  加上前面已经加入的 0 ，
            # 将128维的特征向量（128个浮点数）全部从float类型转换为字符串类型，并用逗号隔开
            features = features + ',' + str(features_mean_personX[i])
        face = faceValue.query.filter(faceValue.staffId == session.get('username')).first()
        if face:
            face.staffFaceValue = features
            # 如果存在则更新
        else:
            # 不存在则添加
            face = faceValue(staffId=session.get('username'), staffFaceValue=features)
            db.session.add(face)
        db.session.commit()
        # print(" >> 特征均值 / The mean of features:", list(features_mean_personX), '\n')
        staff_information = staffInformation.query.filter(staffInformation.staffId == session.get('username')).first()
        staff_information.faceValueState = True
        # 更改人脸信息录入的状态
        db.session.commit()
        flash("提交成功！")
        return redirect(url_for('index.staff_index'))
    except Exception as e:
        print('Error:', e)
        flash("提交不合格照片，请拍摄合格后再重试")
        return redirect(url_for('index.staff_index'))


@staff_bp.route('/delete_faces', methods=['POST'], endpoint='delete_faces')
def delete_face():
    # 驳回重录
    staffId = request.form.get('staffId')
    staff_information = staffInformation.query.filter(staffInformation.staffId == staffId).first()
    face_value = faceValue.query.filter(faceValue.staffId == staffId).first()
    face_value.staffFaceValue = None
    staff_information.faceValueState = False
    db.session.commit()
    os.remove('static/data/data_faces_from_camera/' + staffId + '/1.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/2.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/3.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/4.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/5.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/6.jpg')
    os.remove('static/data/data_faces_from_camera/' + staffId + '/7.jpg')

    return redirect(url_for('staff_all.staff_get_faces'))