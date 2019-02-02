import requests
import pandas as pd
import datetime as dt

base_url = ('https://www.nordnet.no/mux/popups/marknaden/'
            'aktiehemsidan/avslut.html?containerid=avslut&'
            'identifier={}&marketplace={}&limit=1000000')

stocks = {'NEL': base_url.format(57456, 15),
          'SSO': base_url.format(1301292, 15),
          'VELO': base_url.format(36992, 14),
          'EOLU_B': base_url.format(66174, 11)}


def get_orderbook(stock, url):
    today_date = dt.date.today() - dt.timedelta(days=1)
    r = requests.get(url)
    
    columns = ['time', 'volume', 'price', 'buyer', 'seller']
    orderbook = {col: [] for col in columns}
    
    tr_elements = [line for line in r.text.split("</tr>")][1:-1]
    for element in tr_elements:
        td_elements = [td for td in element.split('<td')]
        buyer = td_elements[1].split("title=")[1].split(">")[0].replace('"','').strip()
        seller = td_elements[2].split("title=")[1].split(">")[0].replace('"','').strip()
        volume = int(td_elements[3].replace(">","").replace("</td","").replace(" ",""))
        price = float(td_elements[4].split('</span>')[0].split('>')[-1].replace(",","."))
        time = dt.datetime.strptime(td_elements[5].split('"last">')[1].split('<img')[0].strip(),
                '%H:%M:%S').time()
        timestamp = dt.datetime.combine(today_date, time)#.timestamp()
        orderbook['time'].append(timestamp)
        orderbook['volume'].append(volume)
        orderbook['price'].append(price)
        orderbook['buyer'].append(buyer)
        orderbook['seller'].append(seller)

    orderbook_frame = pd.DataFrame(orderbook, columns=columns)
    orderbook_frame.to_csv(f'{stock}_{today_date.strftime("%m_%d")}.pd',
                           sep=',', encoding='utf-8', index=False)

for stock, url in stocks.items():
    get_orderbook(stock, url)
