#!/usr/bin/python

import sys
import re

a = re.compile("(.*)\|\s+([\w]+)\s+\|\s+([0-9]+)")
b = re.compile("([\w]+)\s+([0-9]+)")

arr = dict()


for line in sys.stdin:
    if a.search(line):
        x = a.search(line)
        if (arr.has_key(x.group(2))):
            tup = [(x.group(2),x.group(3))]
            if (x.group(1)):
                print x.group(1)+": "+x.group(2)+" "+str(int(x.group(3)) - int(arr[x.group(2)]))
            else:
                print x.group(2)+" "+str(int(x.group(3)) - int(arr[x.group(2)]))
            arr.update(tup)
        else:
            arr[x.group(2)] = x.group(3)

    elif b.search(line):
        x = b.search(line)
        if (arr.has_key(x.group(1))):
            tup = [(x.group(1),x.group(2))]
            print x.group(1)+" "+str(int(x.group(2)) - int(arr[x.group(1)]))
            arr.update(tup)
        else:
            arr[x.group(1)] = x.group(2)

    else:
        print "Not match"
        
        

