# -*- coding: utf-8 -*-
"""
    Student:    Kevin O'Mahony
    ID:         R00105946
    Date:       17-03-2017
    
"""
##############################################################

import os
import string
import math
import ConfigParser

##############################################################    

config = ConfigParser.ConfigParser()
config.read("bayes.ini")

SYMBOLS = '{}()[],.:;+-*/&|<>=~$'  
DIGITS  = '1234567890'
negativeWords = ['Not','not','no','No'] 
stopWords = ""

##############################################################
    
def containsAny(astr, strset):
    notrans = string.maketrans('', '')
    return len(strset) != len(strset.translate(notrans, astr))

# Generate space separated ngrams from list of words
# Return list of ngrams
#
def ngrams(n,words):
    retList = [] 
    for i in range(len(words)-n+1): 
        s = ""
        j = i
        while j < i + n:
            s = s + " " + words[j] 
            j = j + 1
        retList.append(s[1:]) # remove the leading space
        i = i + 1
    return retList
    
# Convert any negation words, W (defined in negativeWords) found
# in input word list into Not_W form
# Repeat replacements until first punctuation mark seen.
# Return transformed word list
#
def negate(words):
    i = 0
    negating = False
    while (i < len(words)-1):
        aWord = words[i]
        if (negating == True and not containsAny(aWord,string.punctuation)):
            words[i] = "Not_"+words[i]
        else:
            negating = False
        if (aWord in negativeWords):
            negating = True
            words[i+1] = "Not_"+words[i+1]
            i += 1
        i += 1
    return words
    
# Pre-process input word list according to configuration settings
# Return transformed word list
#
def preprocess(words):         
    if config.getboolean('Parameters','Lowercase') == True:
        words = [w.lower() for w in words]
        
    if config.getboolean('Parameters','RemovePunctuation') == True:
        words = [w.translate(None, SYMBOLS).strip() for w in words]
        
    if config.getboolean('Parameters','RemoveDigits') == True:
        words = [w.translate(None, DIGITS).strip() for w in words]
        
    if config.getboolean('Parameters','StopWords') == True:
        global stopWords
        words = [w for w in words if w not in stopWords]
               
    if config.getboolean('Parameters','Negation') == True:
        words = negate(words) 
   
    if config.getboolean('Parameters','Ngrams') == True:
        n = config.getint('Parameters','NgramSize')
        words = ngrams(n,words)
        
    if config.getboolean('Parameters','SingleOccurrencePerDoc') == True:
        words = set(words) 
        
    return(words)

# Update input word frequency dictionary and vocab set
# for text in given filename
#
def updateVocabAndCounts(filename,vocab,dictCount):
    f = open(filename,'r')
    contents = f.read()   
    f.close()

    if config.getboolean('Parameters','PartOfSpeech') == True:
        tb = TextBlob(contents)
        pos = tb.tags
        words = [w[0] for w in pos if w[1][1] in 'JRVN']
    else:
        words = contents.split()
  
    words = preprocess(words)
    
    for w in words:      
        vocab.add(w)
        dictCount.setdefault(w,0)
        dictCount[w] += 1            

# Classify document as either positive or negative based
# on word probability dictionary values
#            
def classifyDoc(filename,probWordForPositive,probPositive,
                probWordForNegative,probNegative):
    f = open(filename,'r')
    contents = f.read()
    words = contents.split()
    f.close()
        
    words = preprocess(words)
        
    probDocPositive = probPositive
    probDocNegative = probNegative
        
    for w in words:
        if (w in probWordForPositive):
            probDocPositive += probWordForPositive[w]
        if (w in probWordForNegative):
            probDocNegative += probWordForNegative[w]
        
    if (probDocPositive > probDocNegative):
        return(1)
    else: 
        return(-1)

# Read stop words file specified in config file into stopWords string
#
def getStopWords():   
    filename = config.get('Data', 'StopWordFile')
    f = open(filename)
    global stopWords
    stopWords = f.read()
    f.close()
    return stopWords

# Return the top n highest elements of dictionary, A based on 
# dictionary's values.
#
def reduceW(A, n):
    dd = sorted(A.iteritems(), key=itemgetter(1), reverse=True)[:n]
    result_dict = {}
    for t in dd:
        result_dict[t[0]] = t[1]
    return result_dict

# For every file in specified path directory
# update our word count dictionary and overall vocab set
# return the count of documents processed
#    
def trainNB(path,vocab,wordCountDict):
    docCount = 0
    listing = os.listdir(path)
    for eachFile in listing:
        docCount += 1
        updateVocabAndCounts(path+eachFile,vocab,wordCountDict)
    return(docCount) 

