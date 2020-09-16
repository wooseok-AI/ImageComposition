# %%
from PIL import ImageDraw
import PIL
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import cv2
from ImagePreprocess import makeJson
import time
import random
randomseed = 12345
np.random.seed(randomseed)
# if menu image is too small, it can be resized but resolution can be low
size_threshold = 8000

def crop(img_array, height, width, top, bottom, left, right, rot):

    # crop image as mask size (same as ROI size)
    src = img_array
    dst = src.copy()
    dst = src[top:bottom+1, left:right+1]

    return dst


def find_area(mask):
    # find a size of the square which surround the mask(same as ROI size)
    top = 10000
    bottom = -1
    left = 10000
    right = -1

    height, width = mask.shape
    #search linearly to find mask_area for ROI
    for h in range(height):
        for w in range(width):
            if mask[h][w] != 0:
                if w < left:
                    left = w

                elif w > right:
                    right = w

                if h < top:
                    top = h

                elif h > bottom:
                    bottom = h

    height_mask = (bottom - top) + 1
    width_mask = (right - left) + 1
    return height_mask, width_mask, top, bottom, left, right

def resize_ROI(mask, image, result, resize):
    # Zoom In
    if resize > 1:
            
        mask = cv2.resize(mask, dsize=(0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_LINEAR)
        image = cv2.resize(image, dsize=(0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_LINEAR)
        result = cv2.resize(result, dsize=(0, 0), fx=resize,fy=resize, interpolation=cv2.INTER_LINEAR)

    # Zoom Out
    elif resize < 1:
       
        mask = cv2.resize(mask, dsize=(0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_AREA)
        image = cv2.resize(image, dsize=(0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_AREA)
        result = cv2.resize(result, dsize=(0, 0), fx=resize, fy=resize, interpolation=cv2.INTER_AREA)
        
    return mask, image, result


def composition(source_path, target_path, food_label, compare_list, rotate=0, resize=1):

    # read a json file to load a masking data(Polygon address)
    json_path = source_path[:-4]+'.json'
    print(json_path)
    with open(json_path) as data_file:
        data = json.load(data_file)

    label_id = -1
    list_points = []
    list_menu = []

    # extract mask address from jsonfile
    for i in range(len(data['shapes'])):
        
        #extract only food label(class) 
        if data['shapes'][i]['label'] in food_label:
            print(data['shapes'][i]['label'])
            points = data['shapes'][i]['points']
            
            label_id = i
            #save mask address and food class seperately
            list_points.append(points)            
            list_menu.append(data['shapes'][i]['label'])

    # If there is no masking data of food class, return 0
    if label_id == -1:
        return 0


    # to compose only the biggest one in each classes, we compare the area eachother
    if len(compare_list) != 0:

        # Dictionary to compare area
        compare = {} 
        # save a biggest area of menu to compare with other class's menu size
        biggest_compare = {} 

        for k in range(len(list_menu)):
            
            # Comparison Target('class'-'num')
            menu_with_number = list_menu[k]
            
            # Menu Class
            only_food = menu_with_number.split('-')[0]
            
            # Skip when the there is one photo of one individual class 
            if  only_food not in compare_list:
                continue

            # implement mask on mask_background
            mask_background = PIL.Image.new("RGB", (1280, 720))
            mask_draw = ImageDraw.Draw(mask_background) 
            points = [tuple(pair) for pair in list_points[k]]
            mask_draw.polygon((points), fill=200)

            # area_mask : mask data of class
            area_mask = (np.array(mask_background)[:, :, 0] > 0).astype('float32')
            
            # area of the mask
            area = cv2.moments(area_mask)['m00']
            
            # Find out the biggest area among the relevent classes
            if not only_food in compare:
                compare[only_food] = area
                biggest_compare[only_food] = k
            
            else:

                #because food and masking address has same index
                #we will earse the smaller ones at last
                if area < compare[only_food]:
                    list_points[k] = None
                    list_menu[k] = None

                else:
                    # if there is new bigger one, erase the previous bigger one
                    compare[only_food] = area
                    index = biggest_compare[only_food]
                    list_points[index] = None
                    list_menu[index] = None
                    biggest_compare[only_food] = k
            
            
            if area < 5000:
                list_points[k] = None
                list_menu[k] = None

        # To simulate the index of list_menu and list_points 
        # make a smaller one to None and filter it at the last moment
        list_menu = list(filter(lambda a: a != None, list_menu))
        list_points = list(filter(lambda a: a != None, list_points))


            

    """Compose each menu on one plate"""
    for k in range(len(list_menu)):
    # for k in range(1):
        start = time.time()

        img_array = cv2.imread(source_path)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            
        menu = list_menu[k].split('-')[0]
        image = PIL.Image.new("RGB", (1280, 720))
        draw = ImageDraw.Draw(image)

        # draw polygon
        points = [tuple(pair) for pair in list_points[k]]
        draw.polygon((points), fill=200)
        mask = (np.array(image)[:, :, 0] > 0).astype('float32')

        #find a size of class, to find whether it is bigger than threshold.
        size = cv2.moments(mask)['m00']


        """Rotation"""
        if rotate != 0:
            #find mask's height and widht which is actually a box surrounding mask
            mask_height, mask_width = mask.shape

            #There were several problem when we roate mask and image
            #Such as unintended image cutting
            #So I decide to maximize the area of the box for rotation without problem
            mask_height, mask_width = max(mask_height, mask_width), max(mask_height, mask_width)

            #Rotate as amount of the angle 'rotate'
            matrix = cv2.getRotationMatrix2D((mask_width//2, mask_height//2), rotate, 1)
            mask = cv2.warpAffine(mask, matrix, (mask_width, mask_height))

            #As we cut the image by mask, because of mask rotation, we have to rotate image as well
            #process is the same as rotating mask
            img_height, img_width, _ = img_array.shape
            img_height, img_width = max(img_height, img_width), max(img_height, img_width)
            matirx = cv2.getRotationMatrix2D((img_width//2, img_height//2), rotate, 1)
            img_array = cv2.warpAffine(img_array, matrix, (img_width, img_height))

        
        #Set the square ROI which is identical fo the box which surround the mask points
        height, width, top, bottom, left, right = find_area(mask)

        #Cropped the mask and image exact same size of ROI
        cropped_mask = crop(mask, height, width, top,bottom, left, right, rotate)
        cropped_image = crop(img_array, height, width, top,bottom, left, right, rotate)

        result = np.zeros((height, width, 3), dtype='float32')

        for i in range(3):
            result[:, :, i] = np.multiply(result[:, :, i], (cropped_mask != 0))
            result[:, :, i] += np.multiply(cropped_image[:, :, i],cropped_mask).astype(np.uint8)


        """RESIZING IMAGE"""
        
        # if size < size_threshold:
        # if menu.split('-')[0] in compare.keys():

        if cv2.moments(mask)['m00'] < size_threshold:
                   
            # root = Tk()
            # lbl = Label(root, text="menu is too small would you like to resize?")
            # lbl.grid(row=0, column=0)
            # txt = Entry(root)
            # txt.grid(row=0, column=1)
            # btn = Button(root, text="OK", width=15)
            # btn.grid(row=1, column=1)
            resize_class = 1.2
            # root.mainloop()

            cropped_mask, cropped_image, result = resize_ROI(cropped_mask, cropped_image, result, resize_class)
        
        # if resize rate has been set manually
        elif resize != 1 :
            
            cropped_mask, cropped_image, result = resize_ROI(cropped_mask, cropped_image, result, resize)
        

        """pre-process to compose cropped image on target image"""
        food = result.astype('uint8')

        background = cv2.imread(target_path).astype('uint8')
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        #resize the image to 1080,720
        background = cv2.resize(background, (1080, 720))

        #to locate ROI randomly
        a = np.random.randint(2,20)
        b = np.random.randint(2,20)
        c = np.random.randint(1,a)
        d = np.random.randint(1,b)
        """"SET ROI"""
        background_height, background_width, _ = background.shape
        food_height, food_width, _ = food.shape
        # To make train data diverse, I set the ROI position randomly
        # Further, I will update function that make the images rotate randomly
        x = ((background_height - food_height) // a)* (c)
        y = ((background_width - food_width) // b) * (d)
        roi = background[x: x+food_height, y: y+food_width]


        """ Compose on ROI"""
        print('==> Composing Image...', menu)

        tmp = np.copy(roi)
        for i in range(3):
            tmp[:, :, i][cropped_mask == 1] = food[:, :, i][cropped_mask == 1]
        roi_food = tmp

        result = roi_food
        np.copyto(roi, result)

        im2 = PIL.Image.fromarray(background.astype(np.uint8))
        target = target_path.split('/')[-1]
        target = target.split('.')[0]
        im2.save(r'..'+'\\'+'composition'+'\\'+'composed' +'-'+menu+'_'+target+'-'+source_path.split('/')[-1])


        """making new Json file of composed image"""
        print('==> Making Jason...', menu)
        (height, width, _) = background.shape
        path = r'..'+'\\'+'composition'+'\\'+'composed' + '-'+menu+'_'+target+'-'+source_path.split('/')[-1]
        imagename = 'composed' + '-'+menu+ '_' + target+'-'+source_path.split('/')[-1]
        json_data = makeJson.makeNewJson(imagename, height, width, path)

        temp_zero = np.zeros((1280, 1280), dtype='uint8')
        temp_roi = temp_zero[x:x+food_height, y:y+food_width]

        temp_roi[:, :] = np.add(temp_roi[:, :], (cropped_mask != 0))
        temp_roi = temp_roi * 255

        contour = makeJson.getContour(temp_zero)
        json_data = makeJson.addContourJson(contour, menu, json_data)
        filename = r'..'+'\\'+'composition' + '\\'+imagename.split('.')[0] + '.json'

        with open(filename, 'w') as fp:
            json.dump(json_data, fp, indent=4)
        print('done [time spent : %0.2f sec]' %(time.time() - start))


# %%

# ####################################################################################
# if you want to test please use this cell

# source_path = 
# target_path = 
# food_label = ["kkakdugi", "osambulgogi", "kongnamulmuchim"]

# # if there is no folder in this path, create folder
# if not os.path.isdir('composition'):
#     os.makedirs('composition')

# composition(source_path, target_path, food_label, rotate=60)
######################################################################################


# %%
# input: source_path, target_path, food_label, rotate, compare#
######################################################################################
# source_path : 음식 사진이 있는 폴더 경로
# target_path : 음식사진이 합성될 배경 사진 경로
# food_label : Json 파일에서 추출한 음식 라벨
# compare_list : 동일하지만 크기가 다른 음식이 다수라면 비교 (default = False )
# rotate : 음식 합성시 회전을 시킬지의 여부 (default = 0)
######################################################################################

folderpath = r'Z:\wooseokjung\image_composition\sample' #insert your folder path here
os.chdir(folderpath)
file_list = os.listdir(folderpath)
obj = ['plate','spoon', 'chopsticks', 'tray', 'hand', 'bap'] #The class that you want to use
# black, red, blue, yellow, food_trash, grass, people
target_path = 'Z:/wooseokjung/image_composition/target/highway.png' #Background image path that you want to inser class on it

for file in file_list:
    food_label = []
    food_variable = []
    number_menu = {}
    compare_list = []

    # extract food labels from jsonfile
    if file.startswith('Thumb'):
        continue

    if file.endswith('.json'):
        jsonPath = folderpath + '\\' + file
        with open(jsonPath, 'r') as f_json:
            jsonDict = json.load(f_json)

            for h in range(len(jsonDict['shapes'])):
                label = jsonDict['shapes'][h]['label']
                # 메뉴 고유값을 구하기 위해 번호를 삭제
                only_food = label.split('-')[0]  

                if only_food in obj:
                    continue
                else:
                    food_label.append(label)
                    food_variable.append(only_food)

        # 중복제거
        food_label = list(set(food_label))
        food_variable = list(set(food_variable))

        file = file.split('.')[0] + '.png'

    elif file.endswith('.png'):
        continue

    # find menu that we have to compare the size among them
    food_count = {}

    for x in range(len(food_variable)):
        f = food_variable[x]
        food_count[f] = 0
        cnt = 0

        for y in range(len(food_label)):
            if f in food_label[y]:
                cnt += 1

        food_count[f] = cnt
        if cnt > 1:
            compare_list.append(f)

    source_path = folderpath + '/' + file

    if not os.path.isdir('../composition'):
        os.makedirs('../composition')
    composition(source_path, target_path, food_label, compare_list, rotate=45) 

