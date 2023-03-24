from PIL import Image, ImageDraw, ImageFont
import random
import os
import sys
import io

#нанесение водяного знака на изображение

def change_jpg_to_png(path_to_photo):
    base_img = Image.open(path_to_photo).convert('RGB')
    png_image_path = os.path.splitext(path_to_photo)[0] + '.png'

    print(png_image_path)

    base_img.save(png_image_path)
    Image_png = Image.open(png_image_path)

    print(Image_png)

    return png_image_path

def stamp_watermark (pathimgin, pathimgout, codephrase):

    print(pathimgin)


    base_img = Image.open(pathimgin).convert('RGBA')
    width, height = base_img.size

    #создание водяного знака
    font = ImageFont.truetype('arial.ttf', round(height * 0.05))
    size = font.getsize(codephrase)
    WMark = Image.new('RGBA', size, (255, 255, 255, 0))
    pencil = ImageDraw.Draw(WMark)
    pencil.text((0, 0), codephrase, font=font, fill=(119, 123, 126, 25))

    #создание нового изображения
    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(base_img, (0, 0))

    #размножение водяного знака
    WW, WH = WMark.size
    for i in range(0, width // WW + 1 ):
        for j in range(0, height // WH + 1):
            transparent.paste(WMark, (i * WW, j * 2 * WH), mask=WMark)
    transparent.save(pathimgout)







