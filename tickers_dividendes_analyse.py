from yahoo_fin.stock_info import *
from datetime import *
import numpy as np
import pandas as pd


#yield > 2.5
#croissance div

tickersList = tickers_sp500()

ticker = 0

while(ticker < len(tickersList)):
    divCut = 0
    
    try:
        dividendes = get_dividends(tickersList[ticker], "01-01-2000", index_as_date = False)        
    
    except Exception:
        ticker +=1
    
    else:
        dateDivCut = []
        periodeDivCut = []
        nbDivVerse = len(dividendes)-1
        d = 0
        
        while(d < nbDivVerse):            
            if(dividendes.loc[d, 'date'] + timedelta(days = 120) < dividendes.loc[d+1, 'date']):                
                
                periodeDivCut.append(dividendes.loc[d+1, 'date'] - dividendes.loc[d, 'date'])
                dateDivCut.append(dividendes.loc[d, 'date'])
                divCut += 1;

            if(d == nbDivVerse-1):
                if(pd.to_datetime(date.today()) - dividendes.loc[d+1, 'date'] >  timedelta(days = 120)):
                    periodeDivCut.append(pd.to_datetime(date.today()) - dividendes.loc[d+1, 'date'])
                    dateDivCut.append(dividendes.loc[d+1, 'date'])
                    divCut += 1;
            d += 1    

        if(divCut < 3):
            y=0
            Yield = dividendes.loc[nbDivVerse, 'dividend'] * 4 / get_live_price(tickersList[ticker]) * 100
            if(Yield > 2.5):                
                
                if(dividendes.shape[0] < 41):
                    croissanceDiv = dividendes.dividend.tail(41).pct_change().sum() * 100 / dividendes.shape[0]
                    
                else:
                    croissanceDiv = dividendes.dividend.tail(41).pct_change().sum() * 2.5

                print("___________________\nTicker : " + tickersList[ticker])
                print("yield : " + str(Yield) + " %")
                print("Croissance Div : " + str(croissanceDiv) + " %\n")
                while(y < len(dateDivCut)):
                    print(dateDivCut[y])
                    print(periodeDivCut[y])
                    print("")
                    y += 1
        ticker += 1

