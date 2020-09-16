#폴더 속 사진 RGBA에서 RGB로 바꾸는 명령어

import os
from PIL import Image


folderPath = #insert your image(folder) path here
fileList = os.listdir(folderPath)

for file in fileList:
    if not file.endswith('.png'):
        continue
    fileAbsPath = folderPath + '\\' + file
    tmp = Image.open(fileAbsPath)
    tmp = tmp.convert('RGB')
    tmp.save(fileAbsPath)
