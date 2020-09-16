import numpy as np
from matplotlib import pyplot as plt
import cv2
import copy
from ImagePreprocess import imagedata


def makeNewJson(fname, height, width, path):#####해당 식판에 대한 Json파일 생성
    json = {}
    json['version'] = "4.1.1"
    json['flags'] = {}
    json['shapes'] = []
    json['imagePath'] = fname
    json['imageData'] = imagedata.imagedata(path).decode('utf-8')
    json['imageHeight'] = height
    json['imageWidth'] = width
    json['lineColor'] = [0,255,0,128]
    json['fillColor'] = [255,0,0,128]

    return json

"""
if label:
        data = json['shapes'].append({})
        data["label"] = label
        data["points"] = []json['shapes']['label'] = 
"""

def addContourJson(contour, name, json):#######Contour Json파일에 추가
    #print(name)
    for i in range(len(contour)):
        dic = {}
        dic['label'] = name
        dic['points'] = []  
        dic['group_id'] = None
        dic['shape_type'] = "polygon"
        dic['flags'] = {}

        # print(type(dic['points']))
        l = []
        if len(contour[i])>2:
            for j in range(len(contour[i])):
                # print(type(contours2[i][j][0]))
                l.append(contour[i][j][0].tolist())
            dic['points'] = l

            json['shapes'].append(dic)

    return json

def getContour(arr):##########흑백 이미지에서 Contour 추출

    _, contours, hierarchy = cv2.findContours(arr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ##########################필수#############################
    #######contour를 표시할 최소 넓이
    #######자잘한 부분에 대한 contour를 모두 표시하지 않기 위한 부분
    limit = 0
    contour = []
    for c in contours:
        area = cv2.contourArea(c)
        if area>limit:
            contour.append(c)

    #img = cv2.drawContours(im2, contours, -1, (0,255,0), 2)
    #cv2.imshow("images%d"%1, img)
    #cv2.waitKey(0)

    return contour

