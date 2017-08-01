#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import requests,re

url = 'http://bbs.tianya.cn/post-210-104531-1.shtml'

session = requests.Session()

def download_save_img(arg_url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0','Referer':url}
    img = session.get(arg_url)
    pattern = re.compile('http://img3.laibafile.cn/p/m/([0-9]{9}).jpg')
    name = ''
    if res and img.status_code == 200:
        name = res[0]+'.jpg'
        print(name)
        open(name,'wb').write(img.content)
    return name

def download_html(arg_url):
    #print(arg_url)
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    r = session.get(arg_url,headers = headers)
    if r.status_code == 200:
        print(r.cookies)
        return r.content

def parse_html(html):
    soup = BeautifulSoup(html,'lxml')
    print(soup.title.text)
    res = soup.find_all('div',attrs={'class','bbs-content'})
    with open('result.md','a') as file:
        for val in res:
            img = val.find('img')
            if img:
                print('Image download temporary unavailable')
                #download_save_img(img['original'])
            #print(' --- --- ---')
            #print(val.getText())
            file.write(val.getText())
    next_page = soup.find('link',attrs={'rel':'next'})
    if next_page:
        return next_page['href']

if __name__ == '__main__':
    while(url):
        url = parse_html(download_html(url))
