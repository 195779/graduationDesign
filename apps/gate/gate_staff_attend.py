import base64
import os
import time

import cv2
import numpy as np
from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, Response, jsonify, \
    current_app, g

from apps.Index.index_gate_admin import login_required
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
            # A 用户签到成功后，如果一直在这刷脸签到则 此 if 不执行
            # A离开 B过来签到成功， 则 A或者 除了B之外的任何人 再次来这刷脸， 则此if 可以执行

            staffName_last = staffName_first
            print("此时新来的签到人员为：" + str(staffName_first))

            # 在这里，可以对已经识别到的 Name 进行 处理

        if len(attend_records) >= 50:
            del attend_records[:25]
            print("\n 当前attend_records的数量为： ", len(attend_records))

        return jsonify(attend_records)
    else:
        return redirect(url_for('login.login'))


# 开启签到
@login_required('gateAdmin_username'                                    )
@gate_bp.route('<gateAdmin_username>/staff_attend', methods=["POST", 'GET'], endpoint='staff_attend')
def staff_attend(gateAdmin_username):
    if session.get(gateAdmin_username + 'gateAdmin_username') is not None:
        # 开启签到后，开始单次的记录
        global attend_records
        attend_records = []
        now = time.strftime("%Y-%m-%d %H:00:00", time.localtime())
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

