#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
【留意！！】
启动程序前要先留意 locale (Linux 命令)输出的内容是否为zh_CN.UTF-8
建议写 shell 脚本启动并在运行前 export LC_ALL=zh_CN.UTF-8 
'''

from conf import *
from sys import argv
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests,re,yagmail,json,time,redis


ROOT_URL = 'http://news.gdut.edu.cn'

#HttpFox

session = requests.Session()
session.headers.update({'UserAgent':'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'})

def printf(string):
    if string:
        print(time.strftime("%Y-%m-%d %H:%M:%S : ",time.localtime()) + string)


def weather_api():
    weather_request_url = WEATHER_API_URL+'city='+WEATHER_API_CITY+'&&key='+WEATHER_API_KEY
    weather_request = requests.get(weather_request_url)
    weather_data = []
    if weather_request.status_code == 200:
        weather_data = json.loads(weather_request.content.decode(encoding='utf-8'))
    return weather_data


def html_login():

    session.get(url=ROOT_URL+'/UserLogin.aspx')
    result = session.post(ROOT_URL+'/UserLogin.aspx', data=LOGIN_DATA)
    if result.status_code == 200 and result.url == ROOT_URL+'/':
        category = session.get(ROOT_URL + '/ArticleList.aspx?category=4')
        if category.status_code == 200:
            return category.content
    else:
        printf('login failed '+str(result.status_code) )


def attachment_and_excerpt(url,attachment,excerpt):
    if not url:
        printf('empty url')
        return

    s = session.get(url=url)
    if s.status_code == 200:
        soup = BeautifulSoup(s.content, 'lxml')
        content = soup.find('div', attrs={'id': 'articleBody'})
        downlink = content.find_all('a')
        for val in downlink:
            if 'http://news.gdut.edu.cn/DepartmentUploadFiles' in val['href']: #附件地址
                attachment.append(val['href'])

        info = ''.join( content.getText().split() )
        title = content.find('center')
        info = info.replace(title.getText(),'@') #去除信息量不大的内容【日后修改】
        excerpt.append(info[:150]) #梗概为前150字


def article_id_exist(id):
    if not id:
        printf('empty article id')
        return False

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    print(id,r.get(id))

    if not r.get(id):
        r.set(id,"True")
        return False
    else:
        return True
    return False


def html_parse(html,mail):

    if not html:
        printf('empty html')
        return

    soup = BeautifulSoup(html, 'lxml')
    articles = soup.find('div', attrs={'class': 'articles'})

    if articles:
        for val in articles.find_all('p'):
            article_id = val.find('a')['href'][-6:]

            article_url = ROOT_URL + val.find('a')['href'][1:]
            article_date = val.find_all('span')[1].getText()[:-1]
            article_title = val.find('a')['title']

            if not article_id_exist(article_id):

                title = "<a href="+article_url+">"
                title = title + '<font color="red">'
                title = title + ' -- ' + article_title
                title = title + "</font>" + '@' + article_date
                title = title + "</a>"
                mail.append(title)

                attach_list = [] #附件列表
                excerpt_list = [] #梗概列表

                attachment_and_excerpt(article_url,attach_list,excerpt_list)

                if len(excerpt_list) > 0:
                    mail.append('<p>'+excerpt_list[0]+'</p>')

                if len(attach_list) > 0:
                    #　第一部分为部门，第二部分为文件名
                    url_pattern = re.compile(r'http://news.gdut.edu.cn/DepartmentUploadFiles/(.+)/files/(.+)')

                    for var in attach_list:
                        match = url_pattern.match(var)
                        if match:
                            attachment_name = match.group(2)
                            attachment_url = var

                            if '%' in attachment_name:
                                attachment_name = unquote(attachment_name)

                            attachment_string = '<a href='+attachment_url+'>' + attachment_name + '</a><br>'
                            mail.append(attachment_string)


if __name__ == '__main__':
    weather_data = weather_api()
    printf('get weather infomation finish')
    index_content = html_login()
    printf('login finish')
    mail_content = []

    if weather_data:
        mail_content.append('<p>今天又是崭新的一天。:-) </p>')
        mail_content.append('<p> 当前天气：'+weather_data['HeWeather5'][0]['now']['cond']['txt']+'，'
                            +'气温：'+weather_data['HeWeather5'][0]['now']['tmp']+'℃，'
                            +'体感温度：'+weather_data['HeWeather5'][0]['now']['fl']+'℃，'
                            +'</p>')
        mail_content.append('<p>未来几个小时内的天气为：</p>')
        for i in weather_data['HeWeather5'][0]['hourly_forecast']:
            mail_content.append('<p>'+i['date']+'：'+i['cond']['txt']+'</p>')

    if index_content:
        mail_content.append('lastest update:' + VERSION + '#' +ANNOUNCEMENT)
        mail_content.append('－－　以下是今日的校内通知内容：　－－')
        html_parse(index_content,mail_content)
        printf('parse html finish')

    if mail_content:
        client = yagmail.SMTP(user=SEND_MAIL_USER, password=SEND_MAIL_PWD, host=SEND_MAIL_HOST, port=SEND_MAIL_PORT)
        if len(argv) == 2 and '-t' in argv:
            for addr in SEND_TO_LIST_TEST:
                printf('sending[test user]: ' + addr)
                client.send(addr, subject=SEND_MAIL_SUBJECT, contents=mail_content)
                time.sleep(1)
        else:
            for addr in SEND_TO_LIST:
                printf('sending : '+addr)
                client.send(addr,subject=SEND_MAIL_SUBJECT,contents =mail_content)
                time.sleep(1)

