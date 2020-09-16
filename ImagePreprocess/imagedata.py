import base64
import io
import os.path as osp
import os

import PIL.Image
"""
학습용 json파일을 생성할때 일부 object의 경우는 Contour가 생성되어있지만
그 외의 object들은 새로 따줘야하는 등 json파일을 수정해야 함
따라서 생성된 json파일을 labelme로 열기 위해 Imagedata 값을 생성해주는 부분
Imagedata는 이미지 파일을 base64로 인코딩
"""
def load_image_file(filename):
    try:
        image_pil = PIL.Image.open(filename)
    except IOError:
        print('Failed opening image file: {}'.format(filename))
        return

    # apply orientation to image according to exif
    #image_pil = utils.apply_exif_orientation(image_pil)

    with io.BytesIO() as f:
        ext = osp.splitext(filename)[1].lower()
        format = 'JPEG'
        image_pil = image_pil.convert('RGB')
        image_pil.save(f, format=format)

        f.seek(0)
        return f.read()


def imagedata(imagePath):
    imageData = load_image_file(imagePath)
    imageData = base64.b64encode(imageData)
    return imageData
