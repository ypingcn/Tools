#!/usr/bin/python3
# -*- coding:utf-8 -*-

import re,xlwt

common = re.compile(u'您尾号(\d{4})卡(\d{1,2})月(\d{1,2})日([\d:]+)(.+?)([\d.,]+)元，余额([\d.,]+)元。【工商银行】')
notify_fee = re.compile(u'您尾号(\d{4})卡(\d{1,2})日([\d:]+)(.+?)([\d.,]+)元，余额([\d.,]+)元。【工商银行】')

xls = xlwt.Workbook()
table = xls.add_sheet(u'账单')
table.write(0,3,'方式')
table.write(0,4,'用途')
table.write(0,5,'余额')
table.write(0,6,'备注')

def f(month,day,reason,fee,remain,line):
    while(len(month) < 2):
        month = '0' + month
    while(len(day) < 2):
        day = '0' + day

    if '.' in fee:
        fee = float(fee.replace(',',''))
    else:
        fee = int(fee.replace(',',''))
    if '出' in reason:
        fee = -fee

    remain = float(remain.replace(',',''))
    remain = round(remain,2)

    table.write(line,1,month+day)
    table.write(line,2,fee)
    table.write(line,3,reason)
    table.write(line,5,remain)


if __name__ == '__main__':
    with open('bank.txt','r') as file:
        current = 1
        for line in file.readlines():
            line = line.strip()
            r1 = common.match(line)
            r2 = notify_fee.match(line)
            if r1:
                f(r1.group(2),r1.group(3),r1.group(5),r1.group(6),r1.group(7),current)
                current = current + 1
            elif r2:
                f('',r2.group(2),r2.group(4),r2.group(5),r2.group(6),current)
                current = current + 1
            else:
                print('other #' + line.strip())

    xls.save('result.xls')
   
