#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time

LOGIN_DATA = {}
LOGIN_DATA['__VIEWSTATE'] = '/wEPDwUKLTQwOTA4NzE2NmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFI2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkQ2hlY2tCb3gxBufpEJuDDaf6eTj0A4Cn2Erf8u98KcGrQqATTB3mEaQ='
LOGIN_DATA['__EVENTVALIDATION'] = '/wEWBQKb37HjDwLgvLy9BQKi4MPwCQL+zqO2BAKA4sljg4IvzC7ksG01o7aN0RZUOKEC4lV0bTeXI4zrbaQsj0c='

# 联系校内人员获取账号密码，此处的账号密码无效
LOGIN_DATA['ctl00$ContentPlaceHolder1$userEmail'] = 'test'
LOGIN_DATA['ctl00$ContentPlaceHolder1$userPassWord'] = 'test'

LOGIN_DATA['ctl00$ContentPlaceHolder1$CheckBox1'] = 'on'
LOGIN_DATA['ctl00$ContentPlaceHolder1$Button1'] = '%E7%99%BB%E5%BD%95'

#发送者邮箱
SEND_MAIL_USER = 'account'
#发送者邮箱对应的密码
SEND_MAIL_PWD = 'password'
#腾讯企业邮箱
SEND_MAIL_HOST = 'smtp.exmail.qq.com'
#发送端口
SEND_MAIL_PORT = 465
#邮件正文标题
SEND_MAIL_SUBJECT = time.strftime("%Y-%m-%d",time.localtime()) + '@今日校内通知'
#接收邮件的人
SEND_TO_LIST = [
   'mail@mail.com',
]
#用来测试接收邮件的用户，加上-t选项即可
SEND_TO_LIST_TEST = ['mail@mail.com']
#和风天气API地址
WEATHER_API_URL = 'https://free-api.heweather.com/v5/weather?'
#天气API城市，拼音汉字均可
WEATHER_API_CITY = 'guangzhou'
#免费版key，一天4000次调用，注册后可用
WEATHER_API_KEY = 'key'
