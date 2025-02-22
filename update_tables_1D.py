import os
import time
import pandas as pd
import yfinance as yf
from constants import *
from sqlalchemy import text
from datetime import datetime
from dotenv import load_dotenv
from datetime import timedelta
from my_fyers_model import MyFyersModel
from trade_utils.db_connection import MySQLConnector

# Load environment variables
load_dotenv(dotenv_path='config/.env')

# Use environment variables for credentials
db_user = os.getenv('DB_USER').strip()  # Strip to remove unwanted spaces
db_password = os.getenv('DB_PASSWORD')
connector = MySQLConnector(db_user, db_password)

fy_model = MyFyersModel()
today_date = datetime.today().strftime("%Y-%m-%d")


def get_table_name_last_date():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'fnodatabase';"
    engine = connector.get_mysql_connection()
    table_date_time = {}
    old_date_time = {}

    with engine.connect() as connection:
        result = connection.execute(text(query))
        all_tables = [table[0] for table in list(result) if table[0].endswith('_1D') or table[0].endswith('_1d')]
        print(all_tables)
        for table_name in all_tables:
            query = f"SELECT * FROM {table_name};"
            table_data = connection.execute(text(query))
            last_date = list(table_data)[-1]

            if issubclass(type(last_date[1]), str):
                last_date = last_date[1].split('+')[0]
                datetime_object = datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S')
            else:
                datetime_object = last_date[1]
            old_date_time[table_name] = str(datetime_object.__format__("%Y-%m-%d"))

            # yesterday date
            last_date = datetime_object + timedelta(days=1)
            table_date_time[table_name] = str(last_date.__format__("%Y-%m-%d"))
    return table_date_time


def update_all_tables_fyers():
    for table_name, last_date in get_table_name_last_date().items():
        print(last_date, today_date)

        if last_date != today_date:
            dates = pd.date_range(start=last_date, end=today_date).tolist()
            master_data = []
            symbol = None

            for range_from, range_to in zip(dates, dates[1:]):
                if table_name == 'finnifty_1D' or table_name == 'finnifty_1d':
                    symbol = OPTION_SYMBOLS_FYERS['finnifty']
                elif table_name == 'indiavix_1D' or table_name == 'indiavix_1d':
                    symbol = OPTION_SYMBOLS_FYERS['indiavix']
                elif table_name == 'nifty50_1D' or table_name == 'nifty50_1d':
                    symbol = OPTION_SYMBOLS_FYERS['nifty50']
                elif table_name == 'niftybank_1D' or table_name == 'niftybank_1d':
                    symbol = OPTION_SYMBOLS_FYERS['niftybank']
                elif table_name == 'midnifty_1D' or table_name == 'midnifty_1d':
                    symbol = OPTION_SYMBOLS_FYERS['midnifty']
                elif table_name == 'sensex_1D' or table_name == 'sensex_1d':
                    symbol = OPTION_SYMBOLS_FYERS['sensex']
                else:
                    print(f'Invalid symbol name : "{table_name}"')

                data = {
                    "symbol": symbol,
                    "resolution": "1D",
                    "date_format": "1",
                    "range_from": range_from.strftime("%Y-%m-%d"),
                    "range_to": range_to.strftime("%Y-%m-%d"),
                    "cont_flag": "1"
                }

                response = fy_model.get_history(data=data)
                master_data += response['candles']

            df = pd.DataFrame(master_data, columns=["epoc", "open", "high", "low", "close", "volume"])
            df['timestamp'] = pd.to_datetime(df['epoc'], unit='s', utc=True).map(lambda x: x.tz_localize(None))
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            df.drop_duplicates(inplace=True)
            df['volume'] = 0

            df.to_sql(name=table_name, con=connector.get_mysql_connection(), index=False, if_exists='append')
            print(df.head())
            print(df.tail())
            time.sleep(1)
            print(f'{table_name} is updated...')
            print('\n')
        else:
            print(f'{table_name} : table is already up to date ...')


def update_all_tables_yahoo():
    global symbol
    for table_name, last_date in get_table_name_last_date().items():

        if table_name == 'finnifty_1D' or table_name == 'finnifty_1d':
            symbol = OPTION_SYMBOLS_YAHOO['finnifty']
        elif table_name == 'indiavix_1D' or table_name == 'indiavix_1d':
            symbol = OPTION_SYMBOLS_YAHOO['indiavix']
        elif table_name == 'nifty50_1D' or table_name == 'nifty50_1d':
            symbol = OPTION_SYMBOLS_YAHOO['nifty50']
        elif table_name == 'niftybank_1D' or table_name == 'niftybank_1d':
            symbol = OPTION_SYMBOLS_YAHOO['niftybank']
        else:
            print(f'Invalid symbol name : "{table_name}"')

        # print(table_name, "===", symbol)
        data = yf.Ticker(symbol)
        # pass the parameters as the taken dates for start and end
        # df = data.history(start=start_date, end=end_date)
        df = data.history(period="1d", interval="1d")
        df = df.drop(['Dividends', 'Stock Splits'], axis=1)
        df.reset_index(inplace=True)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
        # df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True).map(lambda x: x.tz_localize(None))
        df['volume'] = 0
        df = df.round(2)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(df.head())
        print(df.tail())
        df.to_sql(name=table_name, con=connector.get_mysql_connection(), index=False, if_exists='append')
        print(f'{table_name} is updated...\n')


ask = input("do you want to update 1 day data (Y/n) : ")

if ask.lower() == 'y':
    update_all_tables_fyers()
    # update_all_tables_yahoo()
