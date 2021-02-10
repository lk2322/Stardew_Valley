import os
from PIL import Image


path = r'D:\PyGame\LowCost_Stardew_Valley\assets\farm'
for file_name in os.listdir(path):
    base_name, ext = os.path.splitext(file_name)
    if ext.lower() not in ['.png']:
        continue
    im = Image.open(os.path.join(path, file_name))
    width, height = im.size
    newsize = (32, 32)
    im1 = im.resize(newsize, Image.NEAREST)
    im1.save(os.path.join(r'D:\PyGame\LowCost_Stardew_Valley\assets\farm\resized\melon', file_name))
