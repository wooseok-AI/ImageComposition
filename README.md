# ImageComposition
Image Composition Algorithm to make to make train data when there is not enough train images.
============================================================================================

###This Algorithm is basicly for YOLACT model (Real-Time Instance Segmentation Model)
[YOCLACT](https://github.com/dbolya/yolact#you-only-look-at-coefficients.)

If you don't have enough train data to train,
you might use this algorithm to generate new train images using existing train images.

###You need Json File which can be generated from 'Labelme'
[Labelme](https://github.com/wkentaro/labelme)

<pre>
<code>
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
</code>
</pre>

#Environment
----------------------
+ Python == 3.6x
+ Set up the environment using one of the following methods: 
<pre>
<code>
conda install pillow
conda install opencv
</code>
<pre>

#RGBA2RGB
-----------------------
Sometimes if you want to use png file, you may need to change RGBA to RGB
Especially when you making train set for YOLACT.
+ You can use 
<pre>
<code>
RGBA2RGB.py
</code>
<pre>
