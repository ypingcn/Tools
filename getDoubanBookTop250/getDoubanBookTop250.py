#!/usr/bin/python3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests

def download_html(url):
    if not url :
        print("empty url,stop download")
        return

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    html = requests.get(url,headers=headers)

    if html.status_code == 200:
        return html.content
    return

def parse_html(content):
    if not content:
        print("empty content,stop parse")
        return

    soup = BeautifulSoup(content,"lxml");
    book_list = soup.find("div",attrs={"class":"article"})

    for item in book_list.find_all("tr",attrs={"class":"item"}):

        name = item.div.a.getText().split()

        website = item.a['href']

        info = item.p.getText()

        rating = item.find("span",attrs={"class":"rating_nums"}).getText();

        quote = ""
        if item.find("p",attrs={"class":"quote"}):
            quote = item.find("p",attrs={"class":"quote"}).getText().strip();

        with open("result.md","a") as file:
            title = "".join(name)

            file.write(" **[ " + title + " ](" + website + ")** (" + rating + ")\n\n")
            file.write("> " + quote + "\n\n")
            file.write(info+"\n\n")

if __name__ == "__main__":

    ROOT_URL = "https://book.douban.com/top250?start=";

    for start in range(0,250,25):
        print(ROOT_URL+str(start))
        html = download_html(ROOT_URL+str(start))
        parse_html(html)

    print('done');