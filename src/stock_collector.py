import time
import bs4
import requests
import pandas as pd
import datetime as dt


def get_orderbook(identifier, market):
    url = ('https://www.nordnet.no/mux/popups/marknaden/'
                'aktiehemsidan/avslut.html?containerid=avslut&'
                f'identifier={identifier}&marketplace={market}&limit=1000000')
    today_date = dt.date.today()
    r = requests.get(url)
    columns = ['time', 'volume', 'price', 'buyer', 'seller']
    orderbook = {col: [] for col in columns}
    ticker = r.text.split('</h1>')[0].split('</span>')[-1].strip().replace(' ','_')
    print(f'Retrieving orderbook for {ticker}')
    tr_elements = [line for line in r.text.split("</tr>")][1:-1]
    for element in tr_elements:
        td_elements = [td for td in element.split('<td')]
        buyer = td_elements[1].split("title=")[1].split(">")[0].replace('"','').strip()
        seller = td_elements[2].split("title=")[1].split(">")[0].replace('"','').strip()
        volume = int(td_elements[3].replace(">","").replace("</td","").replace(" ",""))
        price = float(td_elements[4].split('</span>')[0].split('>')[-1].replace(",",".").replace(' ', ''))
        time = dt.datetime.strptime(td_elements[5].split('"last">')[1].split('<img')[0].strip(),
                '%H:%M:%S').time()
        timestamp = dt.datetime.combine(today_date, time)#.timestamp()
        orderbook['time'].append(timestamp)
        orderbook['volume'].append(volume)
        orderbook['price'].append(price)
        orderbook['buyer'].append(buyer)
        orderbook['seller'].append(seller)

    orderbook_frame = pd.DataFrame(orderbook, columns=columns)
    orderbook_frame.to_csv(f'../data/{ticker}_{market}_{today_date.strftime("%m_%d")}.pd',
                           sep=',', encoding='utf-8', index=False)


def get_stocks(url):
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, 'lxml')
    hits = soup.find_all('a', class_=('underline'))
    stocks = dict()
    for hit in hits:
        name = ''.join(s for s in hit.text.replace(' ', 'abcde') if s.isalnum())
        name = name.replace('abcde', '_')
        id_and_m = [k.split('=')[1] for k in hit['href'].split('?')[1].split('&')]
        stocks[name] = id_and_m
    return stocks


if __name__=='__main__':
    market_names = ['Norge', 'Sverige', 'Danmark']
    markets = []
    for m in market_names:
        time.sleep(3)
        markets.append(get_stocks('https://www.nordnet.no/mux/web/marknaden/kurslista/'
                                f'aktier.html?marknad={m}&lista=1_1&large=on&mid=on&'
                                 'small=on&sektor=0&subtyp=price&sortera=aktie&'
                                 'sorteringsordning=stigande'))
    
    for market in markets:
        for stock in market.values():
            time.sleep(2)
            get_orderbook(*stock)
