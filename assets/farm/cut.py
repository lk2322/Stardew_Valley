from PIL import Image
import os
im = Image.open(input())

w, h = im.size
b = 1
for i in range(0, h, 16):
    for j in range(0, w, 16):
        b += 1
        res = im.crop((i, j, i+16, j+16))
        width, height = res.size
        newsize = (width*2, height*2)
        im1 = res.resize(newsize, Image.NEAREST)
        im1.save(os.path.join(r'D:\PyGame\LowCost_Stardew_Valley\assets\farm', str(b) + '.png'))