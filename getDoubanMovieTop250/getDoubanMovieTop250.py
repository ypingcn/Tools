#!/usr/bin/python3
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import requests,re

ROOT_URL = 'https://movie.douban.com/top250'

def download_html(url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0'}
    return requests.get(url,headers=headers).content

def parse_html(html):
    soup = BeautifulSoup(html,'lxml')
    movie_list = soup.find('ol',attrs={'class':'grid_view'})
    
    result = []

    for val in movie_list.find_all('li'):
        rank = val.find('em').getText()
        rating = val.find('span',attrs={'class':'rating_num'}).getText()

        description = val.find('p',attrs={'class':'quote'})
        if description:
            description = description.find('span').getText()

        info = val.find('a')
        url = info['href']        
        name = info.find('img')['alt']
        cover = info.find('img')['src']

        add = {}
        add['rank'] = rank
        add['rating'] = rating
        add['name'] = name
        add['cover'] = cover
        add['url'] = url
        if description:
            add['description'] = description
        result.append(add)

    return result


if __name__ == '__main__':

    result = []
    with open('result.md','w') as file:
        for start in range(0,250,25):
            url = ROOT_URL + "?start=" + str(start)
            print(url)

            html_data = download_html(url)  
    
            for val in parse_html(html_data):
                #file.write('![](' + val['cover'] + ')\n')
                file.write(val['rank']+'. [**'+val['name']+'**]('+val['url']+') ( '+val['rating']+' )\n')
                if 'description' in val:
                    file.write(val['description']+'\n')

