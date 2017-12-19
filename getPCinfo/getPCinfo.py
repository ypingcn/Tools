#!/usr/bin/python3
# -*- coding: utf-8 -*-

def getSystem():
    with open('/etc/issue') as f:
        for line in f:
            info = ""
            for val in line.split():
                if not val.startswith('\\'):
                    info = info + val + " "
            return {'System Info':info}

def getMemory():
    with open('/proc/meminfo') as f:
        for line in f:
            if line.startswith('MemTotal'):
                num = int(line.split()[1])
                break
        num = '%.2f' % ( num / 1024.0 )
        return {'Total Memory':num+' MB '}
            
def getCPU():
    with open('/proc/cpuinfo') as f:
        for line in f:
            if line.startswith('model name'):
                info = line.split()
                return {'CPU':info[3]+" "+info[4]+" "+info[5]}

if __name__ == '__main__':
    result = {}
    result.update(getSystem())
    result.update(getMemory())
    result.update(getCPU())
    for key,value in result.items():
        print('%-15s :' % key,value)
