import base64
import os
import time
from datetime import datetime, timedelta, time as datetime_time

import cv2
import numpy as np
from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, Response, jsonify, \
    current_app, g
from apps.Index.index_gate_admin import login_required
from apps.gate.__init__ import gate_bp
from apps.models.check_model import faceValue, gateAdmin, Staff, staffInformation, Set, Works, Sum, Holidays, Adds, Attendance
from PIL import Image, ImageDraw, ImageFont
import dlib

from exts import db

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
        # OpenCV的VideoCapture类初始化了一个视频捕获对象，以访问默认摄像头设备（索引为0）。
        # 参数0表示要访问的摄像头设备的索引。在这种情况下，0表示第一个可用的摄像头设备。
        # 如果你的系统连接了多个摄像头，你可以根据需要更改索引值以访问不同的摄像头设备。
        # 例如，cv2.VideoCapture(1)将访问第二个摄像头设备

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

        print("执行get_database函数")
        if from_db_all_features and from_db_all_id:
            if len(self.features_known_list) == len(from_db_all_features) and len(self.name_known_list) == len(from_db_all_id):
                return 1
            else:
                for from_db_one_features in from_db_all_features:
                    someone_feature_str = str(from_db_one_features).split(',')
                    # 从mysql取出的人脸特征向量（string类型）是以逗号分割的128个浮点数的形式，将其以逗号拆开存入list数组
                    features_someone_arr = []
                    # 用来存储该用户的人脸特征值向量（float类型）
                    for one_feature in someone_feature_str:
                        if one_feature == '':
                            features_someone_arr.append(0.0)
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
        # 使用stream变量来读取摄像头捕获的图像帧，并对其进行处理

        if self.get_face_database(testId, all_features, all_Id):
            # 这里的get函数不再直接从数据库取数据，而是直接使用已经传入的参数，
            # 其中featuers为职工人脸特征值的list，id为职工ID的list且互相对应
            # get函数内部将特征值的list做了处理，将字符串类型的list修改为float类型的list
            while stream.isOpened():
                # 用于检查视频流是否处于打开状态。如果视频流打开，循环体中的代码将被执行；
                # 如果视频流关闭或发生错误，循环将终止。
                # 应该在适当的时候通过调用stream.release()来释放资源，并确保关闭视频流。
                self.frame_cnt += 1
                # 统计帧数 + 1
                flag, img_rd = stream.read()
                # stream.read()用于从视频流中读取一帧图像。
                # 返回值是一个元组，包含两个部分：
                # flag是一个布尔值，表示是否成功读取到图像。如果成功读取到图像，flag为True；否则，flag为False。
                # img_rd是一个表示读取到的图像帧的NumPy数组。

                # 2. 检测人脸
                faces = detector(img_rd, 0)  # 人脸特征数组（实际上是该图中全部人脸的list，一个人脸数据放一个子元素）

                # 3. 更新帧中的人脸数
                self.last_frame_faces_cnt = self.current_frame_face_cnt
                # 保存上一张图像的人脸数量到last_cnt

                self.current_frame_face_cnt = len(faces)
                if self.current_frame_face_cnt != 0:
                    print('此时在get_frame函数内，获取当前帧图像的人脸数量不为0： ', self.current_frame_face_cnt)
                # current_cnt 进行更新 被重新设置为此时图像中的人脸数量

                filename = 'attendacnce.txt'
                with open(filename, 'a') as file:
                    # filename 是要打开的文件的路径和名称。
                    # 'a' 是打开文件的模式参数，表示以追加（append）模式打开文件。在追加模式下，如果文件不存在，将会创建新文件；如果文件已存在，则新的内容将被追加到文件的末尾。
                    # as file 将文件对象赋值给变量 file，使得你可以通过该变量来引用和操作打开的文件对象。
                    # with 语句是一种上下文管理器，它会在代码块执行完毕后自动关闭文件，无需显式调用 file.close()。
                    # 当代码块执行完毕或发生异常时，文件将自动关闭，确保资源的正确释放。
                    # 你可以使用 file 变量来调用文件对象的方法，例如 file.write() 将数据写入文件。

                    # 4.1 当前帧和上一帧相比没有发生人脸 数目 变化 / If cnt not changes, 1->1 or 0->0
                    if self.current_frame_face_cnt == self.last_frame_faces_cnt:

                        if "unknown" in self.current_frame_name_list:
                            self.reclassify_interval_cnt += 1
                            print('前一帧未能识别到人脸，且此时新一帧无人脸数目变化，即仍未能识别到已知的人脸，计数加1之后为： ',
                                self.reclassify_interval_cnt)

                            # 如果unknown 存在于 c_f_n_list， 则将r_i_cnt + 1
                            # 当 r_i_cnt 加到 10 的时候 ？？

                        # 4.1.1 当前图像中只有一张人脸图像 / One face in this frame
                        if self.current_frame_face_cnt == 1:
                            if self.reclassify_interval_cnt == self.reclassify_interval:
                                # 默认的r_i == 10 , 当r_i_cnt 被加到10 的时候 执行此if下的语句们

                                # 即 ！！若当前时间区间内，每一帧始终保持 1 -> 1 的人脸图像数目不变，！！

                                # 则在每10帧之后计算一次当前帧的人脸特征值
                                self.reclassify_interval_cnt = 0
                                # 让 r_i_cnt 清零
                                self.current_frame_face_feature_list = []
                                # 将存储前一帧图像的特征值清空（当前为1->1 未识别出人脸）
                                self.current_frame_face_X_e_distance_list = []
                                # 将欧式距离值清空
                                self.current_frame_name_list = []
                                # 将上一帧的图像的人脸姓名清空

                                for i in range(len(faces)):
                                    # 此时其实只执行了一次循环，因为当前图像中只有一张人脸图像
                                    shape = predictor(img_rd, faces[i])
                                    self.current_frame_face_feature_list.append(
                                        face_reco_model.compute_face_descriptor(img_rd, shape))
                                    # 存储当前帧的人脸特征值

                                # a. 遍历捕获到的图像中所有的人脸
                                for k in range(len(faces)):
                                    # 此时其实只执行了一次循环，因为当前图像中只有一张人脸图像

                                    self.current_frame_name_list.append("unknown")
                                    # 先默认给当前帧人脸图像的名字设置为unknown

                                    # b. 每个捕获人脸的名字坐标（为了之后在显示的时候在人脸的下方显示出人名）
                                    self.current_frame_face_position_list.append(tuple(
                                        [faces[k].left(),
                                        int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)]))
                                    # 这行代码的作用是将当前帧中检测到的人脸的位置信息（左侧 x 坐标和稍微调整后的底部 y 坐标）
                                    # 作为一个元组添加到列表中

                                    # c. 对于某张人脸，遍历所有数据库中存储的人脸特征
                                    for i in range(len(self.features_known_list)):
                                        # 如果 person_X 数据不为空
                                        if str(self.features_known_list[i][0]) != '0.0':
                                            # 要打断点看features_known_list的具体结构，勿忘，切切
                                            e_distance_tmp = self.return_euclidean_distance(
                                                self.current_frame_face_feature_list[k],
                                                self.features_known_list[i])
                                            self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                            # 计算欧式距离并存储，所存到的list, 与 数据库特征值/人名ID的list 的顺序一一对应（也是因为当前只有一张人脸）
                                        else:
                                            # 空数据 person_X / For empty data
                                            self.current_frame_face_X_e_distance_list.append(999999999)

                                    # d. 寻找出最小的欧式距离匹配
                                    similar_person_num = self.current_frame_face_X_e_distance_list.index(
                                        min(self.current_frame_face_X_e_distance_list))

                                    if min(self.current_frame_face_X_e_distance_list) < 0.4:
                                        # 在这里更改显示的人名
                                        self.current_frame_name_list[k] = self.name_known_list[similar_person_num]
                                        now = time.strftime("%Y 年-%m 月-%d 日 %H:%M", time.localtime())
                                        mm = self.name_known_list[similar_person_num] + '  ' + now + '  已签到\n'
                                        print('人脸从1 到 1： ', mm)
                                        file.write(self.name_known_list[similar_person_num] + '  ' + now + '     已签到\n')
                                        attend_records.append(mm)
                                        staffName = self.name_known_list[similar_person_num]
                                        global staffName_first
                                        # 将函数外部定义的staffName_first 设置为全局变量
                                        staffName_first = staffName
                                        # 每次识别到一个姓名之后，firstName就更新一次
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
                                    print('！！此时绘制了矩形框！！')
                                    img_rd = self.draw_name(img_rd)
                    # 4.2 当前帧和上一帧相比发生人脸的 数目 变化
                    else:
                        self.current_frame_face_position_list = []
                        self.current_frame_face_X_e_distance_list = []
                        self.current_frame_face_feature_list = []
                        # 4.2.1 人脸数从 0->1
                        if self.current_frame_face_cnt == 1:
                            print('！！！ 此时人脸数量从0 到 1  ！！！')
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
                                    print('人脸从0到1： ', mm)
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
                # 5. 生成的窗口添加说明文字
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
@login_required('gateAdmin_username')
@gate_bp.route('<gateAdmin_username>/video_feed', endpoint="video_feed")
def video_feed(gateAdmin_username):
    if session.get(gateAdmin_username+'gateAdmin_username') is not None:
        all_faces = faceValue.query.all()

        all_features = []
        all_Id = []

        for one_face in all_faces:
            if one_face.staffFaceValue is not None:
                # 将已经录入人脸并生成特征值，则特征值不为空的记录 加入该列表list
                # 防止出现因新添加的职工未录入人脸特征值而导致的无法正确打开人脸签到识别界面的情况
                all_Id.append(one_face.staffId)
                all_features.append(one_face.staffFaceValue)

        return Response(gen(VideoCamera(), '001', all_features, all_Id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return redirect(url_for('login.login'))

# 实时显示当前签到人员
@login_required('gateAdmin_username')
@gate_bp.route('<gateAdmin_username>/now_attend')
def now_attend(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:
        # if attend_records:
        # for records in attend_records:
        # print(records)
        global staffName_last
        if staffName_last is None or staffName_last != staffName_first:
            # A 用户签到成功后，如果一直在这刷脸签到（1-1的情况）则 此 if 不执行

            staffName_last = staffName_first
            print("此时新来的签到人员为：" + str(staffName_first))
            if staffName_first:
                # 在这里，可以对已经识别到的 Name(ID) 进行 处理
                # 如果一个用户一直在摄像头前晃荡，只记录他签到时间（即每次从 0 - 1 的时候如果识别到的人名更新了则进行数据库处理）
                staff_information = staffInformation.query.filter(staffName_first == staffInformation.staffId).first()
                set = Set.query.filter(staffName_first == Set.staffId).first()
                current_date = datetime.now().date()
                current_datetime = datetime.now()
                attendanceId = current_date.strftime('%Y-%m-%d') + set.staffId
                attendance = Attendance.query.filter(attendanceId == Attendance.attendanceId).first()
                current_date_year = datetime.now().date().strftime("%Y")
                current_date_month = datetime.now().date().strftime("%m")
                sum_Id = current_date_year + '-' + current_date_month + '-' + set.staffId
                sum = Sum.query.filter(sum_Id == Sum.sumId).first()
                # 当前时间要与 set 时间做比较
                # 当前日期要与 set 日期做比较
                # 要找到该职工 在当前日期的 考勤记录
                # 向此考勤记录中更新/填写数据
                # 要向Works工作表更新数据
                # 要向information表更新出勤状态数据
                # 如果是休假/出差状态（Holidays 和 Outs） ： 要提醒现在非正常出勤时间

                # 如果是加班状态：
                # 要找到当前日期的加班记录，要更新/填写数据
                # 要向ADD表更新数据
                # 要向information表更新数据
                if attendance is None:
                    attend_records.append('ERROR！ 此时新来到的签到人员为：'+ str(staffName_first) + '！！没有今天的考勤记录！！')
                    print('ERROR！ 此时新来到的签到人员为：'+ str(staffName_first) + '！！没有今天的考勤记录！！')
                else:
                    # 是否出差
                    if attendance.outState and staff_information.staffCheckState == 11:
                        string_return = 'ERROR！ 此时 ' + time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime()) + ' 新来到的签到人员为：' + str(staffName_first) + '！！今天为出差状态！！'
                        attend_records.append(string_return)
                        print(string_return)
                    # 是否休假
                    elif attendance.holidayState and staff_information.staffCheckState == 12:
                        string_return = 'ERROR！ 此时 ' + time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime()) + ' 新来到的签到人员为：' + str(staffName_first) + '！！今天为休假状态！！'
                        attend_records.append(string_return)
                        print(string_return)

                    # 非休假/出差状态的情况下 如果当天日期 介于正常考勤的日期之内
                    elif set.beginAttendDate <= current_date <= set.endAttendDate:

                        # 定时函数的处理：
                        # 在 begin + 1 处已经设置好定时函数检测 如有状态 0 的职工，则改为 状态2 迟到
                        # 在 end + 1   处已经设置好定时函数检测 如有状态 1 的职工，则此职工正常出勤忘记了签退                 设置为6 完成出勤 按应签退时间计算工时
                        #    end + 1                          如有状态 2 的职工，如果已经签到 则此职工迟到且忘记了签退       设置为2  迟到    按应签退时间计算工时
                        #                                                       如果没有签到 则此职工今日缺勤              设置为8  今日缺勤 缺勤次数+1
                        #    end + 1                          如有状态 4 的职工，则正常出勤+临时出门+在end+1之前一直没回来   设置为3  早退    按离开时间计算工时
                        #    end + 1                          如有状态 5 的职工，则早上迟到+临时出门+在end+1之前一直没回来   设置为7  迟到    按离开时间计算工时

                        # 状态流转：
                        # 在 0      begin-1  < time < begin+1                            / 签到状态改为 1   正常出勤     记录签到时间
                        # 在 2      time > begin+1  且签到时间为空                        / 签到状态已经在定时函数中改为2  已经迟到   在此要记录迟到的签到时间
                        # 在 1      time < end-1                                         / 签到状态改为 4   临时出门      记录离开时间
                        # 在 1      end-1 < time < end+1                                 / 签到状态改为 6   完成出勤      记录签退时间/记录工作时长
                        # 在 1      time > end+1                                         / 签到状态已经在定时函数里改为6  给用户显示一下默认完成签退
                        # 在 4      time < end+1 则在应签退后一小时内回来了                / 签到状态改为 1   正常出勤      不做时长处理
                        # 在 4      time > end+1 在应签退后一小时之外回来了，晚了           / 签到状态已经在定时函数里改为3   算作早退 这里给用户显示一下  定时函数已经以临时出门的离开时间为结束时间计算工时
                        # 在 2      time < end - 1  且已经签到                            / 签到状态改为 5   临时出门|迟到  记录离开时间
                        # 在 2      end-1 < time < end+1   且已经签到                     / 签到状态改为 9   迟到|完成工作           记录工作时长
                        # 在 2      time > end+1     且已签到                             / 签到状态在定时函数中保持2       迟到|未签退   定时函数按应签退时间计算工作时长
                        # 在 2      time > end+1     且未签到                             / 签到状态在定时函数中更改为8      按缺勤处理
                        # 在 5      time < end+1 在应签退后一小时内回来了                  / 签到状态改为 2   迟到            不做时长处理
                        # 在 5      time > end+1 在应签退后一小时之外回来了，晚了           / 签到状态已经在定时函数中改为7    |早退 这里给用户显示一下 定时函数已经以临时出门的离开时间为结束时间计算工时

                        # 综上：
                        # 对临时出门并且在end+1之前回来的都正常按签到/签退计算工时（所以请理性摸鱼）；对临时出门以后到end+1一直没回来的都算作早退，当天工时会有减少

                        # 生成begin-1 和 begin+1
                        attendTime = set.attendTime.time()
                        endTime = set.endTime.time()
                        dt_attend = datetime.combine(datetime.min, attendTime)
                        dt_plus_one_hour_attend = dt_attend + timedelta(hours=1)
                        dt_sub_one_hour_attend = dt_attend - timedelta(hours=1)
                        result_attend_time_plus = dt_plus_one_hour_attend.time()
                        result_attend_time_sub = dt_sub_one_hour_attend.time()
                        begin_time_plus = datetime.combine(current_date, result_attend_time_plus)
                        begin_time_sub = datetime.combine(current_date, result_attend_time_sub)
                        # 生成 end+1 和 end-1
                        dt_end = datetime.combine(datetime.min, endTime)
                        dt_plus_one_hour_end = dt_end + timedelta(hours=1)
                        dt_sub_one_hour_end = dt_end - timedelta(hours=1)
                        result_end_time_plus = dt_plus_one_hour_end.time()
                        result_end_time_sub = dt_sub_one_hour_end.time()
                        end_time_plus = datetime.combine(current_date, result_end_time_plus)
                        end_time_sub = datetime.combine(current_date, result_end_time_sub)

                        # 0 begin-1<time<begin+1 今日未出勤 + 现在来签到 + 时间满足签到区间 :  状态改为正常出勤 1  记录签到时间
                        if attendance.attendState == 0 and begin_time_sub <= current_datetime < begin_time_plus :
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.attendState = 1
                            attendance.attendTime = current_datetime.time()
                            # 记录正常出勤的签到时间
                            staff_information.staffCheckState = 10
                            # 今日出勤（工作中）
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！完成出勤签到 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 2 time > begin + 1 今日已迟到 + 还未签到 + 现在来签到 ： 状态改为保持为迟到 2 记录签到时间
                        elif attendance.attendState == 2 and current_datetime > begin_time_plus and attendance.attendTime is None:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.attendState = 2
                            attendance.attendTime = current_datetime.time()
                            # 记录迟到的签到时间
                            staff_information.staffCheckState = 21
                            # 今日迟到（工作中）
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！今日迟到|完成签到 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 1 time<end-1 今日正常出勤 + 临时出门 ： 状态改为 正常出勤|临时出门 4 记录离开时间
                        elif attendance.attendState == 1 and current_datetime < end_time_sub:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.leaveTime = current_datetime.time()
                            # 记录临时出门的离开时间
                            attendance.attendState = 4
                            staff_information.staffCheckState = 16
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的识别人员为：' + str(staffName_first) + '！！临时外出 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 1 今日正常出勤 + end-1<time<end+1 : 状态改为6 正常签退下班
                        elif attendance.attendState == 1 and end_time_sub < current_datetime < end_time_plus:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.endTime = current_datetime.time()
                            # 记录签退时间
                            attendance.attendState = 6
                            staff_information.staffCheckState = 14
                            # 今日出勤|已完成工作
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签退人员为：' + str(staffName_first) + '！！今日工作已经完成|离开 ！！'
                            print(string_return)
                            attend_records.append(string_return)
                            # 记录今日工作时长
                            dt1 = datetime.combine(current_date, attendance.endTime)
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

                            # 正常签退下班，出勤统计次数 + 1
                            sum.attendFrequency = sum.attendFrequency + 1

                            # 工作时长保存到年度工作时长统计记录中(Works 的一个字段名的命名写错了，改完以后再执行此操作)
                            work = Works.query.filter(set.staffId == Works.staffId).first()
                            if work.workTime is None:
                                work.workTime = float_time
                            else:
                                work.workTime = work.workTime + float_time


                        # 1 time>end+1 状态下忘记签退，定时函数已经给他签退/记录工作时长（在end+1之后他又回来了）
                        elif attendance.attendState == 6 and current_datetime > end_time_plus :
                            string_return = 'ERROR！ 此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：'+ str(staffName_first) + '！！今天已经默认完成签退 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 4 time<end+1 在临时出门的条件下，他又回来了
                        elif attendance.attendState == 4 and current_datetime < end_time_plus:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.attendState = 1
                            staff_information.staffCheckState = 10
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！临时外出返回 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 4 time>end+1 临时出门然后在end+1之前没回来，之后再回来的那种, 4 状态已经在定时函数中被改为3
                        elif attendance.attendState == 3 and current_datetime > end_time_plus:
                            string_return = 'ERROR！ 此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！今天已经默认完成签退|早退 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 2 time<end-1 今日迟到 + 已经签到 + 去刷脸识别 === 迟到条件下的临时出门
                        elif attendance.attendState == 2 and attendance.attendTime is not None and current_datetime < end_time_sub:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.attendState = 5
                            attendance.leaveTime = current_datetime.time()
                            # 记录临时出门的离开时间
                            staff_information.staffCheckState = 25
                            # 今日迟到（临时外出）
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的识别人员为：' + str(staffName_first) + '！！今日迟到|现在临时外出 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 2  end-1<time<end+1 今日已经签到 + 今日迟到 + 时间满足下班区间 === 迟到+下班
                        elif attendance.attendState == 2 and attendance.attendTime is not None and end_time_sub < current_datetime < end_time_plus:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.endTime = current_datetime.time()
                            # 记录今天下班时间
                            attendance.attendState = 9
                            attendance.endTime = current_datetime.time()
                            staff_information.staffCheckState = 26

                            # 今日迟到|已完成工作
                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签退人员为：' + str(staffName_first) + '！！今日迟到|工作已经完成|离开 ！！'
                            print(string_return)
                            attend_records.append(string_return)
                            # 记录今日工作时长
                            dt1 = datetime.combine(current_date, attendance.endTime)
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

                        # 2 time > end+1 且已经签到 定时函数中已经处理
                        elif attendance.attendState == 2 and attendance.attendTime is not None and current_datetime > end_time_plus:
                            string_return = '此时 '+ time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime()) +' 新来到的签到人员为：' + str(staffName_first) + '！！今天迟到|已经默认完成签退 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 2 time > end + 1 且今日未签到，定时函数中已经将其状态改为8
                        elif attendance.attendState == 8 and current_datetime > end_time_plus:
                            string_return='ERROR！ 此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！今天已经缺勤 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 5 time<end+1
                        elif attendance.attendState == 5 and current_datetime < end_time_plus:
                            # 记录考勤记录更新的时间
                            attendance.editTime = current_datetime

                            attendance.attendState = 2
                            staff_information.staffCheckState = 21

                            string_return = '此时 '+time.strftime("%Y 年-%m 月-%d 日%H:%M", time.localtime())+' 新来到的签到人员为：' + str(staffName_first) + '！！今日迟到|现在临时外出返回 ！！'
                            print(string_return)
                            attend_records.append(string_return)

                        # 5 time > end+1 定时函数已经将其状态修改为7 并记录了工时
                        elif attendance.attendState == 7 and current_datetime > end_time_plus :
                            string_return = 'ERROR！ 此时新来到的签到人员为：' + str(staffName_first) + '！！今天迟到|早退|已经默认完成签退 ！！'
                            attend_records.append(string_return)
                        else:
                            string_return = 'ERROR！ 此时新来到的签到人员为：' + str(staffName_first) + '！！未知的状态 ！！'
                            print(string_return)
                            attend_records.append(string_return)

        # 保存数据库
        db.session.commit()

        if len(attend_records) >= 50:
            del attend_records[:25]
            print("\n 当前attend_records的数量为： ", len(attend_records))

        return jsonify(attend_records)
    else:
        return redirect(url_for('login.login'))


# 开启签到
@login_required('gateAdmin_username')
@gate_bp.route('<gateAdmin_username>/staff_attend', methods=["POST", 'GET'], endpoint='staff_attend')
def staff_attend(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:
        # 开启签到后，开始单次的记录
        global attend_records
        attend_records = []
        now = datetime.now().strftime("%Y-%m-%d %H:00:00")
        session['now_time'] = now
        gate_admin = gateAdmin.query.filter(gateAdmin.gateAdminId == session.get(gateAdmin_username+'gateAdmin_username')).first()
        return render_template("gate_admin_all/staff_attend.html", gateAdmin=gate_admin)
    else:
        return redirect(url_for('login.login'))

# 停止签到
@login_required('gateAdmin_username')
@gate_bp.route('/<gateAdmin_username>/stop_records', methods=['POST'], endpoint='stop_records')
def stop_records(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:
        return redirect(url_for('index.gate_admin_index', gateAdmin_username=gateAdmin_username))
    else:
        return redirect(url_for('login.login'))

