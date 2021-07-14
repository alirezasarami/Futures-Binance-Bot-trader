# Futures-Binance-Bot-trader
Example of Binance futures bot with WMAs indicators

Hello
This project is a very simple example of building a Bainance bot trader.
The video of making this bot has been uploaded on YouTube to:
To work with this bot, you must enter the api key and secret key in the config.py file.


Instruction youtube video link = https://www.youtube.com/watch?v=tl57JIFQfyU


in BinanceFuturesPy you should change new_order function lines : 

BinanceFuturesPY -> futurespy.py -> line 538 - >

    def new_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: float,
        timeInForce: float = None,
        reduceOnly: bool = False,
        price: float = None,
        newClientOrderId: str = None,
        stopPrice: float = None,
        workingType: str = None,
        positionSide : str = None,
        closePosition : bool = False,
        priceProtect : bool = False,
    ):
        """
        POST
        
        Choose side:                SELL or BUY
        Choose quantity:            0.001
        Choose price:               7500

        To change order type    ->  orderType = 'MARKET'
        To change time in force ->  timeInForce = 'IOC'
        """

        req = "order?"

        querystring = {
            "symbol": symbol,
            "side": side,
            "type": orderType,
            "quantity": quantity
        }
	
        if timeInForce is not None:
            querystring["timeInForce"] = timeInForce
        if positionSide is not None :
        	querystring["positionSide"] = positionSide
        
        if closePosition is not False :
        	querystring["closePosition"] = closePosition
        
        if priceProtect is not False :
        	querystring["priceProtect"] = priceProtect
        	
        if reduceOnly is not False :
        	querystring["reduceOnly"] = reduceOnly
        if price is not None:
            querystring["price"] = price
        if newClientOrderId is not None:
            querystring["newClientOrderId"] = newClientOrderId
        if stopPrice is not None:
            querystring["stopPrice"] = stopPrice
        if workingType is not None:
            querystring["workingType"] = workingType
        querystring["timestamp"] = self.timestamp()
        querystring["recvWindow"] = self.recvWindow

        querystring = urllib.parse.urlencode(querystring)

        return self._post_request(req, querystring)
