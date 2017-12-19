#!/usr/bin/python3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests

ROOT_URL = 'http://news.gdut.edu.cn/'

login_data = {}
login_data['__VIEWSTATE']='/wEPDwUKLTQwOTA4NzE2NmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFI2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkQ2hlY2tCb3gxBufpEJuDDaf6eTj0A4Cn2Erf8u98KcGrQqATTB3mEaQ='
login_data['__EVENTVALIDATION'] = '/wEWBQKb37HjDwLgvLy9BQKi4MPwCQL+zqO2BAKA4sljg4IvzC7ksG01o7aN0RZUOKEC4lV0bTeXI4zrbaQsj0c='

# 联系校内人员获取账号密码，此处的账号密码无效
login_data['ctl00$ContentPlaceHolder1$userEmail'] = 'test'
login_data['ctl00$ContentPlaceHolder1$userPassWord'] = 'test'

login_data['ctl00$ContentPlaceHolder1$CheckBox1'] = 'on'
login_data['ctl00$ContentPlaceHolder1$Button1'] = '%E7%99%BB%E5%BD%95'

session = requests.Session()

def title_print(content):
    if not content:
        return
    print("\033[32;1m " + content + "\033[0m")

def html_login():
    login = session.get(url=ROOT_URL+'UserLogin.aspx')
    result = session.post('http://news.gdut.edu.cn/UserLogin.aspx',data=login_data)
    if result.status_code == 200 and result.url == ROOT_URL:
        return result.content
    else:
        print('login failed')

def html_parse(html):
    if not html:
        print('empty html')
        return

    soup = BeautifulSoup(html,'lxml')
    search = soup.find('div',attrs={'id':'hot_news'})
    if search:
        for val in search.find_all('li'):
            title_print(' -- '+val.find('a')['title'])
            test = attachment_detect(ROOT_URL+val.find('a')['href'])
            if test:
                for var in test:
                    print('@'+var)

def attachment_detect(url):
    res = []

    if not url:
        print('empty url')
        return

    s = session.get(url=url)
    if s.status_code == 200:
        soup = BeautifulSoup(s.content,'lxml')
        content = soup.find('div',attrs={'id':'content'})
        downlink = content.find_all('a')
        for val in downlink:
            if 'http://news.gdut.edu.cn/DepartmentUploadFiles' in val['href']:
                res.append(val['href'])

    return res
        

if __name__ == '__main__':
    index_content = html_login()
    if index_content:
        html_parse(index_content)


