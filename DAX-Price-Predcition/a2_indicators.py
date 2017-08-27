#################################################################
#
# Author: Kevin O'Mahony
# Date: 6/5/2017
#
#################################################################
import pandas as pd
import talib as tl

# Creates price, volume, technical indicators and time related
# features for input to the prediction models. 
# Change filename to create a data set for a different instrument
# as required.
#
filename = 'DAX30.csv'
price_data=pd.read_csv(filename, sep=',',header=0)

np_price_data = price_data.ix[:,1:].values
open = np_price_data[:,0]
high = np_price_data[:,1]
low = np_price_data[:,2]
close = np_price_data[:,3]

# create time related features
#
price_data['date'] = pd.to_datetime(price_data['date'])
price_data['DayOfMonth'] =  price_data['date'].dt.day
price_data['DayOfWeek'] =  price_data['date'].dt.weekday
price_data['WeekOfYear'] = price_data['date'].dt.strftime("%U")

# create indicator type features
#
price_data['dirn'] = (close > open) * 1     # convert to 1/0 value
price_data['trend'] = (close > price_data['close'].shift(1)) * 1

price_data['ma0_trend'] = (price_data['close'] > tl.EMA(close,10)) * 1
price_data['ma1_trend'] = (price_data['close'] > tl.EMA(close,20)) * 1
price_data['ma2_trend'] = (price_data['close'] > tl.EMA(close,50)) * 1
price_data['ma3_trend'] = (price_data['close'] > tl.EMA(close,100)) * 1

price_data['close_at_high'] = (close == high) * 1
price_data['close_at_low'] = (close == low) * 1

# write out the combined price data, time info and technical indicators
#
price_data.to_csv("price_data.csv", index=False, encoding='utf-8')