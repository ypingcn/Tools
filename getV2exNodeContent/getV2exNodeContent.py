#!/usr/bin/python3
# -*- coding:utf-8 -*-

import requests,re
from bs4 import BeautifulSoup

keywords = ['深圳','广州']

for i in range(1,5):
    html = requests.get('https://www.v2ex.com/go/jobs?p='+str(i)).content

    #with open(str(i)+'.html','wb') as file:
        #file.write(html)

    soup = BeautifulSoup(html,'lxml')


    topic = soup.find('div',attrs = {'id':'TopicsNode'})

    for val in topic.find_all('div'):
        if 'cell' not in val['class']:
            continue

        text = val.getText().replace('\n','')

        bold = False

        for var in keywords:
            if var in text:
                bold = True

        if bold:
            print("\033[32;1m " + text + "\033[0m")
            pattern = re.compile('t_([0-9]+)')
            res = pattern.match(val['class'][2])
            if res:
                print("\033[32;1m " + 'https://www.v2ex.com/t/'+res.group(1) + "\033[0m")
        else:
            print(text)
