#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import re
import functools
import sqlite3
from bs4 import BeautifulSoup
import requests
import numpy as np
import matplotlib.pyplot as plt


class Bilibili:

    def __init__(self, name, keywords):
        self.con = sqlite3.connect(name)
        self.db = self.con.cursor()
        self.keywords = keywords

    def crawl(self):
        session = requests.Session()
        types = ['totalrank', 'click', 'pubdate', 'dm', 'stow']

        self.db.execute('''
                create table koi_information
                (id int primary key,
                link text,
                uploader text,
                uploadtime text,
                title text,
                description text,
                duration int,
                watch int,
                dm int)
                ''')
        self.con.commit()

        for keyword in self.keywords:
            page = 1
            typeid = 0

            for tp in types:
                os.mkdir(keyword+" "+tp)

            while typeid < 5:
                search = session.get("https://search.bilibili.com/all?keyword=" +
                                     keyword+"&page="+str(page)+"&order="+types[typeid])
                if search:
                    with open(keyword+" "+types[typeid]+"/"+str(page)+".html", "w") as file:
                        file.write(search.content.decode(encoding="utf-8"))
                if page < 50:
                    page = page + 1
                else:
                    typeid = typeid + 1
                    page = 1

            for tp in types:
                allfile = os.listdir(keyword+" "+tp)
                for file in allfile:
                    with open(keyword+" "+tp+"/"+file, "r") as source:
                        soup = BeautifulSoup(source.read(), "lxml")
                        matrixs = soup.find_all("li", attrs={"class": "video matrix "})
                        for matrix in matrixs:
                            head = matrix.find("a", attrs={"class": "title"})
                            link, vid = self.__href_format(head['href'])
                            title = self.__str_format(head['title'])
                            duration_text = matrix.find("span", attrs={"class": "so-imgTag_rb"}).text
                            duration = self.__to_second(self.__str_format(duration_text))
                            description = self.__str_format(matrix.find("div", attrs={"class": "des hide"}).text)
                            watch_text = matrix.find("span", attrs={"title": "观看"}).text
                            watch = self.__num_format(self.__str_format(watch_text))
                            dm_text = matrix.find("span", attrs={"title": "弹幕"}).text
                            dm = self.__num_format(self.__str_format(dm_text))
                            uploadtime_text = matrix.find("span", attrs={"title": "上传时间"}).text
                            uploadtime = self.__str_format(uploadtime_text)
                            uploader_text = matrix.find("span", attrs={"title": "up主"}).text
                            uploader = self.__str_format(uploader_text)
                            try:
                                print("try saving " + vid)
                                self.db.execute("insert into koi_information values(?,?,?,?,?,?,?,?,?)",
                                                (vid, link, uploader, uploadtime, title,
                                                 description, duration, watch, dm))
                            except Exception as e:
                                print("exist or something wrong : " ,e)
                            self.con.commit()

    def show(self):
        release_date = [
            "2016-10-11", "2016-10-18", "2016-10-25", "2016-11-01", "2016-11-08", "2016-11-15",
            "2016-11-22", "2016-11-29", "2016-12-06", "2016-12-13", "2016-12-20"
        ]

        release_rate = [10.2, 12.1, 12.5, 13.0, 13.3, 13.6, 13.6, 16.1, 16.9, 17.1, 20.8]

        release_count = []
        for val in release_date:
            self.db.execute(
                "select title,uploadtime,link from koi_information "
                "where julianday(uploadtime) - julianday(?) < 7 and julianday(uploadtime) - julianday(?) >= 0",
                (val, val))
            cnt = len(self.db.fetchall())
            release_count.append(cnt)

        diff = 7
        all_count = []
        for val in release_count:
            all_count.append(val)

        while diff < 365:
            self.db.execute(
                "select title,uploadtime,link from koi_information "
                "where julianday(uploadtime) - julianday(?) < ? and julianday(uploadtime) - julianday(?) >= ?",
                (release_date[-1], 7 + diff, release_date[-1], 0 + diff))
            cnt = len(self.db.fetchall())
            all_count.append(cnt)
            diff = diff + 7

        self.db.close()

        plt.title("Upload Number in Bilibili & Audience Rating")
        x = range(1, len(release_count) + 1)
        ynum = np.array(release_count)
        plt.bar(x, ynum, width=0.5, align="center", color="gray")
        plt.xticks(x, x)
        for a, b in zip(x, ynum):
            plt.text(a, 5, "%.0f" % (b), ha="center", va="bottom", fontsize=10)
        plt.xlabel("Week")
        plt.ylabel("Upload Number")

        plt2 = plt.twinx()
        yrate = np.array(release_rate)
        plt2.plot(x, yrate, color="b", linestyle="-", marker="o")
        for a, b in zip(x, yrate):
            plt2.text(a, b, "%.2f%%" % b, ha="center", va="bottom", fontsize=10)
        plt.show()

    @staticmethod
    def __str_format(val):
        if not val:
            return None
        return val.replace("\t", "").replace("\n", "")

    @staticmethod
    def __href_format(val):
        if not val:
            return None
        pattern = re.compile(".*(www.bilibili.com/video/av([0-9]+)).*")
        result = pattern.match(val)
        if result:
            return result.group(1), result.group(2)
        else:
            return None

    @staticmethod
    def __to_second(val):
        if not val:
            return 0
        num = val.split(":")
        #return int(list(itertools.accumulate(num, lambda a, b: int(a) * 60 + int(b)))[1])
        return functools.reduce(lambda x,y : int(x)*60+int(y) , num)

    @staticmethod
    def __num_format(val):
        if not val:
            return 0
        if "万" in val:
            num = val.split("万")
            return int(float(num[0]) * 10000)
        else:
            return int(val)


if __name__ == "__main__":
    b = Bilibili("test.db", ["gakki舞"])
    b.crawl()
    b.show()
