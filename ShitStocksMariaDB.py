from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import threading
from datetime import datetime
from time import sleep
from peewee import *
import logging


#Reading and defining variables for alpha-vantage api key - remember free key has limited calls per minute
keyread = open("Alphavantagekey.txt", "r")
api_key = keyread.read()


ts = TimeSeries(api_key)
fd = FundamentalData(api_key)

#Define database
database = MySQLDatabase("ShitStocks", user="root", password="admin", host="172.17.0.2", port=3306)

class BaseModel(Model):
    class Meta:
        database = database

#Define startup - checks list of companies and generates a list and number of companies for use later
def StartUp():
    try:
        Companies_In_DB = open("CompaniesInDB.txt", "r").read()
        Companies_List = Companies_In_DB.split()
        How_many_in_DB = len(Companies_List)

    except FileNotFoundError:
        print("File not found, generating new")
        Companies_In_DB = open("CompaniesInDB.txt", "w")
        Companies_list = database.get_tables()
        x = 0
        str_to_write = ""
        for companies in Companies_list:
            print(Companies_list[x][0])
            str_to_write = str_to_write + " " + Companies_list[x][0]
            x = x + 1
        Companies_In_DB.write(str_to_write)

    except:
        "General Error - Companies in DB lookup"

    return(How_many_in_DB, Companies_List)


#Defines Thread initialisation - takes the number of companies and their symbols to generate the needed threads
def Thread_initialisation(Companies_List):
    logging.info("Starting Thread ")
    count = 0
    thread_dict = []
    for companies in Companies_List:
        thread_dict.append(companies + "_thread")
        thread_dict[count] = threading.Thread(target= scraping, args=(companies, companies))
        thread_dict[count].start()
        count = count + 1


#Defines scraping - api call to alpha-vantage:
#   - takes thread name and symbol,
#   - using a loop breaks down into the data entries needed,
#   - using a peewee query checks if data entry exists using date and symbol - will not check other integers
#   - if entry doesn't exists commits to MariaDB via PeeWee
def scraping(thread_name, symbols):
    logging.info(f"Starting thread - {symbols} - " + datetime.utcnow().strftime("%H:%M:%S - %D"))
    print("Pulling " + thread_name + " data")

    data_line, meta_data = ts.get_daily_adjusted(symbol=symbols, outputsize="full")
    data_line_keys = list(data_line.keys())
    data_line_keys_len = len(data_line_keys)
    date_variable = 0

    for _ in range(data_line_keys_len):
        date_of_entry = data_line_keys[date_variable]
        open = data_line[date_of_entry]['1. open']
        high = data_line[date_of_entry]['2. high']
        low = data_line[date_of_entry]['3. low']
        close = data_line[date_of_entry]['4. close']
        adjusted_close = data_line[date_of_entry]['5. adjusted close']
        volume = data_line[date_of_entry]['6. volume']
        dividend_amount = data_line[date_of_entry]['7. dividend amount']
        split_coefficient = data_line[date_of_entry]['8. split coefficient']

        date_variable = date_variable + 1

        query = Dump.get_or_none(Company = symbols, Date = date_of_entry)
        if query is not None:
            pass
        else:
            row = {
                'Company': symbols,
                'Date': date_of_entry,
                'Open': open,
                'High': high,
                'Low': low,
                'Close': close,
                'Adjusted_Close': adjusted_close,
                'Volume': volume,
                'Dividend_Amount': dividend_amount,
                'Split_Coefficient': split_coefficient
            }
            Dump.insert(row).execute()
    logging.info(f"Finished thread - {symbols} - " + datetime.utcnow().strftime("%H:%M:%S - %D"))
    database.close()
    print(thread_name + " done")

#Defines Thread Control - activates the thread script at 8am and pm, uses a wait as well,
#                         which may cause issues on slower devices if working with data takes too long
def Thread_Control(Companies_List):
    logging.info("Starting Thread_Control " + datetime.utcnow().strftime("%H:%M:%S - %D"))
    print("Test pass")
    Thread_initialisation(Companies_List)
    sleep(10)
    while True:
        time = datetime.utcnow()
        stripped_time = time.strftime("%H:%M:%S")
        if stripped_time == "08:00:00":
            Thread_initialisation(Companies_List)


#The model of the MariaDB table that is used, defined for generation via PeeWee
class Dump(Model):
    Company = CharField(100)
    Date = CharField(100)
    Open = CharField(100)
    High = CharField(100)
    Low = CharField(100)
    Close = CharField(100)
    Adjusted_Close = CharField(100)
    Volume = CharField(100)
    Dividend_Amount = CharField(100)
    Split_Coefficient = CharField(100)
    class Meta:
        database = database

#Start script - will check if logging is working and ask for confirmation to begin scraping
print("Welcome to ShitStocks Scraper \n ")
print("Starting StartUp....")
StartUp()
print("Checking log file....")
try:
    logging.basicConfig(filename="ShitStockLogs.log", encoding="utf-8", level=logging.DEBUG)
    logging.debug("Intialising logs " + datetime.utcnow().strftime("%H:%M:%S - %D"))
    logging.getLogger("peewee").setLevel(logging.WARNING)
except:
    print("Logging failed, exiting....")
    exit()
How_many_in_DB, Companies_List = StartUp()
print("StartUp complete, variables generated \n ")
orders = input("Begin scraping? \nY/N: ")
db_total = len(database.get_tables())
if db_total <1:
    database.create_tables([Dump])
if orders == "N":
        print(" \nClosing session")
        exit()
if orders == "Y":
    Thread_Control(Companies_List)