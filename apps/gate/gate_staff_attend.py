import base64
import os
import time

import cv2
import numpy as np
from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, Response, jsonify, \
    current_app, g

from apps.gate.__init__ import gate_bp
from apps.models.check_model import faceValue, gateAdmin, Staff
from PIL import Image, ImageDraw, ImageFont
import dlib


# 本次签到的所有人员信息
attend_records = []
# 本次签到的开启时间
the_now_time = ''
# 签到人员名字
staffName_first = None
staffName_last = None

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()
# Dlib 人脸 landmark 特征点检测器
predictor = dlib.shape_predictor('static/data_dlib/shape_predictor_68_face_landmarks.dat')

# Dlib Resnet 人脸识别模型，提取 128D 的特征矢量
face_reco_model = dlib.face_recognition_model_v1("static/data_dlib/dlib_face_recognition_resnet_model_v1.dat")


# 人脸识别类
class VideoCamera(object):
    def __init__(self):
        self.font = cv2.FONT_ITALIC
        # 通过opencv获取实时视频流
        self.video = cv2.VideoCapture(0)

        # 统计 FPS
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0

        # 统计帧数
        self.frame_cnt = 0

        # 用来存储所有录入人脸特征的数组
        self.features_known_list = []
        # 用来存储录入人脸名字
        self.name_known_list = []

        # 用来存储上一帧和当前帧 ROI 的质心坐标
        self.last_frame_centroid_list = []
        self.current_frame_centroid_list = []

        # 用来存储当前帧检测出目标的名字
        self.current_frame_name_list = []

        # 上一帧和当前帧中人脸数的计数器
        self.last_frame_faces_cnt = 0
        self.current_frame_face_cnt = 0

        # 用来存放进行识别时候对比的欧氏距离
        self.current_frame_face_X_e_distance_list = []

        # 存储当前摄像头中捕获到的所有人脸的坐标名字
        self.current_frame_face_position_list = []
        # 存储当前摄像头中捕获到的人脸特征
        self.current_frame_face_feature_list = []

        # 控制再识别的后续帧数
        # 如果识别出 "unknown" 的脸, 将在 reclassify_interval_cnt 计数到 reclassify_interval 后, 对于人脸进行重新识别
        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 10

    def __del__(self):
        self.video.release()

    # 从 allfeatures 读取录入人脸特征 / Get known faces from allfeatures
    def get_face_database(self, testId, all_featuers, all_Id):
        from_db_all_features = all_featuers
        from_db_all_id = all_Id


        if from_db_all_features and from_db_all_id:
            for from_db_one_features in from_db_all_features:
                someone_feature_str = str(from_db_one_features).split(',')
                # 从mysql取出的人脸特征向量（string类型）是以逗号分割的128个浮点数的形式，将其以逗号拆开存入list数组
                features_someone_arr = []
                # 用来存储该用户的人脸特征值向量（float类型）
                for one_feature in someone_feature_str:
                    if one_feature == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(float(one_feature))
                        # 单个特征值不为空，则转换回浮点类型
                self.features_known_list.append(features_someone_arr)
                # 存入该用户的特征向量（一个float类型的list）（顺序对应后面的人名）
            for from_db_one_Id in from_db_all_id:
                self.name_known_list.append(from_db_one_Id)
                # 存入人名
            # print("Faces in Database：", len(self.features_known_list))
            return 1
        else:
            return 0

    # 更新 FPS帧率 / Update FPS of video stream
    def update_fps(self):
        now = time.time()
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    # 计算两个128D向量间的欧式距离
    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist

    # 生成的 cv2 window 上面添加说明文字 / putText on cv2 window
    def draw_note(self, img_rd):
        # 添加说明 (Add some statements
        cv2.putText(img_rd, "Face Recognition ", (20, 40), self.font, 1, (0, 0, 255), 1,
                    cv2.LINE_AA)
        cv2.putText(img_rd, "Frames Per Second  " + str(self.fps.__round__(2)), (20, 100), self.font, 1.0,
                    (0, 255, 255), 1,
                    cv2.LINE_AA)
        # cv2.putText(img_rd, "Q: Quit", (20, 450), self.font, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

    def draw_name(self, img_rd):
        # 在人脸框下面写人脸名字
        # print(self.current_frame_name_list)
        font = ImageFont.truetype("simsun.ttc", 40)
        img = Image.fromarray(cv2.cvtColor(img_rd, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        draw.text(xy=self.current_frame_face_position_list[0], text=self.current_frame_name_list[0], font=font)
        img_rd = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img_rd

    # 处理获取的视频流，进行人脸识别
    # 进行人脸识别的方法
    def get_frame(self, testId, all_features, all_Id):
        staffName = None
        stream = self.video
        # 1. 读取存放所有人脸特征的 mysql / Get faces known from mysql
        # 从数据库中获取 拿到人脸特征
        if self.get_face_database(testId, all_features, all_Id):
            while stream.isOpened():
                self.frame_cnt += 1
                flag, img_rd = stream.read()
                # 2. 检测人脸 / Detect faces for frame X
                faces = detector(img_rd, 0)  # 人脸特征数组
                # 3. 更新帧中的人脸数 / Update cnt for faces in frames
                self.last_frame_faces_cnt = self.current_frame_face_cnt
                self.current_frame_face_cnt = len(faces)
                filename = 'attendacnce.txt'
                with open(filename, 'a') as file:
                    # 4.1 当前帧和上一帧相比没有发生人脸数变化 / If cnt not changes, 1->1 or 0->0
                    if self.current_frame_face_cnt == self.last_frame_faces_cnt:
                        if "unknown" in self.current_frame_name_list:
                            self.reclassify_interval_cnt += 1
                        # 4.1.1 当前帧一张人脸 / One face in this frame
                        if self.current_frame_face_cnt == 1:
                            if self.reclassify_interval_cnt == self.reclassify_interval:
                                self.reclassify_interval_cnt = 0
                                self.current_frame_face_feature_list = []
                                self.current_frame_face_X_e_distance_list = []
                                self.current_frame_name_list = []
                                for i in range(len(faces)):
                                    shape = predictor(img_rd, faces[i])
                                    self.current_frame_face_feature_list.append(
                                        face_reco_model.compute_face_descriptor(img_rd, shape))
                                # a. 遍历捕获到的图像中所有的人脸 / Traversal all the faces in the database
                                for k in range(len(faces)):
                                    self.current_frame_name_list.append("unknown")
                                    # b. 每个捕获人脸的名字坐标 / Positions of faces captured
                                    self.current_frame_face_position_list.append(tuple(
                                        [faces[k].left(),
                                         int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                                    # c. 对于某张人脸，遍历所有存储的人脸特征 / For every face detected, compare it with all the faces
                                    # in the database
                                    for i in range(len(self.features_known_list)):
                                        # 如果 person_X 数据不为空 / If the data of person_X is not empty
                                        if str(self.features_known_list[i][0]) != '0.0':
                                            e_distance_tmp = self.return_euclidean_distance(
                                                self.current_frame_face_feature_list[k],
                                                self.features_known_list[i])
                                            self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                        else:
                                            # 空数据 person_X / For empty data
                                            self.current_frame_face_X_e_distance_list.append(999999999)
                                    # d. 寻找出最小的欧式距离匹配 / Find the one with minimum e distance
                                    similar_person_num = self.current_frame_face_X_e_distance_list.index(
                                        min(self.current_frame_face_X_e_distance_list))
                                    if min(self.current_frame_face_X_e_distance_list) < 0.4:
                                        # 在这里更改显示的人名
                                        self.current_frame_name_list[k] = self.name_known_list[similar_person_num]
                                        now = time.strftime("%Y 年-%m 月-%d 日 %H:%M", time.localtime())
                                        mm = self.name_known_list[similar_person_num] + '  ' + now + '  已签到\n'
                                        file.write(self.name_known_list[similar_person_num] + '  ' + now + '     已签到\n')
                                        attend_records.append(mm)
                                        staffName = self.name_known_list[similar_person_num]
                                        global staffName_first
                                        staffName_first = staffName
                                    else:
                                        staffName = None
                                        pass
                            else:
                                # 获取特征框坐标 / Get ROI positions
                                for k, d in enumerate(faces):
                                    # 计算矩形框大小 / Compute the shape of ROI
                                    height = (d.bottom() - d.top())
                                    width = (d.right() - d.left())
                                    hh = int(height / 2)
                                    ww = int(width / 2)
                                    cv2.rectangle(img_rd,
                                                  tuple([d.left() - ww, d.top() - hh]),
                                                  tuple([d.right() + ww, d.bottom() + hh]),
                                                  (255, 255, 0), 2)
                                    self.current_frame_face_position_list[k] = tuple(
                                        [faces[k].left(),
                                         int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)])
                                    img_rd = self.draw_name(img_rd)
                    # 4.2 当前帧和上一帧相比发生人脸数变化
                    else:
                        self.current_frame_face_position_list = []
                        self.current_frame_face_X_e_distance_list = []
                        self.current_frame_face_feature_list = []
                        # 4.2.1 人脸数从 0->1 / Face cnt 0->1
                        if self.current_frame_face_cnt == 1:
                            self.current_frame_name_list = []
                            for i in range(len(faces)):
                                shape = predictor(img_rd, faces[i])
                                self.current_frame_face_feature_list.append(
                                    face_reco_model.compute_face_descriptor(img_rd, shape))
                            # a. 遍历捕获到的图像中所有的人脸
                            for k in range(len(faces)):
                                self.current_frame_name_list.append("unknown")
                                # b. 每个捕获人脸的名字坐标
                                self.current_frame_face_position_list.append(tuple(
                                    [faces[k].left(),
                                     int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                                # c. 对于某张人脸，遍历所有存储的人脸特征
                                for i in range(len(self.features_known_list)):
                                    # 如果 person_X 数据不为空 / If data of person_X is not empty
                                    if str(self.features_known_list[i][0]) != '0.0':
                                        e_distance_tmp = self.return_euclidean_distance(
                                            self.current_frame_face_feature_list[k],
                                            self.features_known_list[i])
                                        self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                    else:
                                        # 空数据 person_X
                                        self.current_frame_face_X_e_distance_list.append(999999999)
                                # d. 寻找出最小的欧式距离匹配
                                similar_person_num = self.current_frame_face_X_e_distance_list.index(
                                    min(self.current_frame_face_X_e_distance_list))
                                if min(self.current_frame_face_X_e_distance_list) < 0.4:
                                    # 在这里更改显示的人名
                                    self.current_frame_name_list[k] = self.name_known_list[similar_person_num]
                                    now = time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())
                                    mm = self.name_known_list[similar_person_num] + '  ' + now + '  已签到\n'
                                    file.write(self.name_known_list[similar_person_num] + '  ' + now + '  已签到\n')
                                    staffName = self.name_known_list[similar_person_num]
                                    attend_records.append(mm)
                                    staffName_first = staffName
                                else:
                                    pass
                            if "unknown" in self.current_frame_name_list:
                                self.reclassify_interval_cnt += 1
                        # 4.2.1 人脸数从 1->0 / Face cnt 1->0
                        elif self.current_frame_face_cnt == 0:
                            self.reclassify_interval_cnt = 0
                            self.current_frame_name_list = []
                            self.current_frame_face_feature_list = []
                            staffName = None
                # 5. 生成的窗口添加说明文字 / Add note on cv2 window
                self.draw_note(img_rd)
                self.update_fps()
                ret, jpeg = cv2.imencode('.jpg', img_rd)
                return [jpeg.tobytes(), time.localtime(), staffName]


def gen(camera, testId, all_featurs, all_Id):
    while True:
        return_list = camera.get_frame(testId, all_featurs, all_Id)
        frame = return_list[0]
        staffId = return_list[2]
        time = return_list[1]
        if staffId:
            print(staffId+"ddddddddddddddddddddddddddddd")
        # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
        # print(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# 人脸识别view函数（视图函数）
@gate_bp.route('/video_feed', endpoint="video_feed")
def video_feed():
    all_faces = faceValue.query.all()

    all_features = []
    all_Id = []

    for one_face in all_faces:
        all_Id.append(one_face.staffId)
        all_features.append(one_face.staffFaceValue)

    return Response(gen(VideoCamera(), '001', all_features, all_Id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# 实时显示当前签到人员
@gate_bp.route('/now_attend')
def now_attend():
    if attend_records:
        for records in attend_records:
            print(records)
    global staffName_last
    if staffName_last is None or staffName_last != staffName_first:
        staffName_last = staffName_first
        print("此时新来的签到人员为：" + str(staffName_first))
    return jsonify(attend_records)


# 开启签到
@gate_bp.route('/staff_attend', methods=["POST", 'GET'], endpoint='staff_attend')
def staff_attend():
    # 开启签到后，开始单次的记录
    global attend_records
    attend_records = []
    now = time.strftime("%Y-%m-%d %H:00:00", time.localtime())
    session['now_time'] = now
    gate_admin = gateAdmin.query.filter(gateAdmin.gateAdminId == session.get('username')).first()
    return render_template("gate_admin_all/staff_attend.html", gateAdmin=gate_admin)


# 停止签到
@gate_bp.route('/stop_records', methods=['POST'], endpoint='stop_records')
def stop_records():
    return redirect(url_for('index.gate_admin_index'))
