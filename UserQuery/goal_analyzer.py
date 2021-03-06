# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 20:13:56 2013

@author: Javier Suarez

This script analyzes a user query through different levels of abstraction, 
ranging from natural language processing to identify the user's intentions 
and goals
"""
from matplotlib import pyplot
import matplotlib as mpl
import building_train_data as bltd
import pickle
import time
import random
from textblob import TextBlob

def accuracy(classifier):
    """
    This function evaluates the accuracy of the implemented classifier 
    Return the trained classifier 
    """
    t0 = time.clock()
    print "Loading Classifier, this may take several minutes, please wait..."
    cl = loadTrainedClassifier(classifier)
    print "Most predictive features: ", cl.show_informative_features(20)
    print  "\tClassifier loaded on", time.clock() - t0, "seconds."
    print 
    
    t0 = time.clock()
    print "Start data load, this may take several minutes, please wait..."
    db = bltd.dbClient()  
    test = db.test
    cursor = test.find({}, {"triGram" : 1})
    
    crs = list(cursor)    
    random.shuffle(crs)
    # split into 90% training and 10% test sets
    p = int(len(crs) * .01)
    cr_test = crs[0:p]        
        
    print "Test", len(cr_test)
    
    test_data = []
    t = ""
    label = "pos" 
    for td in cr_test:
        tgram = td["triGram"]        
        #print tgram
        for tg in tgram:
            d = '-'.join(tg)
            t = t + " " + d
        test_data.append((t, label))
        t = ""
    print "Test data loaded on", time.clock() - t0, "seconds."   
    #print test_data  
    print 
    t0 = time.clock()
    print "Performing test, please wait..."
    print "Accuracy: ", cl.accuracy(test_data)    
    print "Test done on", time.clock() - t0, "seconds."   


def testQueries(classifier):
    """
    This function classifies the user query as appropriate: "Pos" or "Neg".
    """
    t0 = time.clock()
    print "Start testing, this may take several minutes, please wait..."
    db = bltd.dbClient()  
    aol_goals = db.aol_goals
    cursor = aol_goals.find()     
    for c in cursor:
        ID = c["_id"]
        query = c["query"]   
        pos = c["pos"]   
        tgram = c["triGram"]
        t = ""
        for tg in tgram:
            d = '-'.join(tg)
            t = t + " " + d

        prob_dist = classifier.prob_classify(t)
        label = classifier.classify(t)

        goal = {"ID" : str(ID),
                "query": str(query),
                "post" : pos, 
                "label" : str(label),
                "prob_dist_pos" : prob_dist.prob("pos"),
                "prob_dist_neg" : prob_dist.prob("neg")
        }    
        
        accuracy_test = db.accuracy_test
        accuracy_test.insert(goal)
    print "Test done on", time.clock() - t0, "seconds."   

def testQuery(classifier, query):
    t = bltd.triGram(query) 
    classifier.show_informative_features(40)
    prob_dist = classifier.prob_classify(t)
    print    
    print "Max Probability Distribution:", prob_dist.max()
    print "Pos:", prob_dist.prob("pos")
    print "Neg:", prob_dist.prob("neg")
    print
    print
    return prob_dist.prob(str(prob_dist.max())), prob_dist.max()


def updateClassifier(query, classifier, label):
    """
    This feature allows updating the classifier based on new vocabulary (queries not seen in the training phase).
    """
    tgram = bltd.triGram(query)
    new_data = [(tgram , label)]
    classifier.update(new_data)
    
    
def saveTrainedClassifier(path, classifier, classifier_name):
    f = open(classifier_name, 'wb')
    pickle.dump(classifier, f)
    f.close()
    

def loadTrainedClassifier(classifier_name):
    """
    This function allows to load a trained classifier.
    Return: loaded classifier
    """
    f = open(classifier_name)
    loaded_cl = pickle.load(f)
    f.close()
    return loaded_cl
    
    
def viewProbabilityDistribution(prob_dist_max, tag):
    if(tag.strip(' \t\r\n') == 'pos'):
        b = 1 - round(prob_dist_max,2)
    else: 
        b = round(prob_dist_max,2)
        
    # Make a figure and axes with dimensions as desired.
    fig = pyplot.figure(figsize=(8,3))
    ax1 = fig.add_axes([0.09, 0.80, 0.82, 0.15])
    ax2 = fig.add_axes([0.05, 0.475, 0.9, 0.15])
    
    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    
    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                    norm=norm,
                                    orientation='horizontal')
    space = "                                                                                                                                             "
    cb1.set_label('No ' + space + ' Yes')
    
    # The second example illustrates the use of a ListedColormap, a
    # BoundaryNorm, and extended ends to show the "over" and "under"
    # value colors.
    cmap = mpl.colors.ListedColormap(['#2EFEF7', '#DF01D7'])
    cmap.set_over('0.25')
    cmap.set_under('0.75')
    
    # If a ListedColormap is used, the length of the bounds array must be
    # one greater than the length of the color list.  The bounds must be
    # monotonically increasing.
    bounds = [0, b, 1]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    cb2 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                         norm=norm,
                                         # to use 'extend', you must
                                         # specify two extra boundaries:
                                         #boundaries=[0]+bounds+[13],
                                         extend='both',
                                         ticks=bounds, # optional
                                         spacing='proportional',
                                         orientation='horizontal')
    cb2.set_label('Degree of Intentional Explicitness of an  Query')