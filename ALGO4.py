import signal
import requests
from time import sleep
import sys

class ApiException(Exception):
    pass

def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

API_KEY = {'X-API-key': 'I3327HC8'}
s = requests.Session() # assigns the SESSION() function from REQUESTS to the variable "s"
s.headers.update({'X-API-key': 'I3327HC8'})
shutdown = False

SPEEDBUMP = 1
GROSS_LIMIT = 500000
NET_LIMIT = 25000
MAX_VOLUME = 5000
MAX_ORDERS = 5
SPREAD=.05

def get_news():
    resp = s.get('http://localhost:9999/v1/news')
    if resp.ok:
        news = resp.json()
        

def get_tick(session):
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('Authorization error Please check API key.')
    
def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = s.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('Authorization error Please check API key.')

def open_sells(session):
    resp = s.get('http://localhost:9999/v1/orders?status=OPEN')
    if resp.ok:
        open_sells_volume = 0
        ids = []
        price = []
        order_volumes = []
        volume_filled = []
        
        open_orders = resp.json()
        for order in open_orders:
            if order ['action'] == 'SELL':
                volume_filled.append(order['quantity_filled'])
                order_volumes.append(order['quantity'])
                open_sells_volume = open_sells_volume + order['quantity']
                price.append(order['price'])
                ids.append(order['order_id'])
    return volume_filled, open_sells_volume, ids, price, order_volumes

def open_buys(session):
    resp = s.get('http://localhost:9999/v1/orders?status=OPEN')
    if resp.ok:
        open_buys_volume = 0
        ids = []
        price = []
        order_volumes = []
        volume_filled = []
        
        open_orders = resp.json()
        for order in open_orders:
            if order ['action'] == 'BUY':
                volume_filled.append(order['quantity_filled'])
                order_volumes.append(order['quantity'])
                open_buys_volume = open_buys_volume + order['quantity']
                price.append(order['price'])
                ids.append(order['order_id'])
                
    return volume_filled, open_buys_volume, ids, price, order_volumes

def get_bid_ask(ticker): # defines a function called "get_bid_ask" that expects a piece of information that is assigned the variable name "ticker" which is used inside the function "get_bid_ask". The value of ticker comes from the value in the brackets of the function call on line 52, which is TICKER_SYMBOL, which is "MC"
    payload = {'ticker': ticker} # assigns the value of "ticker" to the key (or name) "ticker" in the dictionary "payload" - note the curly brackets surrounding the dictionary
    resp = s.get('http://localhost:9999/v1/securities/book', params = payload) # attaches the dictionary "payload" to the parameters ("params") that are included in the "get" request sent to RIT; in this case "params" includes the ticker symbol that tells RIT which order book to retrieve
    if resp.ok:
        book = resp.json() # stores the parsed data from "resp" in a variable named "book"; "book" is a list that contains two lists (one called "bids" and one called "asks") - similar to a folder called "book" that has two sub-folders, one called "bids" and the other called "asks" - and each of the "bids" and "asks" lists are made up of a list of items, with each item in the list being a dictionary that contains the information for each order in the order book
        bid_book = book['bids'] # creates a new list called "bid_book" composed of all the items/dictionaries from the "bids" list in "book"
        ask_book = book['asks'] # creates a new list called "ask_book" composed of all the items/dictionaries from the "asks" list in "book"
        
        bid_price_fn = bid_book[0]['price'] # assigns the variable "bid_price_fn" the value for the key/name "price" in the first item/dictionary in the "bid_book" list (this is the highest bid price, or the "top of the book"; note that counting in Python starts at 0, so the first item in a list is item 0, the second item in a list is item 1, the third item in a list is item 2, etc. 
        ask_price_fn = ask_book[0]['price'] # assigns the variable "ask_price_fn" the value for the key/name "price" in the first item/dictionary in the "ask_book" list (this is the lowest ask price, or the "top of the book")
        
        bid_volume_fn = sum([item['quantity'] - item['quantity_filled'] for item in bid_book if item["price"] == bid_price_fn]) # assigns the variable "bid_volume_fn" the value calculated by summing the outstanding bid volumes (the "quantity" is the volume of the bid when the order was entered, "quantity filled" is the amount that has been bought, the difference is the remaining volume still bid in the market) for all bids that have a bid price equal to "bid_price_fn"; note: testing an equality uses two equal signs (==), a single equal sign assigns a value
        ask_volume_fn = sum([item['quantity'] - item['quantity_filled'] for item in ask_book if item["price"] == ask_price_fn]) # assigns the variable "ask_volume_fn" the value calculated by summing the outstanding ask volumes (the "quantity" is the volume of the ask when the order was entered, "quantity filled" is the amount that has been sold, the difference is the remaining volume still ask in the market) for all asks that have an ask price equal to "ask_price_fn"
      
        return bid_price_fn, bid_volume_fn, ask_price_fn, ask_volume_fn

