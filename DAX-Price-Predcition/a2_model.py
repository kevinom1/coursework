#################################################################
#
# Author: Kevin O'Mahony
# Date: 6/5/2017
#
#################################################################

import numpy as np
import pandas as pd
import datetime as dt

from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

# define model names
#
ADABOOST      = 0
SVC           = 1
RANDOMFOREST  = 2
GRADIENTBOOST = 3

modelNames = ['AdaBoost','SVC','RandomForest','GradientBoost']

# Input features for our models
#
Features = ['DayOfMonth', 'DayOfWeek', 'WeekOfYear',
            'open', 'high', 'low', 'close', 'volume',
            'dirn', 'ma0_trend', 'ma1_trend', 'ma2_trend', 'ma3_trend',
            'close_at_high', 'close_at_low' ]

#################################################################
#
#  Retrieves data subset based on start/end dates
#  from a pandas dataframe populated from our dataset.
#
def historicalData(data,startDate,endDate):
    theDate = (data['date'] >= startDate) & (data['date'] <= endDate)
    a = data[theDate]
    return(a)

#################################################################
#
#  Returns the date, nDays after startDate taking weekend
#  (non trading days) into account. Note holidays are not handled.
#
def getNextDate(startDate,nDays):
    done = False
    nextDate = startDate
    while (done != True):
        nextDate = startDate + dt.timedelta(nDays)
        if nextDate.weekday() == 5:
            nDays += 2
        elif nextDate.weekday() == 6:
            nDays += 1
        else:
            done = True
    return nextDate

#################################################################
#
# Reads the data set csv file and performs data manipulations
# required before starting training/testing.
#
def initialise_price_data(data_file):

    price_data = pd.read_csv(data_file, sep=',',header=0)
    price_data['date'] = pd.to_datetime(price_data['date'],format='%Y.%m.%d')

    # lag the predicted outcome by 1 day for training and test
    price_data['trend-shift-1'] = price_data['trend'].shift(-1)

    # remove newly created NAN value after shift
    price_data.replace(' ', np.nan,inplace=True)
    price_data.dropna(how='all')
    return price_data

#################################################################
#
# Fits the required model with the specified training and actual data
#
def fitModel(modelName,trainX, trainY):

    if modelName == ADABOOST:
        model = AdaBoostClassifier(n_estimators=50, learning_rate=1)
    elif modelName == SVC:
        model = SVC(kernel='rbf',degree=3)
    elif modelName == RANDOMFOREST:
        model = RandomForestClassifier()
    else:
        model = GradientBoostingClassifier()

    model.fit(trainX, trainY)
    return model

#################################################################
#
# Calculates the number of correct predictions given lists of
# prediction results and actuals.
#
def getCorrectPredictionCount(pplist, yylist):

    true_up = 0.0
    true_dn = 0.0
    false_up = 0.0
    false_dn = 0.0
    nCorrect = 0.0
    for i in range(0, len(pplist)):
        if pplist[i] == 1 and yylist[i] == 1:
            true_up += 1
            nCorrect += 1
        elif pplist[i] == 0 and yylist[i] == 0:
            true_dn += 1
            nCorrect += 1
        elif pplist[i] == 1 and yylist[i] == 0:
            false_up += 1
        elif pplist[i] == 0 and yylist[i] == 1:
            false_dn += 1
    return nCorrect

#################################################################
#
# Calculates and prints average features importance from a list
# of one or more feature importance value lists.
#
def avgFeatureImportance(feature_importance):
    n = len(feature_importance[0])
    totalsList = [0.0] * n
    for i in range(0, len(feature_importance)):
        for e in range(0, n):
            totalsList[e] += feature_importance[i][e]
    for e in range(0, n):
        print e + 1, totalsList[e] / len(feature_importance)

#################################################################

def main():

    nTrainingRuns = 20      # number of training runs for each month
    nTrainingDays = 3       # number of training days
    yylist = []             # used to track actual test class
    pplist = []             # used to track predicted class
    totalCorrectCount = []  # tracks total correct predictions
    feature_importance = []
    theModel = ADABOOST     # to run a different model change this to
                            # one of  models defined at top of this file

    print "Using model:",modelNames[theModel]
    price_data = initialise_price_data('price_data.csv')

    # for specified years, months and training period runs....
    #
    for year in range(2016,2017):
        for month in range(1,12):
             for theDay in (range(1,nTrainingRuns)):

                # do a train/predict cycle
                # first get data for the required training period
                startDate = dt.date(year, month, 1) + dt.timedelta(days=theDay)
                endDate = getNextDate(startDate,nTrainingDays)
                data =  historicalData(price_data,startDate,endDate)

                # create the training and class data
                trainX = np.array(data[Features].values)
                trainY = np.array(data['trend-shift-1'].values)

                if len(np.unique(trainY)) <= 1:
                    continue

                # scale the training data
                scaler = preprocessing.MinMaxScaler().fit(trainX)
                trainX = scaler.transform(trainX)
                np.random.seed(123)

                # create the model and fit our training data
                model = fitModel(theModel,trainX,trainY)

                # keep a history of feature importance if RandomForest
                if theModel == RANDOMFOREST:
                    feature_importance.append(model.feature_importances_)

                # get data for the required test period
                testStartDate = getNextDate(endDate,1)
                testEndDate = testStartDate + dt.timedelta(days=0)
                testData = historicalData(price_data,testStartDate,testEndDate)

                if (len(testData) > 0):

                    # scale the input testing data
                    testX = np.array(testData[Features].values)
                    testX = scaler.transform(testX)

                    # create the test class data
                    testY = np.array(data['trend-shift-1'].values)

                    p = model.predict(testX)

                    # save the actual class and predicted class
                    yylist.append(testY[0])
                    pplist.append(p[0])

        # calculate and display prediction accuracy for one year
        nCorrect = getCorrectPredictionCount(pplist,yylist)
        avg = (nCorrect/len(pplist))*100
        print year,":",int(nCorrect),"correct out of",len(pplist),'predictions =>', \
            '{0:.2f}% correct'.format(avg)

        totalCorrectCount.append(avg)
        del yylist[:]
        del pplist[:]

    # calculate and display average prediction accuracy
    print 'Average correct:','{0:.2f}%'.format(sum(totalCorrectCount)/len(totalCorrectCount))

    # calculate and display average feature importance
    if theModel == RANDOMFOREST:
        avgFeatureImportance(feature_importance)

#################################################################

main()