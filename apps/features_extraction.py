import os
import dlib
from skimage import io
import csv
import numpy as np

# 要读取人脸图像文件的路径 / Path of cropped faces
path_images_from_camera = "static/data/data_faces_from_camera/"

# Dlib 正向人脸检测器 / Use frontal face detector of Dlib
detector = dlib.get_frontal_face_detector()

# Dlib 人脸 landmark 特征点检测器 / Get face landmarks
predictor = dlib.shape_predictor('static/data_dlib/shape_predictor_68_face_landmarks.dat')

# Dlib Resnet 人脸识别模型，提取 128D 的特征矢量 / Use Dlib resnet50 model to get 128D face descriptor
face_reco_model = dlib.face_recognition_model_v1("static/data_dlib/dlib_face_recognition_resnet_model_v1.dat")
# 这行代码创建了一个人脸识别模型对象，并将其赋值给变量face_reco_model。这个人脸识别模型使用了一个预训练的ResNet模型，
# 模型文件的路径为static/data_dlib/dlib_face_recognition_resnet_model_v1.dat。
# 这个模型文件包含了训练好的人脸识别模型的参数。


# 返回单张图像的 128D 特征 / Return 128D features for single image
# Input:    path_img           <class 'str'>
# Output:   face_descriptor    <class 'dlib.vector'>
def return_128d_features(path_img):
    img_rd = io.imread(path_img)
    # 这行代码使用io.imread()函数从指定路径加载图像，并将其赋值给变量img_rd。
    # 这里使用了io模块的imread()函数，该函数能够读取图像文件，并将其解码为NumPy数组表示的图像数据。
    faces = detector(img_rd, 1)
    # 这行代码使用之前创建的人脸检测器对象detector对图像img_rd进行人脸检测。
    # 它返回一个包含检测到的人脸矩形框的列表，并将结果赋值给变量faces。
    # 参数1表示对图像进行上采样（upsample），以便提高人脸检测的准确性。

    # 因为有可能截下来的人脸再去检测，检测不出来人脸了, 所以要确保是 检测到人脸的人脸图像拿去算特征
    if len(faces) != 0:
        shape = predictor(img_rd, faces[0])
        face_descriptor = face_reco_model.compute_face_descriptor(img_rd, shape)
        # 首先，它检查变量faces中是否存在检测到的人脸矩形框。如果存在人脸矩形框，就使用人脸特征点检测器predictor从图像img_rd中获取人脸的特征点坐标，
        # 并将结果赋值给变量shape。接下来，使用人脸识别模型face_reco_model的compute_face_descriptor()函数计算给定人脸的128维特征向量，
        # 并将结果赋值给变量face_descriptor。如果未检测到人脸矩形框，则将变量face_descriptor的值设为0，并打印"no face"的提示信息。
    else:
        face_descriptor = 0
        print("no face")
    return face_descriptor


# 返回 personX 的 128D 特征均值 / Return the mean value of 128D face descriptor for person X
# Input:    path_faces_personX       <class 'str'>
# Output:   features_mean_personX    <class 'numpy.ndarray'>
def return_features_mean_personX(path_faces_personX):
    features_list_personX = []
    photos_list = os.listdir(path_faces_personX)
    # 给定职工用户人脸图片的存储文件夹的路径
    if photos_list:
        # 遍历其中的全部图片
        for i in range(len(photos_list)):
            # 调用 return_128d_features() 得到 128D 特征
            features_128d = return_128d_features(path_faces_personX + "/" + photos_list[i])
            # 遇到没有检测出人脸的图片跳过
            if features_128d == 0:
                i += 1
            else:
                features_list_personX.append(features_128d)
    else:
        print(" >> 文件夹内图像文件为空 / Warning: No images in " + path_faces_personX + '/', '\n')

    # 计算 128D 特征的均值 / Compute the mean
    # personX 的 N 张图像 x 128D -> 1 x 128D
    if features_list_personX:
        features_mean_personX = np.array(features_list_personX).mean(axis=0)
    else:
        features_mean_personX = np.zeros(128, dtype=int, order='C')
    return features_mean_personX


