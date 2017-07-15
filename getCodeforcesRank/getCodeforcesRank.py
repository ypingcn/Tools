#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib import request
import json
#import random,time

file = open("cfrank.txt","r")

result = []
for line in file:
    line = line.replace("\n","")
    if line[0] == '#':
        continue
    name,account = line.split("****")
    with request.urlopen("http://codeforces.com/api/user.rating?handle="+account) as f:
        if f.status == 200:
            data = f.read().decode()
            rank = json.loads(data)
            if rank['status'] == "FAILED":
                print(rank['comment'])
            elif rank['status'] == 'OK' and len(rank['result']) >= 1:
                print(name,account,rank['result'][-1]['newRating'])
                add = (name,account,rank['result'][-1]['newRating'])
                result.append(add)

    #time.sleep(random.randint(1,3))

result = sorted(result,key=lambda x : x[2])

print('---')

out = open("result.txt","w")

for val in result:
    print(val[2],val[0])
    out.write(str(val[2]))
    out.write(str(val[0])+"\n")

