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
from jinja2 import  Environment,FileSystemLoader,select_autoescape
import re,os,json,time,redis,yagmail,requests

ROOT_URL = 'http://news.gdut.edu.cn'

session = requests.Session()
session.headers.update({'UserAgent':'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'})

jinja2_env = Environment(
    loader = FileSystemLoader(os.getcwd()+'/template'),
    autoescape = select_autoescape(['html'])
)


def printf(string):
    if string:
        print(time.strftime("%Y-%m-%d %H:%M:%S : ", time.localtime()) + string)


def article_id_exist(id):
    if not id:
        printf('empty article id')
        return False

    if not id.isdigit():
        printf('need number instead of other value type')
        return False

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    if not r.get(id):
        r.set(id,"True")
        return False
    else:
        return True


def get_weather_data():
    weather_request_url = WEATHER_API_URL + 'city=' + WEATHER_API_CITY + '&&key=' + WEATHER_API_KEY
    weather_request = requests.get(weather_request_url)
    weather_data = []
    if weather_request.status_code == 200:
        weather_data = json.loads(weather_request.content.decode(encoding='utf-8'))
    return weather_data


def get_index():
    session.get(url=ROOT_URL+'/UserLogin.aspx')
    result = session.post(ROOT_URL+'/UserLogin.aspx', data=LOGIN_DATA)
    if result.status_code == 200 and result.url == ROOT_URL+'/':
        category = session.get(ROOT_URL + '/ArticleList.aspx?category=4')
        if category.status_code == 200:
            return category.content
    else:
        printf('login failed '+str(result.status_code) )


def parse_html(html):
    if not html:
        printf('empty html')
        return

    html_soup = BeautifulSoup(html, 'lxml')
    articles = html_soup.find('div', attrs={'class': 'articles'})

    if not articles:
        printf('article not found')
        return

    article_result = []

    for val in articles.find_all('p'):
        article_id = val.find('a')['href'][-6:]
        article_url = ROOT_URL + val.find('a')['href'][1:]
        article_date = val.find_all('span')[1].getText()[:-1]
        article_title = val.find('a')['title']
        article_author = val.span['title']
        article_attachment = []
        article_excerpt = ''

        if article_id_exist(article_id):
            printf('article exist in database %s' % (article_title))
            continue

        article_detail = session.get(url=article_url)

        if article_detail.status_code != 200:
            printf('get article detail error %s' % (article_id) )
            continue

        article_soup = BeautifulSoup(article_detail.content,'lxml')
        article_content = article_soup.find('div', attrs={'id': 'articleBody'})

        article_link = article_content.find_all('a')
        attachment_url_pattern = re.compile(r'http://news.gdut.edu.cn/DepartmentUploadFiles/(.+)/files/(.+)')
        for link in article_link:
            if 'http://news.gdut.edu.cn/DepartmentUploadFiles' not in link['href']:
                printf('%s do not have file attachment' % (link['href']))
                continue

            match = attachment_url_pattern.match(link['href'])
            if not match:
                printf('%s do not have file attachment' % (link['href']))
                continue

            attachment_name = match.group(2)
            attachment_url = link['href']

            if '%' in attachment_name:
                attachment_name = unquote(attachment_name)

            article_attachment.append({'attach_name':attachment_name,'attach_url':attachment_url})

        info = ''.join(article_content.getText().split())
        info = info.replace(article_title, '')
        info = info.replace('单位：'+article_author,'')
        article_excerpt = article_excerpt.join(info[:150])

        article_result.append(
            {
                'url':article_url,
                'date':article_date,
                'title':article_title,
                'author':article_author,
                'excerpt':article_excerpt,
                'attachment':article_attachment
            }
        )
    return article_result


if __name__ == '__main__':

    welcome_string = [
        '周日：今天是周末的最后一天,好好珍惜时间\n',
        '周一：你从周末的作息里调整过来了吗？把上周的通知邮件都删了吧\n',
        '周二：吾日三省吾身\n',
        '周三：生活仍将继续\n',
        '周四：未来近在咫尺\n',
        '周五：明天就是周末了，加油！\n',
        '周六：你今天打算做什么？别浪费时间\n',
    ]

    welcome_content = welcome_string[ int( time.strftime('%w',time.localtime(time.time())) ) ]
    update_content = '最近更新：'+VERSION+':'+ANNOUNCEMENT+'\n'

    weather_data = get_weather_data()
    printf('get weather data finish')

    weather_render = jinja2_env.get_template('weather.html')

    now = weather_data['HeWeather5'][0]['now']
    forecast =  weather_data['HeWeather5'][0]['hourly_forecast'];
    weather_content = weather_render.render(now=now,forecast=forecast)

    index = get_index()
    article_data = parse_html(index)

    article_render = jinja2_env.get_template('article.html')
    if article_data:
        article_content = article_render.render(articles=article_data)
    else:
        article_content = article_render.render()

    mail_client = yagmail.SMTP(user=SEND_MAIL_USER, password=SEND_MAIL_PWD, host=SEND_MAIL_HOST, port=SEND_MAIL_PORT)
    mail_content = welcome_content + weather_content + update_content + article_content
    if len(argv) == 2 and '-t' in argv:
        for addr in SEND_TO_LIST_TEST:
            printf('sending[test user]: ' + addr)
            mail_client.send(addr, subject=SEND_MAIL_SUBJECT, contents=mail_content)
            time.sleep(1)
    else:
        for addr in SEND_TO_LIST:
            printf('sending : '+addr)
            mail_client.send(addr,subject=SEND_MAIL_SUBJECT,contents =mail_content)
            time.sleep(1)