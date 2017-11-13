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
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import re,os,json,time,redis,yagmail,requests




class SchoolNewsMail:
    def __init__(self):
        self.ROOT_URL = 'http://news.gdut.edu.cn'

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0")

        self.jinja2_env = Environment(
            loader=FileSystemLoader(os.getcwd() + '/template'),
            autoescape=select_autoescape(['html'])
        )

        self.browser = webdriver.PhantomJS(desired_capabilities=dcap)

        self.weather_data = []
        self.article_data = []
        self.update_content = ''

        self.mail_content = ''

    def get_weather_data(self):
        request_url = WEATHER_API_URL + 'city=' + WEATHER_API_CITY + '&&key=' + WEATHER_API_KEY
        request = requests.get(request_url)
        data = []
        if request.status_code == 200:
            data = json.loads(request.content.decode(encoding='utf-8'))
        self.weather_data = data

    def get_update_data(self):
        self.update_content = '最近更新：'+VERSION+':'+ANNOUNCEMENT+'\n'

    def login(self):

        self.printf('login begin')

        try:
            self.browser.get(self.ROOT_URL+'/UserLogin.aspx')
            self.browser.find_element_by_id('ContentPlaceHolder1_userEmail').send_keys(LOGIN_ACCOUNT)
            self.browser.find_element_by_id('ContentPlaceHolder1_userPassWord').send_keys(LOGIN_PASSWORD)
            time.sleep(2)
            self.browser.find_element_by_id('ContentPlaceHolder1_userPassWord').send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            print(e)

        time.sleep(3)

        self.browser.save_screenshot("index.png")  # 截图保存

        self.printf('login end')

    def parse(self):

        self.printf('parse begin')

        self.browser.get(self.ROOT_URL + '/ArticleList.aspx?category=4')
        self.browser.save_screenshot('parse.png')

        index = self.browser.page_source

        html_soup = BeautifulSoup(index, 'lxml')
        articles = html_soup.find('div', attrs={'class': 'articles'})

        if not articles:
            self.printf('article not found')
            return

        article_result = []

        for val in articles.find_all('p'):
            article_id = val.find('a')['href'][-6:]
            article_url = self.ROOT_URL + val.find('a')['href'][1:]
            article_date = val.find_all('span')[1].getText()[:-1]
            article_title = val.find('a')['title']
            article_author = val.span['title']
            article_attachment = []
            article_excerpt = ''

            self.printf(article_title)

            if self.article_id_exist(article_id):
                self.printf('article exist in database %s' % (article_title))
                continue

            self.browser.get(article_url)

            article_soup = BeautifulSoup(self.browser.page_source, 'lxml')
            article_content = article_soup.find('div', attrs={'id': 'articleBody'})

            article_link = article_content.find_all('a')
            attachment_url_pattern = re.compile(r'http://news.gdut.edu.cn/DepartmentUploadFiles/(.+)/files/(.+)')
            for link in article_link:
                if 'http://news.gdut.edu.cn/DepartmentUploadFiles' not in link['href']:
                    self.printf('%s do not have file attachment' % (link['href']))
                    continue

                match = attachment_url_pattern.match(link['href'])
                if not match:
                    self.printf('%s do not have file attachment' % (link['href']))
                    continue

                attachment_name = match.group(2)
                attachment_url = link['href']

                if '%' in attachment_name:
                    attachment_name = unquote(attachment_name)

                article_attachment.append({'attach_name': attachment_name, 'attach_url': attachment_url})

            info = ''.join(article_content.getText().split())
            info = info.replace(article_title, '')
            info = info.replace('单位：' + article_author, '')
            article_excerpt = article_excerpt.join(info[:150])

            article_result.append(
                {
                    'url': article_url,
                    'date': article_date,
                    'title': article_title,
                    'author': article_author,
                    'excerpt': article_excerpt,
                    'attachment': article_attachment
                }
            )

        self.article_data = article_result

        self.printf('parse end')

    def render(self):
        weather_render = self.jinja2_env.get_template('weather.html')

        if self.weather_data:
            now = self.weather_data['HeWeather5'][0]['now']
            forecast = self.weather_data['HeWeather5'][0]['hourly_forecast'];
            weather_content = weather_render.render(now=now, forecast=forecast)
        else:
            weather_content = article_render.render()

        article_render = self.jinja2_env.get_template('article.html')
        if self.article_data:
            article_content = article_render.render(articles=self.article_data)
        else:
            article_content = article_render.render()

        self.mail_content = weather_content + article_content + self.update_content

    def send_mail(self,type):
        mail_client = yagmail.SMTP(user=SEND_MAIL_USER, password=SEND_MAIL_PWD, host=SEND_MAIL_HOST,
                                   port=SEND_MAIL_PORT)
        if(type == 1):
            for addr in SEND_TO_LIST_TEST:
                printf('sending[test user]: ' + addr)
                mail_client.send(addr, subject=SEND_MAIL_SUBJECT, contents=self.mail_content)
                time.sleep(1)
        else:
            for addr in SEND_TO_LIST:
                printf('sending : ' + addr)
                mail_client.send(addr, subject=SEND_MAIL_SUBJECT, contents=mail_content)
                time.sleep(1)

    def article_id_exist(self,id):

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

    def printf(self,string):
        if string:
            print(time.strftime("%Y-%m-%d %H:%M:%S : ", time.localtime()) + string)


obj = SchoolNewsMail()
obj.get_weather_data()
obj.login()
obj.parse()
obj.render()
obj.get_update_data()
if len(argv) == 2 and '-t' in argv:
    obj.send_mail(1)
else:
    obj.send_mail(0)
