#!/usr/bin/python3
#! -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests,re,time

session = requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0 (Linux; U; Android 4.4.4; Nexus 5 Build/KTU84P) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'})


root_url = 'https://www.zhihu.com/question/52940752/answer/135966540'
#root_url = 'https://www.zhihu.com/question/51504667/answer/137780139'

def download_save_img(url):
    pattern = re.compile('https://pic([0-9]{1}).zhimg.com/([0-9a-zA-z_.-]+)')

    for val in url:

        #print(val)
        #hint: 如果只输出了四个地址，请检查接下来的四行内有无错误

        res = pattern.findall(val)
        img = session.get(url=val,timeout=5)
        with open(res[0][1],'wb')as file:
            file.write(img.content)
                

if __name__ == '__main__':

    start = time.time()

    s = session.get(root_url)

    if s.status_code == 200:

        soup = BeautifulSoup(s.content,'lxml')
        answer = soup.find('div',attrs={'class':'AnswerItem-content'})
        image = answer.find_all('img',attrs={'class':'origin_image zh-lightbox-thumb lazy'})

        print('%d image(s) found in %s' % (len(image),root_url))

        #text = answer.find('div',attrs={'class':'RichText'})
        #print(text.getText().replace(' ',''))

        result = []
        for val in image:
            result.append(val['data-actualsrc'])

        p = Pool()

        for i in range(4):
            p.apply_async(download_save_img,args=(result[i::4],))

        p.close()
        p.join()

        end = time.time()
        print('finish in %.2f second(s)'%(end-start))

        #with open('res.html','w') as file:
            #file.write(str(soup.prettify()))
