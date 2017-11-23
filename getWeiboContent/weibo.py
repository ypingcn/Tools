#!/usr/bin/python3
# -*-coding:utf-8-*-

import requests,os,time,random,argparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Weibo(object):
    def __init__(self,url,type='all'):
        self.url = url
        self.type = type
        self.account = input('input your account\n')
        self.password = input('input your password\n')
        self.firefox = webdriver.Firefox(executable_path=os.getcwd()+'/geckodriver')


    def login(self):
        login_url = 'http://www.weibo.com/login.php'
        self.firefox.get(login_url)
        time.sleep(random.randint(1,5))
        self.firefox.find_element_by_xpath('//*[@id="loginname"]')\
            .send_keys(self.account)
        self.firefox.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')\
            .send_keys(self.password)  # 输入密码
        self.firefox.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a')\
            .click()  # 点击登陆
        time.sleep(random.randint(1, 5))
        cookies = self.firefox.get_cookies() #导出cookie
        self.session = requests.Session()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'],cookie['value'])


    def parse(self,html):
        soup = BeautifulSoup(html, 'lxml')
        weibos = soup.find_all('div', attrs={'class': 'WB_detail'})

        if not weibos:
            return False

        for weibo in weibos:
            id = weibo.find('div', attrs={'class': 'WB_from S_txt2'})
            info = weibo.find('div', attrs={'class': 'WB_info'})
            content = weibo.find('div', attrs={'class': 'WB_text W_f14'})
            content_date = weibo.find('a', attrs={'class': 'S_txt2'})
            # print(id.a['href'])
            # print(info.getText().replace(' ', '').replace('\n', ''))
            print(content.getText().replace(' ', '').replace('\n', ''))
            # print(content_date.getText())
            media = weibo.find('div', attrs={'class': 'media_box'})
            expand = weibo.find('div',attrs={'class':'WB_expand S_bg1'})

            if media:
                pics = media.find_all('img')
                for pic in pics:
                    pass

            if expand:
                pass

        return True


    def download(self):
        page = 1

        # 筛选原创微博
        if self.type == 'origin':
            traverse_url = self.url + '?from=myfollow_all&profile_ftype=1&is_ori=1'
        # 全部微博
        elif self.type == 'all':
            traverse_url = self.url + '?from=myfollow_all&is_all=1'
        else:
            print('unsupported type: '+self.type)

        self.firefox.get(traverse_url+'&page='+str(page))
        self.__to_end__()
        while(self.parse(self.firefox.page_source)):
            time.sleep(5)
            page = page + 1
            self.firefox.get(traverse_url+'&page='+str(page))
            self.__to_end__()

        self.firefox.close()

    def __to_end__(self):
        self.firefox.find_element_by_xpath('/html/body').send_keys(Keys.END)
        time.sleep(1)
        self.firefox.find_element_by_xpath('/html/body').send_keys(Keys.END)
        time.sleep(1)
        self.firefox.find_element_by_xpath('/html/body').send_keys(Keys.END)
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',help='weibo URL,make sure you input a vaild URL')
    parser.add_argument('--type',help='\'origin\' or \'all\',all for default')

    args = parser.parse_args()

    wb = Weibo(args.url)
    wb.login()
    time.sleep(5)
    wb.download()