def buy_sell(session, sell_price, buy_price):
    for i in range(MAX_ORDERS):
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': sell_price, 'action': 'SELL'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': buy_price, 'action': 'BUY'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': sell_price, 'action': 'SELL'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': buy_price, 'action': 'BUY'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': sell_price, 'action': 'SELL'})
        s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX', 'type': 'LIMIT', 'quantity': MAX_VOLUME, 'price': buy_price, 'action': 'BUY'})
        
def re_order(session, number_of_orders, ids, volumes_filled, volumes, price, action):
    for i in range(number_of_orders):
        id = ids[i]
        volume = volumes[i]
        volume_filled = volumes_filled[i]
        if(volume_filled != 0):
            volume = MAX_VOLUME - volume_filled
            
        deleted = s.delete('http://localhost:9999/v1/orders/{}'.format(id))
        if(deleted.ok):
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RGLD','type': 'LIMIT', 'quantity': volume, 'price': price, 'action': action})

    for i in range(number_of_orders):
        id = ids[i]
        volume = volumes[i]
        volume_filled = volumes_filled[i]
        if(volume_filled != 0):
            volume = MAX_VOLUME - volume_filled
            
        deleted = s.delete('http://localhost:9999/v1/orders/{}'.format(id))
        if(deleted.ok):
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'RFIN','type': 'LIMIT', 'quantity': volume, 'price': price, 'action': action})
            
    for i in range(number_of_orders):
        id = ids[i]
        volume = volumes[i]
        volume_filled = volumes_filled[i]
        if(volume_filled != 0):
            volume = MAX_VOLUME - volume_filled
            
        deleted = s.delete('http://localhost:9999/v1/orders/{}'.format(id))
        if(deleted.ok):
            s.post('http://localhost:9999/v1/orders', params = {'ticker': 'INDX','type': 'LIMIT', 'quantity': volume, 'price': price, 'action': action})

def main():
    
    news = []
    news[0]
    buy_ids = []
    buy_prices = []
    buy_volumes = []
    volume_filled_buys = []
    open_buys_volume = 0
    
    sell_ids = []
    sell_prices = []
    sell_volumes = []
    volume_filled_sells = []
    open_sells_volume = 0
    
    single_side_filled = False
    single_side_transaction_time = 0 
    
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        
        while tick > 5 and tick < 295 and not shutdown:
            volume_filled_sells, open_sells_volume, sell_ids, sell_prices, sell_volumes = open_sells(s)
            volume_filled_buys, open_buys_volume, buy_ids, buy_prices, buy_volumes = open_buys(s)
            bid_price, ask_price = ticker_bid_ask(s, 'RGLD')
            bid_price, ask_price = ticker_bid_ask(s, 'RFIN')
            bid_price, ask_price = ticker_bid_ask(s, 'INDX')
            
            if(open_sells_volume == 0 and open_buys_volume == 0):
                single_side_filled = False
                
                bid_ask_spread = ask_price - bid_price
                
                sell_price = ask_price
                buy_price = bid_price
                
                if(bid_ask_spread >= SPREAD):
                    buy_sell(s, sell_price, buy_price)
                    sleep(SPEEDBUMP)
            else:
                if(not single_side_filled and (open_buys_volume == 0 or open_sells_volume == 0)):
                    single_side_filled = True
                    single_side_transaction_time = tick
                
                if(open_sells_volume == 0):
                    if(buy_price == bid_price):
                        continue
                    
                    elif(tick - single_side_transaction_time >= 3):
                        next_buy_price = bid_price + .01
                        potential_profit = sell_price - next_buy_price - .02
                        
                        if(potential_profit >= .01 or tick - single_side_transaction_time >= 6):
                            action = 'BUY'
                            number_of_orders = len(buy_ids)
                            buy_price = bid_price + .01
                            price = buy_price
                            ids = buy_ids
                            volumes = buy_volumes
                            volumes_filled = volume_filled_buys
                            
                            re_order(s, number_of_orders, ids, volumes_filled, volumes, price, action)
                            sleep(SPEEDBUMP)
                            
                    elif(open_buys_volume == 0):
                        if(sell_price == ask_price):
                            continue
                        elif(tick - single_side_transaction_time >= 3):
                            next_sell_price = ask_price- .01
                            potential_profit = next_sell_price - buy_price - .02
                            
                            if(potential_profit >= .01 or tick - single_side_transaction_time >= 6):
                                action = 'SELL'
                                number_of_orders = len(sell_ids)
                                sell_price = ask_price - .01
                                price = sell_price
                                ids = sell_ids
                                volumes = sell_volumes
                                volumes_filled = volume_filled_sells
                                
                                re_order(s, number_of_orders, ids, volumes_filled, volumes, price, action)
                                sleep(SPEEDBUMP)



        tick = get_tick(s)
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()