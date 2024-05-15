from datetime import datetime, timedelta
from techniques import STRATEGY
from coinss_filter import COInN_FILTERR
from log import log_exceptions_decorator

class STOP_LOGIC(STRATEGY):
    def __init__(self):  
        super().__init__()  

    @log_exceptions_decorator
    def calculate_stop_loss_ratio(self, direction, enter_price, candles_df, stop_loss_type, fixed_stop_loss_ratio_val):
        # /////////////////////////////////////////////////////
        if enter_price == 0:
            return
        stop_loss_ratio = None
        period = int(candles_df.shape[0]/ 2.5) + 1  
        if stop_loss_type == 'FIXED':
            return fixed_stop_loss_ratio_val
        if stop_loss_type == 'ATR_VAL':
            atr_period = period 
            # atr_period = int(candles_df.shape[0]) - 1
            _, atr_value  = self.calculate_atr(candles_df, atr_period)
            return (atr_value / enter_price) * 1.1   

        if direction == 1:
            if stop_loss_type == 'LAST_MIN':
                lows = candles_df['Low']
                local_minima = lows.rolling(window=period, min_periods=period).min()
                last_local_minima = local_minima[local_minima.index < candles_df.index[-1]].iloc[-1]
                if last_local_minima >= enter_price:
                    return fixed_stop_loss_ratio_val
                else:
                    return ((enter_price - last_local_minima) / enter_price)* 1.1
            elif stop_loss_type == 'ABSOLUTE_MIN':
                absolute_min = candles_df['Low'].min()
                if absolute_min >= enter_price:
                    return fixed_stop_loss_ratio_val
                else:
                    return ((enter_price - absolute_min) / enter_price)* 1.1
        elif direction == -1:
            if stop_loss_type == 'LAST_MIN':
                highs = candles_df['High']
                local_maxima = highs.rolling(window=period, min_periods=period).max()
                last_local_maxima = local_maxima[local_maxima.index > candles_df.index[0]].iloc[-1]
                if last_local_maxima <= enter_price:
                    return fixed_stop_loss_ratio_val
                else:
                    return (abs(enter_price - last_local_maxima) / enter_price)* 1.1
            elif stop_loss_type == 'ABSOLUTE_MIN':
                absolute_max = candles_df['High'].max()
                if absolute_max <= enter_price:
                    return fixed_stop_loss_ratio_val
                else:
                    return (abs(enter_price - absolute_max) / enter_price)* 1.1

        if stop_loss_ratio is not None and stop_loss_ratio < 0.005:
            print(f"stop_loss_ratio < 0.004: {stop_loss_ratio < 0.005}")
            return 0.005
        return
    
class STATISTIC(COInN_FILTERR):
    def __init__(self):  
        super().__init__()

    @log_exceptions_decorator
    def last_statistic(self, symbol):        
        init_order_price, oposit_order_price = 0, 0
        try:
            orders = self.get_all_orders(symbol)
            orders= sorted(orders, key=lambda x: x["time"], reverse=True)
            the_orders = []
            for order in orders:
                if len(the_orders) == 2:
                    break
                try:
                    if order["status"] == 'FILLED':                        
                        the_orders = [order] + the_orders                        
                except:
                    pass
            init_order_price = float(the_orders[0].get('avgPrice', None))
            oposit_order_price = float(the_orders[1].get('avgPrice', None))
            if the_orders[0].get('side', None) == the_orders[1].get('side', None):
                return 0, 0, 0, self.depo
            if the_orders[0].get('side', None) == 'BUY':
                if init_order_price - oposit_order_price > 0:
                    return -1, init_order_price, oposit_order_price, self.depo
                elif init_order_price - oposit_order_price < 0:
                    return 1, init_order_price, oposit_order_price, self.depo
            elif the_orders[0].get('side', None) == 'SELL':
                if init_order_price - oposit_order_price > 0:
                    return 1, init_order_price, oposit_order_price, self.depo
                elif init_order_price - oposit_order_price < 0:
                    return -1, init_order_price, oposit_order_price, self.depo
        except Exception as ex:
            print(ex)
        return 0, init_order_price, oposit_order_price, self.depo
    
    # /////////////////////////////////////////////////////////////
    @log_exceptions_decorator
    def get_next_show_statistic_time(self):
        current_time = datetime.now()
        target_time = current_time.replace(hour=self.show_statistic_hour, minute=0, second=0)
        if current_time >= target_time:            
            target_time += timedelta(days=1)        
        return target_time
    @log_exceptions_decorator
    def show_statistic_signal(self, target_time): 
        now_time = datetime.now()      
        if now_time >= target_time:
            target_time = self.get_next_show_statistic_time()             
            return True, target_time          
        return False, target_time
    # /////////////////////////////////////////////////////////////

    @log_exceptions_decorator
    def statistic_calculations(self, daily_trade_history_list):
        result_statistic_dict = {}
        result_statistic_dict["symbol"] = self.symbol
        if not isinstance(daily_trade_history_list, list) or len(daily_trade_history_list) == 0:
            return {}

        try:
            win_count = sum(1 for win_los, _, _, _ in daily_trade_history_list if win_los == 1)
            loss_count = sum(1 for win_los, _, _, _ in daily_trade_history_list if win_los == -1)
            total_trade_count = win_count + loss_count
            if total_trade_count != 0:
                win_per = (win_count * 100) / total_trade_count
                loss_per = (loss_count * 100) / total_trade_count
                win_to_loss_statistik = f"{win_count}:{loss_count}"

                result_statistic_dict["Побед"] = win_count
                result_statistic_dict["Поражений"] = loss_count
                result_statistic_dict["Процент побед"] = win_per
                result_statistic_dict["Процент поражений"] = loss_per
                result_statistic_dict["Отношение побед к поражениям"] = win_to_loss_statistik
        except Exception as ex:
            print(ex)

        try:
            max_profit_abs = max((abs(init_order_price - oposit_order_price) / init_order_price) * last_depo for win_los, init_order_price, oposit_order_price, last_depo in daily_trade_history_list if win_los == 1)
            max_drawdown_abs = min(-1 * (abs(init_order_price - oposit_order_price) / init_order_price) * last_depo for win_los, init_order_price, oposit_order_price, last_depo in daily_trade_history_list if win_los == -1)
            total_profit_abs = sum((abs(init_order_price - oposit_order_price) / init_order_price) * last_depo for win_los, init_order_price, oposit_order_price, last_depo in daily_trade_history_list if win_los == 1)
            total_losses_abs = sum(-1 * (abs(init_order_price - oposit_order_price) / init_order_price) * last_depo for win_los, init_order_price, oposit_order_price, last_depo in daily_trade_history_list if win_los == -1)

            result_statistic_dict["Максимальная прибыль ($)"] = max_profit_abs
            result_statistic_dict["Максимальный убыток ($)"] = max_drawdown_abs
            result_statistic_dict["Общая прибыль ($)"] = total_profit_abs
            result_statistic_dict["Общий убыток ($)"] = total_losses_abs
        except Exception as ex:
            print(ex)

        # Вывод результатов в столбик
        result_string = ""
        for key, value in result_statistic_dict.items():
            result_string += f"{key}: {value}\n"

        return result_string