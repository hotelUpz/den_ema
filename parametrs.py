# import os
# from dotenv import load_dotenv
import math
from HIDDEN.config import *

is_tg_interface_true = 0 # использовать интерфейс тг, Вкл/выкл: 1/0

class PARAMS():
    def __init__(self) -> None:
        self.SOLI_DEO_GLORIA = 'Soli Deo Gloria!' # одному Богу слава!!
        # //////////////////////////////////// must have params:        
        # крипто пара:
        # self.symbol = 'BTCUSDT' 
        # self.symbol = 'ARBUSDT' 
        # self.symbol = 'BNBUSDT'
        # self.symbol = 'NEARUSDT'
        # self.symbol = '1000PEPEUSDT'
        self.symbol = 'DOGEUSDT'
        self.start_depo = 10 # начальное значение депо которое сбрасфывается после тог как текущий self.cur_martin_gale_multiplier достигнет максимального self.max_martin_gale_multiplier (см. настройки мартингейла)
        self.depo = 10 # депозит в USDT
        self.lev_size = 1 # размер кредитного плеча
        self.was_change_leverage_true = False
        self.margin_type = 'ISOLATED' # CROSS (изолированная маржа или кросс маржа. Изолированная по дефолту) 
        # ////////////////////
        self.default_tg_vars() 
        self.init_all_params()

    def init_all_params(self):
        # ///////////// интрадакшн ///////////////////////////////////
        self.my_name = 'Denis' # ваше имя
        self.market_place = 'binance' # ...
        self.market_type = 'futures' # ...
        # /////////////////////////////////////////
        # self.in_position = 0
        # //////////урлы api бинанс: ///////////////////////
        self.create_order_url = 'https://fapi.binance.com/fapi/v1/order'
        self.exchangeInfo_url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
        self.klines_url = 'https://fapi.binance.com/fapi/v1/klines' 
        self.set_margin_type_url = 'https://fapi.binance.com/fapi/v1/marginType'
        self.set_leverage_url = 'https://fapi.binance.com/fapi/v1/leverage'
        self.positions_url = 'https://fapi.binance.com/fapi/v2/positionRisk'
        self.all_tikers_url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        self.get_all_orders_url = 'https://fapi.binance.com/fapi/v1/allOrders'
        self.cancel_all_orders_url = 'https://fapi.binance.com/fapi/v1/allOpenOrders'
        # self.current_price_url = "https://fapi.binance.com/fapi/v1/ticker/price"
        # self.get_all_open_orders_url = 'https://fapi.binance.com/fapi/v1/openOrders'
        # self.account_url = 'https://fapi.binance.com/fapi/v2/account'
        # ////////////////////// некоторые переменные /////////////////////////////////////////
        self.cur_klines_data = None
        self.direction = None    
        #///////////////////////////////////////////////
        self.filter_settings()
        self.stop_loss_settings()
        self.ema_settings()
        self.default_statistic_vars()
        self.martin_gale_settings()
        self.init_keys()

    def filter_settings(self):
        self.switch_coins_filter = 1 # для работы чисто с коробки
        self.black_coins_list = ['shitok1', 'shitok2'] # монеты исключени. Например ['shitokusdt', 'shitok2usdt']
        self.price_filter_flag = 0 # фильтр по цене. Сейчас отключен. Включить/выкл: - 1/0
        self.MIN_FILTER_PRICE = 0 # минимальный порог цены. Актуально если self.price_filter_flag = 1
        self.MAX_FILTER_PRICE = math.inf # максимальный порог цены 
        self.daily_filter_direction = 0 # 0 -- пас. 1 -- искать только которые показывают растущую динамику (зеленые графики). -1 --- для падающих (красные графики) на бинанс
        self.slice_volum_flag = 1 # флаг фильтра по объему
        self.slice_volatilyty_flag = 1 # находить самые волатильные на бинанс
        self.SLICE_VOLATILITY = 40
        self.min_volume_usdtFilter_flag = 0 # искать по минимальному объему торгов за сутки на бинанс. 0 -- неактивный, 1 - активный
        self.MIN_VOLUM_USDT = 10000000 # размер минимального обьема в usdt
        self.SLICE_VOLUME_BINANCE_PAIRS = 60 # срез монет по объему торгов на бинанс
        self.volume_range_true = 0 # ранжировать по объему. Включить/выкл: - 1/0
        self.volatility_range_true = 1 # ранжировать по волатильности. Включить/выкл: - 1/0
        self.in_coinMarketCup_is = 1 # показывать только те монеты которые есть в топе Coin Market Cup. Включить/выкл: - 1/0
        self.TOP_MARKET_CUP = 30 # срез монет. по коин маркет кап это будет первая двадцатка

    def stop_loss_settings(self):
        # /////////////////////////////////////////////////////
        self.stop_loss_global_type = 'TRAILLING_GLOBAL_TYPE' # треллинг стоп лосс 
        # self.stop_loss_global_type = 'FIXED_GLOBAL_TYPE' # фиксированные стоп лосс и тейк профит
        # ниже параметры для расчета stop_loss_ratio (stop_loss_ratio = abs(точка входа - точка стоп лосса)/ точка входа):
        self.ricks_earnings_ratio = '1:3' # соотношение риска к прибыли. только для 'FIXED_GLOBAL_TYPE'
        # //////// способы вычисления точки стоп лосса: /////////////////
        self.stop_loss_type = 'LAST_MIN' # стоп лосс по последнуму локальному минимуму или максимуму
        # self.stop_loss_type = 'ABSOLUTE_MIN' # стоп лосс по минимуму или максимуму за определенный период. Берется период равный длине наибольшего периода ema
        # self.stop_loss_type = 'ATR_VAL' # стоп лосс по волатильности умноженный на 1.6
        # self.stop_loss_type = 'FIXED' # фиксированный стоп. Может быть как в 'TRAILLING_GLOBAL_TYPE' так и в 'FIXED_GLOBAL_TYPE'
        self.default_stop_loss_ratio_val = 0.01 # дефолтное значение stop_loss_ratio для self.stop_loss_type = 'FIXED' или в результате аномалий при вычислении stop_loss_ratio
        # /////////////////////////////////////////////////////

    def ema_settings(self):
        self.kline_time, self.time_frame = 5, 'm' # таймфрейм где челое число - период, а буква - сам тайм фрейм (минута, час и т.д)
        self.interval = str(self.kline_time) + self.time_frame # то же только на китайский мови...
        self.strategy_name = 'ema_crossover_2x' # стратегия прересечения двух ema
        # self.strategy_name = 'ema_crossover_3x' # стратегия прересечения трех ema
        self.ema1_period = 5 # - длина короткой волны
        self.ema2_period = 10 # - длина длинной волны (для 'ema_crossover_3x' длина средней волны)
        self.ema3_period = 100 # для 'ema_crossover_2x' установлен в None. Для 'ema_crossover_3x' обязаня быть челым числом большим чем предыдущие две волны например 25
        if self.strategy_name == 'ema_crossover_2x':
            self.ema3_period = None
        self.ema_list = [self.ema1_period, self.ema2_period, self.ema3_period] # - для тех части...
        self.max_period = max(x for x in self.ema_list if x is not None) # - для тех части...
        self.smoothing_crossover_condition = 0 # рекомендуется в 0. Некое сглаживающие условия для нахождения сигнала. Потенциально может дать больше сигналов, но худшего качества. По желанию 1

    def default_statistic_vars(self):
        self.show_statistic_hour = 21 # время показа дневной статистики (21 - в 9 часов вечера каждого дня)
        self.win_los = 0 # результат последней сделки (в плюс или в минус)
        self.daily_trade_history_list = [] # список трейдов (точки входа и точки выхода в позиции) за все время торгов
        self.total_trade_history_list = [] # список трейдов (точки входа и точки выхода в позиции) за все время торгов

    def martin_gale_settings(self):
        self.martin_gale_flag = 0 # мартин гейл отключен. Включить/выкл: - 1/0
        self.martin_gale_ratio = 2 # множитель депозита
        self.cur_martin_gale_counter = 0 # всегда равен 0
        self.max_martin_gale_level = 4 # сколько раз умножать позицию

    # /////////// переменные... - суто по тех части: ///////////////////////
    def default_tg_vars(self): 
        self.veryf_attemts_number = 9 # количество попыток доступа
        self.run_flag = 0
        self.stop_bot_flag = 0          
        self.block_acess_flag = 0
        self.start_flag = 0
        self.start_day_date = None
        self.block_acess_counter = 0
        self.seq_control_flag = 0
        self.stop_redirect_flag = 0  
        self.settings_redirect_flag = 0

    def init_keys(self): 
        # ////////////////////// инициализация ключей: ///////////////////////////////
        self.api_key = BINANCE_API_PUBLIC_KEY
        self.api_secret = BINANCE_API_PRIVATE_KEY 
        self.tg_api_token = TG_TOKEN
        self.coinMarketCup_api_token = COIN_MARKET_CUP_TOKEN
        self.seq_control_token = ACESS_TOKEN
        #////////////////////////////// для деплоя на сервер:
        # self.api_key = os.getenv(f"{self.market_place.upper()}_API_PUBLIC_KEY", "")
        # self.api_secret = os.getenv(f"{self.market_place.upper()}_API_PRIVATE_KEY", "")
        # self.tg_api_token = os.getenv("TG_TOKEN", "")
        # # print(self.tg_api_token)
        # self.coinMarketCup_api_token = os.getenv("COIN_MARKET_CUP_TOKEN", "")
        # self.seq_control_token = os.getenv("ACESS_TOKEN", "")
   
