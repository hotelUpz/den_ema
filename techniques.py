import pandas_ta as ta
from log import log_exceptions_decorator

class INDICATORS():
    def __init__(self) -> None:
        pass     
    # pandas_ta library: .......................................  
    @log_exceptions_decorator 
    def calculate_ema(self, data, ema1_period, ema2_period, ema3_period):
        data[f"EMA{ema1_period}"] = ta.ema(data['Close'], length=ema1_period)
        data[f"EMA{ema2_period}"] = ta.ema(data['Close'], length=ema2_period)  
        if ema3_period is not None: 
            data[f"EMA{ema3_period}"] = ta.ema(data['Close'], length=ema3_period)    
        data.dropna(inplace=True)
        return data
    
    @log_exceptions_decorator
    def calculate_atr(self, data, atr_period):
        data[f"ATR{atr_period}"] = ta.atr(data['High'], data['Low'], data['Close'], length=atr_period)
        data.dropna(inplace=True)
        return data, data[f"ATR{atr_period}"].iloc[-1]

class STRATEGY(INDICATORS):
    def __init__(self) -> None:
        super().__init__()

    @log_exceptions_decorator 
    def get_signals(self, strategy_name, smoothing_crossover_condition, df, ema_list): 
        ema1_period = ema_list[0]
        ema2_period = ema_list[1]
        ema3_period = ema_list[2]            
        df = self.calculate_ema(df, ema1_period, ema2_period, ema3_period)
        smoothing_long_flag = False
        smoothing_short_flag = False
        if strategy_name == 'ema_crossover_2x':
            if smoothing_crossover_condition:
                if (df[f"EMA{ema1_period}"].iloc[-3] < df[f"EMA{ema2_period}"].iloc[-3]):
                    smoothing_long_flag = True
                elif (df[f"EMA{ema1_period}"].iloc[-3] > df[f"EMA{ema2_period}"].iloc[-3]):
                    smoothing_short_flag = True
            if (df[f"EMA{ema1_period}"].iloc[-1] > df[f"EMA{ema2_period}"].iloc[-1]) and ((df[f"EMA{ema1_period}"].iloc[-2] < df[f"EMA{ema2_period}"].iloc[-2]) or smoothing_long_flag):            
                return "LONG_SIGNAL"
            elif (df[f"EMA{ema1_period}"].iloc[-1] < df[f"EMA{ema2_period}"].iloc[-1]) and ((df[f"EMA{ema1_period}"].iloc[-2] > df[f"EMA{ema2_period}"].iloc[-2]) or smoothing_short_flag):
                return "SHORT_SIGNAL"
        if strategy_name == 'ema_crossover_3x':
            if smoothing_crossover_condition:
                if (df[f"EMA{ema1_period}"].iloc[-3] < df[f"EMA{ema2_period}"].iloc[-3]) and (df[f"EMA{ema2_period}"].iloc[-3] < df[f"EMA{ema3_period}"].iloc[-3]):
                    smoothing_long_flag = True
                elif (df[f"EMA{ema1_period}"].iloc[-3] > df[f"EMA{ema2_period}"].iloc[-3]) and (df[f"EMA{ema2_period}"].iloc[-3] > df[f"EMA{ema3_period}"].iloc[-3]):
                    smoothing_short_flag = True

            if ((df[f"EMA{ema1_period}"].iloc[-1] > df[f"EMA{ema2_period}"].iloc[-1]) and (df[f"EMA{ema2_period}"].iloc[-1] > df[f"EMA{ema3_period}"].iloc[-1])) and (((df[f"EMA{ema1_period}"].iloc[-2] < df[f"EMA{ema2_period}"].iloc[-2]) and (df[f"EMA{ema2_period}"].iloc[-2] < df[f"EMA{ema3_period}"].iloc[-2])) or smoothing_long_flag):            
                return "LONG_SIGNAL"
            elif ((df[f"EMA{ema1_period}"].iloc[-1] < df[f"EMA{ema2_period}"].iloc[-1]) and (df[f"EMA{ema2_period}"].iloc[-1] < df[f"EMA{ema3_period}"].iloc[-1])) and (((df[f"EMA{ema1_period}"].iloc[-2] > df[f"EMA{ema2_period}"].iloc[-2]) and (df[f"EMA{ema2_period}"].iloc[-2] > df[f"EMA{ema3_period}"].iloc[-2])) or smoothing_short_flag): 
                return "SHORT_SIGNAL"
        return