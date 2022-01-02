from yahoo_fin.stock_info import *
from datetime import *
import numpy as np
import pandas as pd
import math

pd.set_option('display.max_rows', None)

#Importer les tickers d'une spread sheet excel
df = pd.read_excel('investissementLongTerme.xlsx')
tickersList = df['ticker'].values.tolist()


#Variables pour les critères à respecter 
YIELD_TO_REACH = 2.5
DIV_GROWTH_TO_REACH = 5
DIV_CUT_MAX = 2

#Liste des tickers ayant respectés les critères de sélection
tickersGoodCompany = []

#Compteur pour itérer la liste de tickers
ticker = 0


#########################################################################
# Role : Accède à la Summary table du ticker
#
# Entré : ticker de la compagnie (string)
# Sortie : dictionnaire comportant les informations générales de l'action (dict)
# ________________________________________________
# La Summary table comprend les données suivantes :
#  Quote Price
#  Previous Close           Market Cap
#  Open                     Beta
#  Bid                      PE Ratio (TTM)
#  Ask                      EPS (TTM)
#  Days Range               Earnings Date
#  52 Week Range            Dividend & Yield
#  Volume                   Ex-Dividend Date
#  Avg. Volume              1y Target Est
#########################################################################
def dict_Quote_Table(ticker):   
    try:
        dictQuoteTable = get_quote_table(ticker)
    except Exception:
        return False 
    else:
        return dictQuoteTable


#########################################################################
# Role : Accède au EPS de la compagnie dans le dictionnaire d'informations générales
#
# Entré : dictionnaire d'informations générales (dict)
# Sortie : EPS de la compagnie (float)
#########################################################################
def eps_actual(stock_general_infos):
    
    if(math.isnan(stock_general_infos['EPS (TTM)'])):
        print("pas de eps")
        return False
    else:
        return stock_general_infos['EPS (TTM)']

    
#########################################################################
# Role : Accède à l'historique des dividendes versés par la compagnie
#        et les retourne un DataFrame Pandas qui comporte 
#        les dates et les montants versés en dividendes
#
# Entré : ticker de la compagnie (string)
# Sortie : l'historique de dividendes (DataFrame Pandas)
#########################################################################
def dividends_infos(ticker):
    
    try:
        dividendes = get_dividends(ticker, "01-01-2000", index_as_date = False)           
    except Exception:
        print("pas de div")
        return False        
    else:
        return dividendes


#########################################################################
# Role : Calcule la croissance du dividendes de la compagnie depuis les 10 dernières années
#
# Entré : l'historique de dividendes (DataFrame Pandas)
# Sortie : moyenne de croissance du dividendes en % (float)
#########################################################################
def dividends_10_years_growth(div_history):
    dateDiv = 0
    while(dateDiv < div_history.shape[0]):
        if(pd.to_datetime(date.today()) - timedelta(days = 3650) < div_history.loc[dateDiv, 'date']):            
            
            deltaDiv = (div_history.loc[(div_history.shape[0]-1), 'date'] - div_history.loc[dateDiv, 'date']).days/365
 
            return div_history.dividend.tail(div_history.shape[0] - (dateDiv+1)).pct_change().sum() * 100 / deltaDiv
        dateDiv += 1


#########################################################################
# Role : Vérifie si la compagnie a coupé son dividende dans le passé
#        si oui on inscrit la date de coupure du dividende, ainsi que sa période dans une liste
#
# Entré : l'historique de dividendes (DataFrame Pandas)
# Sortie : liste comprenant le nombre de fois que la compagnie à coupé son dividende
#          ainsi que les dates et les périodes des coupures
#########################################################################
def dividends_cut(div_history):
    
    div = 0
    divCut = 0
    dateDivCut = [divCut]
    nbDivVerse = len(div_history)-1
        
    while(div < nbDivVerse):            
        
        if(div_history.loc[div, 'date'] + timedelta(days = 120) < div_history.loc[div+1, 'date']):                
            dateDivCut.append(div_history.loc[div, 'date'])    
            dateDivCut.append(div_history.loc[div+1, 'date'] - div_history.loc[div, 'date'])
            
            dateDivCut[0] += 1

        if(div == nbDivVerse-1):
            if(pd.to_datetime(date.today()) - div_history.loc[div+1, 'date'] >  timedelta(days = 120)):
                dateDivCut.append(div_history.loc[div+1, 'date'])
                dateDivCut.append(pd.to_datetime(date.today()) - div_history.loc[div+1, 'date'])
                
                dateDivCut[0] += 1
        div += 1
    return dateDivCut


#########################################################################
# Role : Calcule du dividende annuel de la compagnie
#
# Entré : l'historique de dividendes (DataFrame Pandas)
# Sortie : dividende annuel (float)
#########################################################################
def dividend_actual(dividends_history):
    return float(dividends_history.dividend.tail(1))*4


#########################################################################
# Role : Calcule du yield de la compagnie
#
# Entré : dictionnaire d'informations générales (dict), l'historique de dividendes (DataFrame Pandas)
# Sortie : yield (float)
#########################################################################
def yield_info(stock_general_infos, div_history):
    
    if(stock_general_infos['Forward Dividend & Yield'] == "N/A (N/A)"):
        return False
    else:
        return div_history.loc[div_history.shape[0]-1, 'dividend'] * 4 / stock_general_infos['Quote Price'] * 100



#####################################################################################################
while(ticker < len(tickersList)):
    
    print(ticker)
    stock_general_infos = dict_Quote_Table(tickersList[ticker])
    
    if(stock_general_infos != False):           
        eps = eps_actual(stock_general_infos)
        div_history = dividends_infos(tickersList[ticker])

        if(type(eps) != bool and type(div_history) != bool):
            
            if(eps > 0):            
                
                if(eps > dividend_actual(div_history)):
                    
                    divCut = dividends_cut(div_history)

                    if(divCut[0] <= DIV_CUT_MAX):
                        
                        Yield = yield_info(stock_general_infos, div_history)
                
                        if(Yield > YIELD_TO_REACH):                
                            div_growth = dividends_10_years_growth(div_history)
                    
                        
                            if(float(div_growth) > DIV_GROWTH_TO_REACH):
                                tickersGoodCompany += tickersList[ticker]
                                print("___________________\nTicker : " + tickersList[ticker])
                                print("yield : " + str(Yield) + " %")
                                print("Croissance Div : " + str(div_growth) + " %\n")
                                
                                y=1
                                while(y < len(divCut)):
                                    print(divCut[y])                                                                      
                                    y += 1
                                print("\n")
                            else:
                                print("-Dividendes")
                        else:
                            print("-yeild")
                    else:
                        print("Div cut")
                else:
                    print("EPS < DIV")
            else:
                print("-EPS")
    else:
        print("PAS d'infos")
    ticker += 1