import pandas as pd
import numpy as np
import datetime as dt
import math

from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor


#################################################################
#
# Features used in training / prediction
#
Features =  ['Slot', 'EA', 'EA2', 'WD1', 'EP2-SHIFT-7D'
             # 'LOAD-SHIFT-1D',           # Decided to remove these after
             # 'LOAD-SHIFT-7D',           # completed document - not adding to accuracy.
             ]

#################################################################
#
# define model names
#
SUPPORT_VECTOR_REG = 1
MLP_REGRESSOR      = 2
RANDOM_FOREST      = 3
GRADIENT_BOOSTED   = 4
EXTRA_TREE_REG     = 5

#################################################################
#
# Retrieve historical price data
#
def historicalData(data,startDate,endDate):
    theDate = (data['TheDate'] >= startDate) & (data['TheDate'] <= endDate)
    a = data[theDate]
    return(a)

#################################################################
#
# Metrics related functions
#
def mape(actual, pred):
    tmp = 0.0
    avgActual = sum(actual)/len(actual)
    for i in range(0,len(pred)):
        if actual[i] != 0:
            # note: we use average actual for denominator to handle
            # near zero price values in data set
            tmp += math.fabs((actual[i]-pred[i])/avgActual)
    return (tmp/len(pred)) * 100

def rmse(actual, pred):
    return(metrics.mean_squared_error(actual, pred)**0.5)

#################################################################
#
# Read in data set and create some additional features
#
def initialise_price_data():
    data=pd.read_csv('price-2014-to-2016.csv', sep=',',header=0, low_memory=False)

    # convert date/time related to correct type
    data['TheTimeStamp'] = pd.to_datetime(data['TheTimeStamp'])
    data['TheDate'] = pd.to_datetime(data['TheDate'])

    # create time shifted features
    data['LOAD-SHIFT-1D'] = data['LOAD'].shift(48)
    data['LOAD-SHIFT-7D'] = data['LOAD'].shift(48*7)
    data['diff_log10_EP2-SHIFT-7D'] = data['diff_log10_EP2'].shift(48*7)
    data['EP2-SHIFT-7D'] = data['EP2'].shift(48 * 7)

    # shift all 48 of tomorrows price to today as response variable
    data['EP2-SHIFT-1D'] = data['EP2'].shift(-48)

    data.replace(r'\s+( +\.)|#', np.nan, regex=True).replace('', np.nan)
    data.dropna(inplace=True) # delete rows with any cell Nan

    return data

#################################################################
#
# Creates the required model
#
def createModel(modelName):

    if modelName == SUPPORT_VECTOR_REG:
        model = SVR(kernel='rbf',cache_size=900)
    elif modelName == MLP_REGRESSOR:
        model = MLPRegressor(activation='logistic',solver='sgd',
                    hidden_layer_sizes=(13),momentum=0.3,
                    learning_rate='adaptive')
    elif modelName == RANDOM_FOREST:
        model = RandomForestRegressor()
    elif modelName == GRADIENT_BOOSTED:
        model = GradientBoostingRegressor()
    else:
        # default to EXTRA_TREE_REG
        model = ExtraTreesRegressor()

    return model

#################################################################
#
# Main routine
#
def main():

    rSum = []
    mSum = []

    forecast = {}
    doLogTransform = False
    doLnTransform = False

    importances = [[] for i in range(len(Features))]

    # change this for different model, as defined line 28
    modelName = GRADIENT_BOOSTED

    testStartDate = dt.date(2016,1,1)   # first day to predict
    trainingDays = 360                  # the training period in days
    startDay = 1
    nDays = 360                         # number of prediction days

    data = initialise_price_data()
    model = createModel(modelName)

    print dt.datetime.now().time(),",",trainingDays
    trainStartDate = testStartDate - dt.timedelta(days=trainingDays + 2)

    for theDay in (range(startDay,startDay+nDays)):

        startDate = trainStartDate + dt.timedelta(days=theDay)
        endDate = startDate +  dt.timedelta(days=trainingDays)

        print dt.datetime.now().time(),"Training data from: ",startDate," to ",endDate
        df = historicalData(data, startDate, endDate)

        trainX = np.array(df[Features].values)

        if len(trainX) > 0:

            # do transforms if specified
            if doLogTransform == True:
                trainY = df["EP2-SHIFT-1D"].apply(math.log10).values
            elif doLnTransform == True:
                trainY = df["EP2-SHIFT-1D"].apply(math.log).values
            else:
                trainY = df["EP2-SHIFT-1D"].values

            scaler = StandardScaler().fit(trainX)
            trainX = scaler.transform(trainX)

            np.random.seed(666)

            model.fit(trainX, trainY)

            if modelName == RANDOM_FOREST:
                for index in range(len(trainX[0])):
                    importances[index].append(model.feature_importances_[index])

            # now that we've trained the model we predict value for
            # the next day after the last training day
            testStartDate = endDate + dt.timedelta(days=1)
            testEndDate = testStartDate + dt.timedelta(days=0)
            df = historicalData(data, testStartDate, testEndDate)
            if len(df) > 0:
                testX = np.array(df[Features].values)
                testX = scaler.transform(testX)

                # do transforms if specified
                if doLogTransform == True:
                    testY = df["EP2-SHIFT-1D"].apply(math.log10).values
                elif doLnTransform == True:
                    testY = df["EP2-SHIFT-1D"].apply(math.log).values
                else:
                    testY = df["EP2-SHIFT-1D"].values

                p = model.predict(testX)

                slots = df['Slot'].tolist()
                testValues = testY.tolist()
                predictedValues = p.tolist()

                # save the predicted values
                for s in range(0,len(slots)):
                    forecast[slots[s]] = {testValues[s]:predictedValues[s]}

        # undo any transforms
        tY = []
        p = []
        sortedKeys = sorted(forecast.keys())
        for k in sortedKeys:
            v = forecast[k]
            if doLogTransform == True:
                tY.append(math.pow(10,v.keys()[0]))
                p.append(math.pow(10,v.values()[0]))
            elif doLnTransform == True:
                tY.append(math.exp(v.keys()[0]))
                p.append(math.exp(v.values()[0]))
            else:
                tY.append((v.keys()[0]))
                p.append((v.values()[0]))

        # if we have predicted values print accuracy metrics
        if len(tY) > 0:
            r = rmse(tY,p)
            m = mape(tY,p)

            print "Test data on: ", testStartDate,",", \
                "RMSE:", float("{0:.2f}".format(r)), \
                " MAPE:", float("{0:.2f}".format(m)),'\n'

            # save metrics to for average calculation
            rSum.append(r)
            mSum.append(m)

    # print average metrics for complete train/predict run
    if (len(rSum)):
        print dt.datetime.now().time(),',', \
            trainingDays,',',\
            'Overall RMSE: ',float("{0:.2f}".format(sum(rSum)/len(rSum))),',', \
            'Overall MAPE: ',float("{0:.2f}".format(sum(mSum)/len(mSum)))

    if modelName == RANDOM_FOREST:
        for index in range(len(trainX[0])):
            print "Average importance of feature ", index, "is", \
                sum(importances[index])/len(importances[index])

main()