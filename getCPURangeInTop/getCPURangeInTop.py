#!/usr/bin/python3
# -*- coding:utf-8 -*-

# 用 top 命令的 -b 参数将产生的内容重定向到文本文件 result.txt(必须)，-d 是时间间隔参数(选用)
# 想边输出到终端边输入到文本可以用 top -b | tee result.txt
# 将产生的一个或多个文本与程序放在同一个目录，运行 python3 getCPURangeInTop.py

import os

keywords = ['systemd']

def getNthNum(line,n):
    values = line.split(' ')
    for value in values:
        if value != '':
            n = n - 1
        if n == 0:
            return value
    return ''

def getMaxMin(value):
    maxx = 0 
    minn = 666666 # 初始数值要大于100 * CPU 数
    for v in value[5:]:
        try:
            tmp = float(v)
        except:
            pass
        else:
            maxx = max(maxx,tmp)
            minn = min(minn,tmp)
    return maxx,minn

def f(filename):
    count = dict()
    for keyword in keywords:
        count[keyword] = list()
    with open(filename,'r') as file:
        for line in file.readlines():
            for i in range(len(keywords)):
                if not keywords[i] in line:
                    continue
                value = float(getNthNum(line,9))
                count[keywords[i]].append(value)
    print('                                               '+filename)
    for keyword in count:
        maxx,minn = getMaxMin(count[keyword])
        print(keyword+'  ---   minn,maxx:   '+str(minn)+'% @ '+str(maxx)+'%')


if __name__ == '__main__':
    files = os.listdir()
    for file in files:
        if file.endswith('.txt')
            f(file)
            #break
