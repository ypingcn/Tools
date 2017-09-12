#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
【留意！！】
启动程序前要先留意 locale (Linux 命令)输出的内容是否为zh_CN.UTF-8
建议写 shell 脚本启动并在运行前 export LC_ALL=zh_CN.UTF-8 
'''

from conf import *
from sys import argv
from bs4 import BeautifulSoup
import requests,re,yagmail,json,time


ROOT_URL = 'http://news.gdut.edu.cn/'

#HttpFox

session = requests.Session()

def weather_api():
    weather_request_url = WEATHER_API_URL+'city='+WEATHER_API_CITY+'&&key='+WEATHER_API_KEY
    weather_request = requests.get(weather_request_url)
    weather_data = []
    if weather_request.status_code == 200:
        weather_data = json.loads(weather_request.content.decode(encoding='utf-8'))
    return weather_data


def html_login():
    session.get(url=ROOT_URL + 'UserLogin.aspx')
    result = session.post('http://news.gdut.edu.cn/UserLogin.aspx', data=LOGIN_DATA)
    if result.status_code == 200 and result.url == ROOT_URL:
        return result.content
    else:
        print('login failed')


def attachment_and_excerpt(url,attachment,excerpt):
    if not url:
        print('empty url')
        return

    s = session.get(url=url)
    if s.status_code == 200:
        soup = BeautifulSoup(s.content, 'lxml')
        content = soup.find('div', attrs={'id': 'content'})
        downlink = content.find_all('a')
        for val in downlink:
            if 'http://news.gdut.edu.cn/DepartmentUploadFiles' in val['href']: #附件地址
                attachment.append(val['href'])

        info = ''.join( content.getText().split() )
        info = info.replace('您现在的位置>校内通知>文章内容','@') #去除信息量不大的内容【日后修改】
        excerpt.append(info[:150]) #梗概为前150字


def html_parse(html,mail):
    if not html:
        print('empty html')
        return

    soup = BeautifulSoup(html, 'lxml')
    search = soup.find('div', attrs={'id': 'hot_news'})

    if search:
        for val in search.find_all('li'):
            title = "<a href="+ROOT_URL + val.find('a')['href']+">"
            title = title + '<font color="red">'
            title = title + ' -- ' + val.find('a')['title']
            title = title + "</font>"
            title = title + "</a>"
            mail.append(title)

            attach_list = [] #附件列表
            excerpt_list = [] #梗概列表

            attachment_and_excerpt(ROOT_URL + val.find('a')['href'],attach_list,excerpt_list)

            if len(excerpt_list) > 0:
                mail.append('<p>'+excerpt_list[0]+'</p>')

            if len(attach_list) > 0:
                #　第一部分为部门，第二部分为文件名
                pattern = re.compile('http://news.gdut.edu.cn/DepartmentUploadFiles/(.+)/files/(.+)')

                for var in attach_list:
                    match = pattern.match(var)
                    if match:
                        attachment_name = match.group(2)
                        attachment_url = var

                        attachment_string = '<a href='+attachment_url+'>' + attachment_name + '</a><br>'
                        mail.append(attachment_string)


if __name__ == '__main__':
    weather_data = weather_api()
    print('get weather infomation finish')
    index_content = html_login()
    print('login finish')
    mail_content = []

    if weather_data:
        mail_content.append('<p>今天又是崭新的一天。:-) '
                            +'当前天气：'+weather_data['HeWeather5'][0]['now']['cond']['txt']+'，'
                            +'气温：'+weather_data['HeWeather5'][0]['now']['tmp']+'℃，'
                            +'体感温度：'+weather_data['HeWeather5'][0]['now']['fl']+'℃，'
                            +'</p>')
        mail_content.append('<p>'+'未来几个小时内的天气为：'+'</p>')
        for i in weather_data['HeWeather5'][0]['hourly_forecast']:
            mail_content.append('<p>'+i['date']+'：'+i['cond']['txt']+'</p>')
    if index_content:
        mail_content.append('－－　以下是今日的校内通知内容：　－－')
        html_parse(index_content,mail_content)
        print('parse html finish')

    if mail_content:
        client = yagmail.SMTP(user=SEND_MAIL_USER, password=SEND_MAIL_PWD, host=SEND_MAIL_HOST, port=SEND_MAIL_PORT)
        if len(argv) == 2 and '-t' in argv:
            for addr in SEND_TO_LIST_TEST:
                print('[test user] - sending : ' + addr)
                client.send(addr, subject=SEND_MAIL_SUBJECT, contents=mail_content)
                time.sleep(1)
        else:
            for addr in SEND_TO_LIST:
                print('sending : '+addr)
                client.send(addr,subject=SEND_MAIL_SUBJECT,contents =mail_content)
                time.sleep(1)

