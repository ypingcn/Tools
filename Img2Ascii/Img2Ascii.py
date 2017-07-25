#!/usr/bin/python3
# -*- coding:utf-8 -*-

from PIL import Image
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('file',help='input name list file')
parser.add_argument('--output','-o',help='output file name,result.txt for default')
parser.add_argument('--height',help='height pixel to resize,100 for default',type=int,default=100)
parser.add_argument('--width',help='width pixel to resize,100 for default',type=int,default=100)
parser.add_argument('--show','-s',help='show the image after resizing,false for default',action="store_true", default=False)

args = parser.parse_args()

INPUT_FILE = args.file
HEIGHT = args.height
WIDTH = args.width
OUTPUT_FILE = args.output

R_VALUE = 0.2126
G_VALUE = 0.7152
B_VALUE = 0.0722

ASCII = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
UNIT = (256+1.0)/len(ASCII)

def handle(r,g,b,alpha=256):
    if alpha == 0:
        return ''

    gray = int(R_VALUE*r + G_VALUE*g + B_VALUE*b)

    return ASCII[int(gray/UNIT)]

    
if __name__ == '__main__':

    img = Image.open(INPUT_FILE)
    img = img.resize((WIDTH,HEIGHT),Image.NEAREST)
    if args.show:
        img.show()

    res = ''

    for i in range(HEIGHT):
        for j in range(WIDTH):
            #print(*img.getpixel((j,i)))
            res += handle( *img.getpixel( (j,i) ) )
        res += '\n'

    print(res)

    if OUTPUT_FILE:
        with open(OUTPUT_FILE,'w') as file:
            file.write(res)
    else:
        with open('result.txt','w') as file:
            file.write(res)
        
