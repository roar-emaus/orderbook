import sqlite3 as sq
import bokeh.plotting as bp
import bokeh.layouts as bl
import numpy as np
import pandas as pd
import datetime as dt


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sq.connect(db_file)
        print(sq.version)
    except Error as e:
        print(e)
    finally:
        conn.close()
        

sql_create_stocks_table = """ CREATE TABLE IF NOT EXISTS stocks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    market_id integer NOT NULL,
                                    stock_id integer NOT NULL
                                ); """

sql_create_sale_table = """ CREATE TABLE IF NOT EXISTS sales (
                                id integer PRIMARY KEY,
                                time text NOT NULL,
                                buyer text NOT NULL,
                                seller text NOT NULL,
                                price real NOT NULL,
                                volume integer NOT NULL
                                ); """

with open('stocks.txt' ,'r') as stocks:
    for line in stocks:
        line = line.strip().split(',')

if __name__=='__main__':
    create_connection('markets.db')
