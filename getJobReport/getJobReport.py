#!/usr/bin/python3

from urllib import request
import requests,re,time,random

base_url = "http://www.gradjob.com.cn/News/2016/"
request_url = request.Request(base_url + "jyzl")
request_url.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0")

final_result = []

with request.urlopen(request_url) as f:
    print('status ',f.status)
    if f.status == 200:
        data = f.read()
        save = open("html.txt","w")
        save.write(data.decode(encoding="utf-8"))
        pattern = re.compile(u'<a href="file/([0-9]{5}).pdf">([\u4e00-\u9fa5]+)</a>')
        for line in open("html.txt","r"):
            #print(line)
            result = pattern.findall(line)
            if result:
                final_result.append(result[0])
for pdf_id,name in final_result:
    print(name,"pdf download start")
    pdf_2015_url = base_url + "2015/file/" + pdf_id + ".pdf"
    pdf_2015_save = open(name+"-2015.pdf","wb")
    with pdf_2015_save as file:
        file.write(requests.get(pdf_2015_url).content)
    
    #time.sleep(random.randint(1,3))

    pdf_2016_url = base_url + "file/" + pdf_id + ".pdf"
    pdf_2016_save = open(name+"-2016.pdf","wb")
    with pdf_2016_save as file:
        file.write(requests.get(pdf_2016_url).content)
    print(name,"pdf download finish")
