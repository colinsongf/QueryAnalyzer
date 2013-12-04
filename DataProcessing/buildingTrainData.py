# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:10:12 2013

@author: javier
"""
from textblob import TextBlob
import time

path = "/home/javier/Desarrollo/PythonProject/"
goals = "aolGoals.txt"

def writeLineOn(file_name, line):
    document = open(file_name, 'a')    
    document.write(line + "\n")
    document.close

def addPositiveLabel():
    train = []
    print "Add Positive label to query, please wait..."
    for line in open(path + goals):
        query = line.strip(' \t\r\n')
        tag = "pos"
        data = []
        data.append(query)
        data.append(tag)
        train.append(tuple(data))
        print train[:10]
    print "finished"
    return train


def posTagging(train, file_name):
    t0 = time.clock()
    print "Performing POS Tagging, please wait..."
    document = open(file_name, 'a')   
    for tr in train:
        #print tr.strip(' \t\r\n')
        t = TextBlob(tr.strip(' \t\r\n'))    
        postg = t.tags    
        p = ''
        #print postg
        for pt in postg:
            p = p + str(pt[1]) + " "
        #print p
        document.write(p + "\n")
    document.close    
    print "Finished on", time.clock() - t0, "seconds."


    
    
