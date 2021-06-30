#import requirements module
import websocket , config , json ,talib , numpy ,time
from BinanceFuturesPy.futurespy import Client , MarketData
from datetime import datetime

#connect trader bot to binance API
#if use tesnet.binance API you should tesnet = True
#if use binance API you should tesnet = False
client = Client(api_key=config.API_KEY,
                        sec_key=config.API_SECRET , testnet=True)

#socket url for stream API binance
socket = f"wss://stream.binance.com:9443/ws/{config.symbol.lower()}@kline_1m"

candle_closed_list = []

#false = None position , true = position opened
position = False

#false = short , true = long
type_position = True

#get balance of futur account wallet (usdt , bnb , busd)
def balance():
    try:
        blnc = client.balance()
        for counter in blnc:
            for value in counter:
                if value == 'asset':
                    print(value , ' >> ' , counter[value])
                if value == 'balance' :
                    print(value , ' >> ' , counter[value])
                if value == 'withdrawAvailable':
                    print(value , ' >> ' , counter[value])

    except Exception as Error:
        print(Error)

#create new order
def new_order(symbol , type , quantity , side , priceProtect = False ,
              closePosition = False , price = None, stopPrice = None , positionSide = None ,
              reduceonly = False , timeInForce = None):
    try:
        result = client.new_order(side=side,
                                  quantity=quantity,
                                  symbol=symbol,
                                  reduceOnly=reduceonly,
                                  positionSide=positionSide,
                                  stopPrice = stopPrice,
                                  timeInForce = timeInForce,
                                  price= price,
                                  closePosition= closePosition,
                                  priceProtect= priceProtect ,
                                orderType=type)

        print(result)
        return result
    except Exception as Error:
        print(Error)

#this function use for change leverage
def change_initial_leverage(leverage):
    try:
        result = client.change_leverage(leverage)
        print(result)
    except Exception as Error:
        print(Error)

#print history of last close position
def HPrint(history):
    for value in history[0]:
        if value == 'time':
            print('time >> ', datetime.fromtimestamp(history[0]['time'] / 1e3))

        elif value == 'realizedPnl':
            print(value, f' >> {float(history[0][value])} ')

        else:
            print(value , f' >> {history[0][value]} ')


#get history from 5 days ago until now
def history():

    dt2 = datetime.now()
    dt = datetime(dt2.year, dt2.month, dt2.day-5)
    milliseconds = int(round(dt.timestamp() * 1000))
    now = int(round(dt2.timestamp())*1000)
    his2 = client.trade_list(limit=1000 , startTime=milliseconds , endTime=now)
    HPrint(his2)

#get information of open position
def position_info():
    posInf = client.position_info()
    for counter in posInf:
        if counter['symbol'] == config.symbol:
            print(counter)
            return counter

#calculator stop loss price
def stop_loss(positionInfo):
    close = float(positionInfo['entryPrice'])
    percent = (0.3*close)/100
    if type_position == True:
        return close-percent
    else:
        return close+percent

#calculator take profit price
def take_profit(positionInfo):
    close = float(positionInfo['markPrice'])
    return close

#close orders function
def close_orders():
    client.cancel_all_open_orders(symbol=config.symbol)

#open connection message when trader bot connect to binance stream
def on_open(ws):
    print('open connection')

#close connection message when trader bot disconnect from binance stream
def on_close(ws):
    print('close connection')

#get information candle and do my strategy
def on_message(ws , message):
    global candle_closed_list
    global position
    global type_position
    # print('this message -> ' , message)
    jsonmessage = json.loads(message)
    candle = jsonmessage['k']
    candle_closed = candle['x']
    if candle_closed:
        candle_closed_list.append(float(candle['c']))
        # print('append candle close' , candle_closed_list)
        print(f'candle open on {candle["o"]} and  close on {candle["c"]}')
        if len(candle_closed_list) > config.WMAUP:

            close_np = numpy.array(candle_closed_list)
            WMAUP = talib.WMA(close_np, config.WMAUP)
            WMADOWN = talib.WMA(close_np, config.WMADOWN)

            if is_cross(WMAUP , WMADOWN):
                if WMAUP[-1] > WMADOWN[-1]:
                    print(f'WMAUP{config.WMAUP}({WMAUP[-1]}) > WMADOWN{config.WMADOWN}({WMADOWN[-1]})')
                    #sell position long and let's short
                    if position == True and type_position == True: #opened long position
                        # order = new_order(symbol=config.symbol, type='TAKE_PROFIT_MARKET', quantity=config.buy_quantity, side='SELL',
                        #                   reduceonly=True , stopPrice=take_profit(position_info()))
                        order = client.new_order(symbol = config.symbol , orderType= 'MARKET' , quantity = config.buy_quantity , side = 'SELL' , reduceOnly=True)
                        close_orders()
                        print('close position long >> ' , history())
                        position = False

                    if position == False :
                        type_position = False
                        order = new_order(symbol=config.symbol, type='MARKET', quantity=config.buy_quantity, side='SELL')
                        SLP = int(stop_loss(position_info()))
                        order1 = new_order(symbol=config.symbol, type='STOP_MARKET', quantity=config.buy_quantity,
                                           side='BUY', stopPrice=SLP, reduceonly=True)
                        print('open position short and stop loss order >> ', order , order1)
                        position = True

                if WMAUP[-1] < WMADOWN[-1]:
                    print(f'WMAUP{config.WMAUP}({WMAUP[-1]}) < WMADOWN{config.WMADOWN}({WMADOWN[-1]})')

                    # sell position short and let's long
                    if position == True and type_position == False: #opened short position
                        # order = new_order(symbol=config.symbol, type='TAKE_PROFIT_MARKET', quantity=config.buy_quantity, side='BUY',
                        #                   reduceonly=True , stopPrice=take_profit(position_info()))
                        order = client.new_order(symbol = config.symbol , orderType= 'MARKET' , quantity = config.buy_quantity , side = 'BUY' , reduceOnly=True)
                        close_orders()
                        print('close position short >> ' , history())
                        position = False

                    if position == False :
                        type_position = True
                        order = new_order(symbol=config.symbol, type='MARKET', quantity=config.buy_quantity, side='BUY')
                        SLP = int(stop_loss(position_info()))
                        order1 = new_order(symbol=config.symbol, type='STOP_MARKET',
                                                    quantity=config.buy_quantity, priceProtect= True ,
                                           side='SELL', stopPrice=SLP ,reduceonly=True)
                        print('open position long and stop loss order >> ' , order , order1)
                        position = True

#WMAs cross eachother function
def is_cross(WMAUP , WMADOWN):

    if WMAUP[-1] > WMADOWN[-1] and WMADOWN[-2] > WMAUP[-2]:
        print(f'WMAUP{config.WMAUP} cross form WMADOWN{config.WMADOWN}')
        return True
    elif WMAUP[-1] < WMADOWN[-1] and WMADOWN[-2] < WMAUP[-2]:
        print(f'WMADOWN{config.WMADOWN} cross form WMAUP{config.WMAUP}')
        return True
    else:
        print('not cross')
        return False

# change_initial_leverage(10)
# ws = websocket.WebSocketApp(socket , on_open= on_open , on_close= on_close , on_message= on_message)
# ws.run_forever()
