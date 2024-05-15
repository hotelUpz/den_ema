from parametrs import PARAMS
from log import log_exceptions_decorator
import pandas as pd
import time
import hmac
import hashlib
import requests

class CONNECTOR_BINANCEE(PARAMS):
    def __init__(self) -> None:
        super().__init__()
        self.headers = {
            'X-MBX-APIKEY': self.api_key
        } 

    @log_exceptions_decorator
    def get_signature(self, params):
        params['timestamp'] = int(time.time() *1000)
        params_str = '&'.join([f'{k}={v}' for k,v in params.items()])
        hash = hmac.new(bytes(self.api_secret, 'utf-8'), params_str.encode('utf-8'), hashlib.sha256)        
        params['signature'] = hash.hexdigest()
        return params
   
    @log_exceptions_decorator
    def HTTP_request(self, url, **kwards):
        response = None
        multipliter = 2

        for i in range(2):
            try:
                response = requests.request(url=url, **kwards)
                return response.json()
            except Exception as ex:
                print(ex)
                time.sleep((i+1) * multipliter)

        return None

class BINANCE_API(CONNECTOR_BINANCEE):
    def __init__(self) -> None:
        super().__init__()       
# ////////////////////////////////////////get api: //////////////////////////////////
    @log_exceptions_decorator
    def get_excangeInfo(self):     
        return self.HTTP_request(self.exchangeInfo_url, method='GET', headers=self.headers)
    
    @log_exceptions_decorator
    def get_all_tickers(self):       
        return self.HTTP_request(self.all_tikers_url, method='GET', headers=self.headers)
        
    @log_exceptions_decorator
    def get_all_orders(self, symbol):
        params = {
            'symbol': symbol,
            # 'limit': limit
        }
        params = self.get_signature(params)
        resp = self.HTTP_request(self.get_all_orders_url, method='GET', headers=self.headers, params=params)
        # print(resp)
        return resp

    @log_exceptions_decorator
    def get_klines(self, symbol):
        klines = None       
        params = {}
        params["symbol"] = symbol
        params["interval"] = self.interval
        # print(f"self.ema2_period: {self.ema2_period}")
        params["limit"] = int(self.max_period*2.5)
        params = self.get_signature(params)
        klines = self.HTTP_request(self.klines_url, method='GET', headers=self.headers, params=params)
        if klines:
            data = pd.DataFrame(klines).iloc[:, :6]
            data.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            data = data.set_index('Time')
            data.index = pd.to_datetime(data.index, unit='ms')
            return data.astype(float)        
        return

    @log_exceptions_decorator    
    def is_closing_position_true(self, symbol):
        positions = None
        params = {
            "symbol": symbol
        }
        params = self.get_signature(params)
        positions = requests.get(self.positions_url, headers=self.headers, params=params)
        if positions.status_code == 200:    
            positions = positions.json()                        
            for position in positions:
                if position['symbol'] == symbol and float(position['positionAmt']) != 0:
                    return   
            return True        
        return
    
# ///////////////////////////////////////////// post api: ////////////////////////////////////////////    
    @log_exceptions_decorator
    def set_margin_type(self, symbol, margin_type):                
        params = {}
        params['symbol'] = symbol
        params['margintype'] =  margin_type
        params['recvWindow'] = 5000
        params['newClientOrderId'] = 'CHANGE_MARGIN_TYPE'       
        params = self.get_signature(params)
        return self.HTTP_request(self.set_margin_type_url, method='POST', headers=self.headers, params=params)
        
    @log_exceptions_decorator
    def set_leverage(self, symbol, lev_size):                     
        params = {}
        params['symbol'] = symbol
        params['leverage'] = lev_size
        params = self.get_signature(params)
        # print(params)
        return self.HTTP_request(self.set_leverage_url, method='POST', headers=self.headers, params=params)

    @log_exceptions_decorator
    def make_order(self, symbol, qty, side, market_type, target_price): 
        print(symbol, qty, side, market_type, target_price)
        params = {}        
        params["symbol"] = symbol        
        params["type"] = market_type
        params["quantity"] = qty
        if market_type == 'STOP_MARKET' or market_type == 'TAKE_PROFIT_MARKET':
            params['stopPrice'] = target_price
            params['closePosition'] = True 
        params["side"] = side
        params['newOrderRespType'] = 'RESULT' # default 'ASK'
        params = self.get_signature(params)
        resp = self.HTTP_request(self.create_order_url, method='POST', headers=self.headers, params=params)
        # print(resp)
        return resp

    @log_exceptions_decorator
    def tralling_stop_order(self, symbol, qty, side, callback_rate, market_type='TRAILING_STOP_MARKET'):
        params = {}        
        params["symbol"] = symbol        
        params["type"] = market_type
        params["quantity"] = qty
        params['callbackRate'] = callback_rate
        params["side"] = side
        params["recvWindow"] = 5000
        params['newOrderRespType'] = 'RESULT' # default 'ASK'
        params = self.get_signature(params)
        resp = self.HTTP_request(self.create_order_url, method='POST', headers=self.headers, params=params)
        # print(resp)
        return resp
    
    # //////////////////////////////////// delete api:
    @log_exceptions_decorator
    def cancel_all_open_orders(self, symbol):
        params = {
            'symbol': symbol            
        }
        params = self.get_signature(params)
        resp = self.HTTP_request(self.cancel_all_orders_url, method='DELETE', headers=self.headers, params=params)
        return resp