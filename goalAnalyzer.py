# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 20:13:56 2013

@author: Javier Suarez

This script analyzes a user query through different levels of abstraction, 
ranging from natural language processing to identify the user's intentions 
and goals
"""

from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob

import time
import buildingTrainData as bltd

#This function initializes the data sets of training and testing
def init():

    test = [
         ("how to cut hair", 'pos'),
         ('w2express.com','neg'),
         ('how to play cornhole', 'pos'),
         ('safety ideas','neg'),
         ("check your claim status", 'pos'),
         ('buying rental cars','pos'),
         ('canon','neg'),
         ('changing your password','pos'),
         ('park central hotel convention center','neg'),         
         ('google','neg')
    ] 
    path = '/media/University/University Disc/2-Master/Master Thesis/Ejecución Tesis/Desarrollo/PythonProjects/Data/'
    positives = 'positiveSample.txt'
    negatives = 'negativeSample.txt'
    
    train = bltd.renderTrainData(path, positives, negatives)
    
    cl = accuracy(train, test)
    return cl
    
    

#This function evaluates the accuracy of the implemented classifier 
#Return the trained classifier 
def accuracy(train, test):
    t0 = time.clock()
    print "Start trining of NaiveBayesClassifier, this may take several minutes, please wait..."
    cl = NaiveBayesClassifier(train)
    print  "\tTrainig done on", time.clock() - t0, "seconds."
    print 
    print "\tAccuracy: ", cl.accuracy(test)
    cl.show_informative_features(20)
    print
    return cl

#This function performs a Part-of-speech taggin out from a collection of documents.
def posTaggingCollection(train_file):
    postags_train = []
    for trf in train_file:        
        #print trf[0]
        data = []
        t = TextBlob(trf[0])
        postg = t.tags
        p = ''
        for pt in postg:
            p+= str(pt[1]) + " "
        #print p
        data.append(p)
        data.append(trf[1])
        postags_train.append(tuple(data))
    #print postags_train
    return postags_train

#This function performs a Part-of-speech taggin per sentence (document).
def posTaggingDocument(sentence):
    t = TextBlob(sentence)
    p = ''
    for pt in t.tags:
        p+= str(pt[1]) + " "
    return p
    
#This function classifieds the user query as appropriate: "Pos" or "Neg".
def test(query, classifier):
    p = posTaggingDocument(query)
    classifier.classify(p)
    prob_dist = classifier.prob_classify(p)
    print "Max Probability Distribution:", prob_dist.max()
    print "Pos:", prob_dist.prob("pos")
    print "Neg:", prob_dist.prob("neg")
    return prob_dist.max()

#This feature allows updating the classifier based on new vocabulary (queries not seen in the training phase).
def updateClassifier(query, classifier, label):
    post = posTaggingDocument(query)
    new_data = [(post, label)]
    classifier.update(new_data)

#The following commands allow to observe the operation of this script.
"""    
>>> import goalAnalyzer as ga
>>> train, test = ga.init()
>>> train = ga.posTaggingCollection(train)
>>> test = ga.posTaggingCollection(test)
>>> cl = ga.accuracy(train, test)
>>> query = 'where to find info on aquarium in atlanta ga' #Example
>>> label = ga.test(query, cl)
>>> updateClassifier(query, cl, label)
>>> cl.accuracy(test)    
""" 


    
