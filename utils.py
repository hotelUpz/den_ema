import time
from datetime import datetime as dttm
from random import choice
import math
import decimal
from log import log_exceptions_decorator

def server_to_utc_difference_counter():
    server_time_naive = dttm.now()
    # print(f"server_time_naive: {server_time_naive}")
    utc_time = dttm.utcnow()
    # print(f"utc_time: {utc_time}")
    time_difference = server_time_naive - utc_time
    total_seconds = abs(time_difference.total_seconds()) * 1000
    total_seconds = math.ceil(total_seconds)
    if total_seconds < 10:
        return 0
    return total_seconds

time_correction_val = server_to_utc_difference_counter()
# print("Разница между серверным временем в милисекундах:", time_correction_val)

class UTILS():
    def __init__(self):  
        # super().__init__()
        pass

    @log_exceptions_decorator
    def date_of_the_month(self):        
        current_time = time.time()        
        datetime_object = dttm.fromtimestamp(current_time)       
        formatted_time = datetime_object.strftime('%d')
        return int(formatted_time) 
        
    def milliseconds_to_datetime(self, milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        time = dttm.utcfromtimestamp(seconds)
        # milliseconds_str = str(milliseconds).zfill(3)
        # return time.strftime('%Y-%m-%d %H:%M:%S') + '.' + milliseconds_str
        return time.strftime('%Y-%m-%d %H:%M:%S')    
    
    @log_exceptions_decorator
    def time_calibrator(self, kline_time, time_frame):
        current_time = time.time()
        time_in_seconds = 0

        if time_frame == 'm':
            time_in_seconds = kline_time * 60
        elif time_frame == 'h':
            time_in_seconds = kline_time * 3600
        elif time_frame == 'd':
            time_in_seconds = kline_time * 86400

        next_interval = math.ceil(current_time / time_in_seconds) * time_in_seconds
        wait_time = next_interval - current_time
        return int(wait_time)
    
    @log_exceptions_decorator
    def usdt_to_qnt_converter(self, symbol, depo, symbol_info, cur_price):
        symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == symbol), None)
        # print(symbol_data)
        # //////////////////////
        quantity_precision = int(float(symbol_data['quantityPrecision']))
        price_precision = int(float(symbol_data['pricePrecision']))
        print(f"quantity_precision: {quantity_precision}")
        min_notional = int(float(next((f['notional'] for f in symbol_data['filters'] if f['filterType'] == 'MIN_NOTIONAL'), 0)))
        if depo <= min_notional:
            depo = min_notional
        if quantity_precision == 0 and (depo / cur_price) < 1:
            return "Too_litle_size", None            
        return round(depo / cur_price, quantity_precision), price_precision
    
    @log_exceptions_decorator
    def from_anomal_view_to_normal(self, strange_list):
        normal_list = [] 
        # /////////////////////////////////////////////////////
        for x in strange_list:
            x_f = decimal.Decimal(str(x))
            normal_list.append(format(x_f, 'f'))
        print(', '.join(normal_list))                         
