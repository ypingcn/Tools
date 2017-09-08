#!/usr/bin/python3
# -*- coding:utf-8 -*-

'''
【留意！！】
启动程序前要先留意 locale (Linux 命令)输出的内容是否为zh_CN.UTF-8
建议写 shell 脚本启动并在运行前 export LC_ALL=zh_CN.UTF-8 
'''

from bs4 import BeautifulSoup
import requests,re,yagmail,time

ROOT_URL = 'http://news.gdut.edu.cn/'

#HttpFox

LOGIN_DATA = {}
LOGIN_DATA['__VIEWSTATE'] = '/wEPDwUKLTQwOTA4NzE2NmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFI2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkQ2hlY2tCb3gxBufpEJuDDaf6eTj0A4Cn2Erf8u98KcGrQqATTB3mEaQ='
LOGIN_DATA['__EVENTVALIDATION'] = '/wEWBQKb37HjDwLgvLy9BQKi4MPwCQL+zqO2BAKA4sljg4IvzC7ksG01o7aN0RZUOKEC4lV0bTeXI4zrbaQsj0c='

# 联系校内人员获取账号密码，此处的账号密码无效
LOGIN_DATA['ctl00$ContentPlaceHolder1$userEmail'] = 'account'
LOGIN_DATA['ctl00$ContentPlaceHolder1$userPassWord'] = 'password'

LOGIN_DATA['ctl00$ContentPlaceHolder1$CheckBox1'] = 'on'
LOGIN_DATA['ctl00$ContentPlaceHolder1$Button1'] = '%E7%99%BB%E5%BD%95'

session = requests.Session()

#发送者邮箱
SEND_MAIL_USER = 'mail@mail.com'
#发送者邮箱对应的密码
SEND_MAIL_PWD = 'password'
#腾讯企业邮箱
SEND_MAIL_HOST = 'smtp.exmail.qq.com'
#发送端口
SEND_MAIL_PORT = 465
#邮件正文标题
SEND_MAIL_SUBJECT = time.strftime("%Y-%m-%d",time.localtime()) + '@今日校内通知'
#接收邮件的人
SEND_TO_LIST = ['mail@mail.com']


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
    index_content = html_login()
    mail_content = []

    if index_content:
        html_parse(index_content,mail_content)

    if mail_content:
        client = yagmail.SMTP(user=SEND_MAIL_USER, password=SEND_MAIL_PWD, host=SEND_MAIL_HOST, port=SEND_MAIL_PORT)
        for addr in SEND_TO_LIST:
            client.send(addr,subject=SEND_MAIL_SUBJECT,contents =mail_content)
            time.sleep(2)

