import streamlit as st
import plotly.figure_factory as ff
import pandas as pd
import plotly.graph_objects as go
from finta import TA
import datetime
import numpy as np
import joblib
import sklearn
from sklearn import preprocessing 

encoder =  preprocessing.LabelEncoder()
encoder.classes_ = np.load('classes.npy',allow_pickle=True)
model = joblib.load('model_pattern')
# Add histogram data

df = pd.read_csv('final_data.csv')
df = df[['date','open','high','low','close','volume']]

config = dict({'scrollZoom': True})  
# Group data together

df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M')
df['date_day'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M')
#year = st.selectbox('select year',(2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018,2019, 2020, 2021, 2022))
#month = st.selectbox('select month',(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12))
#date1 = st.selectbox('select date',([z for z in range(1,32)]))

date = st.date_input(
    "Enter Date",datetime.date(2022, 10, 24))
    

period = st.number_input('Insert  period for DEMA',14)


af = st.number_input('Insert  AF for SAR',0.02)
amax = st.number_input('Insert  AMAX for SAR',0.02)

chart_type = st.selectbox('chart_type',('normal','remove_candles','pred_pattern'))


def rem_candle(df):
  red_index = df.loc[(  df['open'] > df['DEMA']  )  & (df['close']  < df['DEMA'] )].index
  green_index = df.loc[(  df['open'] < df['DEMA']  )  & (df['close']  > df['DEMA'] )].index
  df.at[red_index,'red'] = 1
  df.at[green_index,'green'] = 1
  sig_index = df.loc[(  df['red'] == 1  )  | (df['green']  == 1 )].index
  df.at[sig_index,'sig'] = 1


  df['open'] = np.where(df['sig']!=1,np.NaN,df['open'])
  df['close'] = np.where(df['sig']!=1,np.NaN,df['close'])
  df['high'] = np.where(df['sig']!=1,np.NaN,df['high'])
  df['low'] = np.where(df['sig']!=1,np.NaN,df['low'])
  return df

def get_da(dchec):
    def get_va(ind):
        if ind>10:
            fet =  ["DEMA_1","DEMA_2",
          "DEMA_3",
          "DEMA_4",
          "DEMA_5",
          "DEMA_6",
          "DEMA_7",
          "DEMA_8","open_c","high_c","low_c","close_c","SAR_val"]
            df_check = pd.DataFrame(columns = fet)
            df_check.loc[len(dchec)]  = list(dchec['DEMA'].iloc[ind-7:ind+1]) + [dchec['open'].iloc[ind] , dchec['high'].iloc[ind]  , dchec['low'].iloc[ind] , dchec['close'].iloc[ind], dchec['SAR'].iloc[ind]]
            pctc = df_check.pct_change(axis=1)
            #print(pctc)
            preds =  model.predict(pctc)
            pre = encoder.inverse_transform(preds)

            if pre[0] == 'buy_signal':


                if dchec['SAR'].iloc[ind] < dchec['low'].iloc[ind]:
                    return pre[0]

            if pre[0] == 'sell_signal':

                if dchec['SAR'].iloc[ind] > dchec['high'].iloc[ind]:
                    return pre[0]            


            return np.NaN
        else:
            return np.NaN

    dx= pd.DataFrame([z for z in range(len(dchec))])
    dx['da'] = dx 
    dchec['prediction'] = dx['da'].apply(get_va)
    
    
    test_list = list(dchec.loc[(dchec['prediction'] == 'buy_signal')  ].index)
    res = [test_list[i + 1] - test_list[i] for i in range(len(test_list)-1)]
    sublistt = [[z for z in range(i-7,i+1)] for i in test_list]
    flat_list = [item for sublist in sublistt for item in sublist]    
    sor_index = sorted(list(set(flat_list))) 



    dchec['dema_line_buy'] = dchec.loc[sor_index]['DEMA']


    test_list = list(dchec.loc[ (dchec['prediction'] == 'sell_signal') ].index)
    res = [test_list[i + 1] - test_list[i] for i in range(len(test_list)-1)]
    sublistt = [[z for z in range(i-7,i+1)] for i in test_list]
    flat_list = [item for sublist in sublistt for item in sublist]    
    sor_index = sorted(list(set(flat_list))) 

    dchec['dema_line_sell'] = dchec.loc[sor_index]['DEMA']
    
    
    
    df_year['dema_line_buy'] = df_year['dema_line_buy'] +15
    df_year['dema_line_sell'] = df_year['dema_line_sell'] +25
    df_year['DEMA'] = df_year['DEMA'] +20

    
    
    return df_year
    
    

    
    
    
    






if date: 
    print(period,af,amax) 
    #df_year = df.loc[(df['year'] == year) & (df['month'] == month ) & (df['date_1'] == date1 )]
    df_year  = df.loc[df['date_day'].dt.date == date]
    if len(df_year) >0:
        df_year = df_year.reset_index()       
          
        df_year['SAR'] = TA.SAR(df_year,af = af,amax = amax)  

        df_year['DEMA'] = TA.DEMA(df_year,period = period) 

        
        
        df_year = get_da(df_year)
        
        if chart_type == 'remove_candles':
            df_year = rem_candle(df_year)
            
            
    
        price = go.Candlestick(x=df_year['date'],
                        open=df_year['open'],
                        high=df_year['high'],
                        low=df_year['low'],
                        close=df_year['close'],name = 'price')

        DEMA =  go.Scatter(x=df_year['date'],y=df_year['DEMA'],name = 'DEMA',marker_line_color="MediumPurple", marker_color="lightskyblue")
        SAR =  go.Scatter(x=df_year['date'],y=df_year['SAR'],name = 'SAR',mode='markers',
                           marker_line_color="midnightblue", marker_color="lightskyblue",
                           marker_line_width=0.5, marker_size=2)                            
 



        BDEMA =  go.Scatter(x=df_year['date'] - 5,y=df_year['dema_line_buy'],name = 'dema_line_buy',marker_line_color="lightskyblue", marker_color="MediumPurple")
        SDEMA =  go.Scatter(x=df_year['date'] + 5,y=df_year['dema_line_sell'],name = 'dema_line_sell',marker_line_color="DarkSlateGrey", marker_color="DarkSlateGrey")
 
                        
        fig = go.Figure(data=[DEMA,BDEMA,SDEMA,SAR])
                        
                        
                        

        fig.update_layout(xaxis_rangeslider_visible=False)
        #fig.update_xaxes(rangebreaks=[dict(values=df_year['date'])]) # hide dates with no values


        # Plot!

        st.plotly_chart(fig,config=config, use_container_width=True)
    else:
        st.write('Data is not available for this date')
