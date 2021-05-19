from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import alpha_vantage
from alpha_vantage import techindicators
from alpha_vantage import sectorperformance
import requests
import json
from datetime import date
import sqlite3

keyread = open("C:\Key Dump\Alphavantagekey.txt", "r")
api_key = keyread.read()

ts = TimeSeries(api_key)
fd = FundamentalData(api_key)

z = True
while z is True:
    orders = input("Enter request: ")
    def CompanyOverview():
        global symbols
        symbols = input("Enter search term: ")
        if symbols == "Cancel":
            return()
        try:
            print(" ")
            print(fd.get_company_overview(symbols))
            print(" ")
        except:
            wp = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={symbols}&apikey={api_key}"
            response = requests.get(wp)
            stockjson = response.json()
            x = 0
            length = len(stockjson['bestMatches'])
            if length == 0:
                print("Failed to find stock")
                return()
            a = True
            while a is True:
                print((stockjson['bestMatches'][x]['1. symbol']), "    ", (stockjson['bestMatches'][x]['2. name']), "    ", (stockjson['bestMatches'][x]['4. region']))
                x=x+1
                if  x == length:
                    a = False
                    print(" ")
                    CompanyOverview()

    def StockWatch():
        StockSTR = open("C:\Key Dump\StockstoWatch.txt", "r")
        Stocktolist = StockSTR.read()
        SplitStocks = Stocktolist.split(" ")
        global stocklen
        stocklen = len(SplitStocks)
        sc = True
        ss = 0
        while sc is True:
            check = ts.get_daily(symbol = SplitStocks[ss])
            print(check)
            ss = ss + 1
            if ss == stocklen:
                sc = False

    def HistoricDaily():
        global symbols
        symbols = input("Enter search term: ")
        if symbols == "Cancel":
            return()
        try:
            print(" ")
            data, meta_data = ts.get_daily_adjusted(symbol = symbols, outputsize="full")
            print(data)
            data_keys = list(data.keys())
            data_keys_len = len(data_keys)
            date_variable = 0
            for _ in range(data_keys_len):
                con = sqlite3.connect('Stocks.db')
                cur = con.cursor()

                data_two = data_keys[date_variable]
                data_to_edit = data[data_two]
                print(data_to_edit)
                open = data[data_two]['1. open']
                high = data[data_two]['2. high']
                low = data[data_two]['3. low']
                close = data[data_two]['4. close']
                adjusted_close = data[data_two]['5. adjusted close']
                volume = data[data_two]['6. volume']
                dividend_amount = data[data_two]['7. dividend amount']
                split_coefficient = data[data_two]['8. split coefficient']
                data_to_save = f"'{data_two}', '{open}', '{high}', '{low}', '{close}', '{adjusted_close}', '{volume}', '{dividend_amount}', '{split_coefficient}'"
                try:
                   cur.execute(f"INSERT INTO {symbols} VALUES ({data_to_save})")
                except:
                   cur.execute(f"CREATE TABLE {symbols} (Date, Open, High, Low, Close, Adjusted Close, Volume, Dividend Amount, Split Coefficient)")
                   cur.execute(f"INSERT INTO {symbols} VALUES ({data_to_save})")
                con.commit()
                con.close()
                date_variable = date_variable + 1

        except:
            wp = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={symbols}&apikey={api_key}"
            response = requests.get(wp)
            stockjson = response.json()
            x = 0
            length = len(stockjson['bestMatches'])
            if length == 0:
                print("Failed to find stock")
                return()
            a = True
            while a is True:
                print((stockjson['bestMatches'][x]['1. symbol']), "    ", (stockjson['bestMatches'][x]['2. name']), "    ", (stockjson['bestMatches'][x]['4. region']))
                x=x+1
                if  x == length:
                    a = False
                    print(" ")

    if orders == "CompanyOverview" or orders == "CO":
        CompanyOverview()
    if orders == "StockWatch" or orders == "SW":
        StockWatch()
    if orders == "HistoricDaily" or orders == "HD":
        HistoricDaily()