# Classify every file in the specified directory, 
# given expected sentiment and our trained probability dictionaries
# Return the number of documents processed and the
# number of correctly classified
#
def doClassification(dirPath,sentiment,
                     probWordForPositive,probPositive,
                     probWordForNegative,probNegative):
    nClassified = 0
    nTestDocs = 0
    listing = os.listdir(dirPath)
    for eachFile in listing:
        nTestDocs += 1
        docClass = classifyDoc(dirPath+eachFile,
                             probWordForPositive,probPositive,
                             probWordForNegative,probNegative)
        if (docClass == -1 and sentiment == -1):
            nClassified += 1
        elif (docClass == 1 and sentiment == 1):
            nClassified += 1
            
    return nTestDocs,nClassified
            
def printConfigParameters(config):
    print "======================================"
    print " Naive Bayes Configuration Parameters"
    print "======================================"
    for section in config.sections():
        #print section
        for option in config.options(section):
            print " ", option, "=", config.get(section, option)
    print "======================================"
    
def main(): 
    printConfigParameters(config)        
    stopWords = getStopWords() 
    
    vocab = set()    
    positiveWordCounts = {}
    negativeWordCounts = {}
    pathNegativeReviews = config.get('Data', 'NegativeTrainDir')
    pathPositiveReviews = config.get('Data', 'PositiveTrainDir')

    # Build word frequency dictionaries and vocabulary
    #   
    classNegativeDocCount = trainNB(pathNegativeReviews,vocab,negativeWordCounts)                                  
    classPositiveDocCount = trainNB(pathPositiveReviews,vocab,positiveWordCounts)         
    
    # get list of keys in vocab not in positiveWordCounts
    ps = set(positiveWordCounts)
    notInPs = vocab - ps
    
    # add this list as keys with zero counts into positiveWordCounts
    for w in notInPs:
        positiveWordCounts[w] = 0
        
    # do the same for negativeWordCounts
    ns = set(negativeWordCounts)   
    notInNs = vocab - ns
    for w in notInNs:
        negativeWordCounts[w] = 0 

    if config.getboolean('Parameters','ReduceFeature') == True: 
        n = config.getint('Parameters','ReduceFeatureCount')
        positiveWordCounts = reduceW(positiveWordCounts,n)
        negativeWordCounts = reduceW(negativeWordCounts,n)
    print "Feature size:",len(positiveWordCounts)
         
    # Caculate the probabilities for each word given both classes
    # and calculate the standalone probability for each class:
    #
    # for each word, w in docs of class Ci:
    #   P(w|Ci) = count(w,Ci) + 1 / count(Ci) + |vocab|    
    # for each class Ci: 
    #   P(Ci) = |docs of class Ci| / | total docs |
    #
    pDenom = sum(positiveWordCounts.values()) + len(vocab)
    nDenom = sum(negativeWordCounts.values()) + len(vocab) 
    probWordForPositive = {}
    probWordForNegative = {} 
    for w in vocab:
        if (w in positiveWordCounts):
            probWordForPositive[w] = math.log10((positiveWordCounts[w] + 1.0) / pDenom)
        if (w in negativeWordCounts):
            probWordForNegative[w] = math.log10((negativeWordCounts[w] + 1.0) / nDenom)                                 
    
    # Calculate the stand alone probabilities 
    probPositive = math.log10(float(classPositiveDocCount) / (classPositiveDocCount
                        + classNegativeDocCount))   
    probNegative = math.log10(float(classNegativeDocCount) / (classPositiveDocCount
                        + classNegativeDocCount)) 

    # Do classification on test data
    #
    pathNegativeReviews = config.get('Data', 'NegativeTestDir')
    nTestNegativeDocs, classifiedNegative = doClassification(pathNegativeReviews,-1,
                                                 probWordForPositive,probPositive,
                                                 probWordForNegative,probNegative)
                     
    pathPositiveReviews = config.get('Data', 'PositiveTestDir')
    nTestPositiveDocs, classifiedPositive = doClassification(pathPositiveReviews,1,
                                                 probWordForPositive,probPositive,
                                                 probWordForNegative,probNegative)
    
    # Print the results
    #
    print("Correctly predicted "+str(classifiedNegative)+" docs out of "
        +str(nTestNegativeDocs)+" negative docs")      
    print("Correctly predicted "+str(classifiedPositive)+" docs out of "
        +str(nTestPositiveDocs)+" positive docs")
    print("Accuracy: "+str(100.0*(classifiedPositive+classifiedNegative)/
                        (nTestPositiveDocs+nTestNegativeDocs)))+"%"                  
                        
main()