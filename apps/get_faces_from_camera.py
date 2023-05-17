# 进行人脸录入

import dlib
import numpy as np
import cv2
import os
from skimage import io

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()


class Face_Register:
    def __init__(self):
        pass

    # 将录入的图片进行人脸检测，部分截取人脸部分
    @staticmethod
    def process(self, path):
        photos_list = os.listdir(path)
        if photos_list:
            for i in range(len(photos_list)):
                # 调用 return_128d_features() 得到 128D 特征
                current_face_path = path + photos_list[i]
                print("%-40s %-20s" % (" >> 正在检测的人脸图像 / Reading image:", current_face_path))
                img_rd = cv2.imread(current_face_path)
                faces = detector(img_rd, 0)
                # detector = dlib.get_frontal_face_detector() & Dlib人脸检测器
                # 遇到没有检测出人脸的图片跳过
                if len(faces) == 0:
                    i += 1
                else:
                    for k, d in enumerate(faces):
                        # 计算人脸区域矩形框大小
                        height = (d.bottom() - d.top())
                        width = (d.right() - d.left())
                        hh = int(height / 2)
                        ww = int(width / 2)

                        # 判断人脸矩形框是否超出 480x640
                        if (d.right() + ww) > 640 or (d.bottom() + hh > 480) or (d.left() - ww < 0) or (
                                d.top() - hh < 0):
                            print("%-40s %-20s" % (" >>超出范围，该图作废", current_face_path))
                        else:
                            img_blank = np.zeros((int(height * 2), width * 2, 3), np.uint8)
                            for ii in range(height * 2):
                                for jj in range(width * 2):
                                    img_blank[ii][jj] = img_rd[d.top() - hh + ii][d.left() - ww + jj]
                            cv2.imwrite(path + str(i + 1) + ".jpg", img_blank)
                            print("写入本地 / Save into：", str(path) + str(i + 1) + ".jpg")
        else:
            print(" >> 文件夹内图像文件为空 / Warning: No images in " + path, '\n')

    @staticmethod
    def single_pocess(path):
        # 读取人脸图像
        img_rd = cv2.imread(path)
        # 使用OpenCV库的imread()
        # 函数从指定路径读取图像，并将其赋值给变量img_rd。返回值类型是一个NumPy数组，表示读取的图像
        # Dlib的人脸检测器
        faces = detector(img_rd, 0)
        # 使用detector对象对图像进行人脸检测。它接受两个参数：第一个参数是待检测的图像（img_rd），
        # 第二个参数是可选参数，用于设置图像金字塔的缩放比例（这里设置为0，表示不进行缩放）。
        # 返回值是一个包含检测到的人脸位置信息的列表。每个人脸位置信息表示为dlib.rectangle对象。
        # 如果没有检测到人脸，返回的列表将为空。
        # 遇到没有检测出人脸的图片跳过
        if len(faces) == 0:
            return "none"
        else:
            for k, d in enumerate(faces):
                # 计算人脸区域矩形框大小
                # enumerate(faces)返回一个迭代器，每次迭代返回一个元组，其中第一个元素是索引（k），
                # 第二个元素是人脸位置信息（d）。dlib.rectangle对象的方法（例如bottom()、top()、right()、left()）
                # 可用于获取人脸矩形框的底部、顶部、右侧和左侧坐标。height和width计算人脸区域矩形框的高度和宽度。
                # hh和ww分别是高度和宽度的一半，转换为整数类型。
                height = (d.bottom() - d.top())
                width = (d.right() - d.left())
                hh = int(height / 2)
                ww = int(width / 2)

                # 判断人脸矩形框是否超出 480x640
                # right > left 而且 bottom > top
                # 所以利用 长度与宽度的 1/2 长度， 让原图 在中间，
                # 判断其原图的外部框（2*height, 2*width）是否满足 0*0---480*640的坐标区间
                if (d.right() + ww) > 640 or (d.bottom() + hh > 480) or (d.left() - ww < 0) or (
                        d.top() - hh < 0):
                    print("%-40s %-20s" % (" >>超出范围，该图作废", path))
                    return "big"

                else:
                    img_blank = np.zeros((int(height * 2), width * 2, 3), np.uint8)
                    for ii in range(height * 2):
                        for jj in range(width * 2):
                            img_blank[ii][jj] = img_rd[d.top() - hh + ii][d.left() - ww + jj]
                    # 将满足条件的外部框整个复制出来，覆写原图片路径
                    # 完成人脸图像的裁剪
                    # ！！！！
                    # 这里要注意： 如果上传的图片包含两个及其以上的人脸， 则只能识别出第一个人脸就return退出循环了
                    # 所以要提醒使用者，在拍摄时保持提交图片中仅包含一人人脸图像，否则容易误传入他人人脸图像，
                    # 造成最后计算的人脸特征值的均值不准确
                    # ！！！！
                    cv2.imwrite(path, img_blank)
                    # 重新给该图片的完整路径下写入裁剪之后的人脸图片
                    print("写入本地 / Save into：", path)
                    return "right"
