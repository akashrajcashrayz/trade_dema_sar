import streamlit as st
import plotly.figure_factory as ff
import pandas as pd
import plotly.graph_objects as go
from finta import TA
import datetime
# Add histogram data

df = pd.read_csv('final_data - Copy.csv')
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



if date: 
    print(period,af,amax) 
    #df_year = df.loc[(df['year'] == year) & (df['month'] == month ) & (df['date_1'] == date1 )]
    df_year  = df.loc[df['date_day'].dt.date == date]
    if len(df_year) >0:
        df_year = df_year.reset_index()       
        
        print(df_year)            
        df_year['SAR'] = TA.SAR(df_year,af = af,amax = amax)  
        print(df_year)
        df_year['DEMA'] = TA.DEMA(df_year,period = period)       
        print(df_year)        
        price = go.Candlestick(x=df_year['date'],
                        open=df_year['open'],
                        high=df_year['high'],
                        low=df_year['low'],
                        close=df_year['close'],name = 'price')

        DEMA =  go.Scatter(x=df_year['date'],y=df_year['DEMA'],name = 'DEMA')
        SAR =  go.Scatter(x=df_year['date'],y=df_year['SAR'],name = 'SAR',mode='markers',
                           marker_line_color="midnightblue", marker_color="lightskyblue",
                           marker_line_width=2, marker_size=5)                            
                        
                        
        fig = go.Figure(data=[price,DEMA,SAR])
                        
                        
                        

        fig.update_layout(xaxis_rangeslider_visible=False)
        #fig.update_xaxes(rangebreaks=[dict(values=df_year['date'])]) # hide dates with no values


        # Plot!

        st.plotly_chart(fig,config=config, use_container_width=True)
    else:
        st.write('Data is not available for this date')
