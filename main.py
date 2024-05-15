import telebot
from telebot import types 
import time
# import math
from parametrs import is_tg_interface_true
from risk_management import STATISTIC
from utils import UTILS
from risk_management import STOP_LOGIC
from log import total_log_instance, log_exceptions_decorator

class CONNECTOR_TG(STATISTIC, UTILS, STOP_LOGIC):
    def __init__(self):  
        super().__init__()  
        self.bot = telebot.TeleBot(self.tg_api_token)
        self.menu_markup = self.create_menu() 
        self.last_message = None

    def create_menu(self):
        menu_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton("START")
        button2 = types.KeyboardButton("GO")
        button3 = types.KeyboardButton("STOP")
        button4 = types.KeyboardButton("SEARCH_COINS")
        button5 = types.KeyboardButton("SETTINGS")    
        menu_markup.add(button1, button2, button3, button4, button5)        
        return menu_markup

class TG_ASSISTENT(CONNECTOR_TG):
    def __init__(self):
        super().__init__()

    def connector_func(self, message, response_message):
        retry_number = 3
        decimal = 1.1       
        for i in range(retry_number):
            try:
                self.bot.send_message(message.chat.id, response_message)                
                return message.text
            except Exception as ex:
                print(ex)

                time.sleep(1.1 + i*decimal)                   
        return None
    
class TEMPLATES(TG_ASSISTENT):
    def __init__(self):  
        super().__init__()
    
    @log_exceptions_decorator
    def make_orders_template(self, qty, market_type, target_price):
        order_answer = {}
        response_list = []        
        side = 'BUY' if self.direction == 1 else 'SELL'
        try:
            order_answer = self.make_order(self.symbol, qty, side, market_type, target_price)
            response_list.append(order_answer)
        except Exception as ex:
            print(ex)
        return response_list, self.response_order_logger(order_answer, side, market_type)
    
    @log_exceptions_decorator
    def make_tralling_sl_template(self, qty, stop_loss_ratio):
        order_answer = None
        side = 'BUY' if self.direction == -1 else 'SELL'
        callbackRate = round(stop_loss_ratio*100, 2)
        if callbackRate < 0.1:
            print("callbackRate < 0.1")
            callbackRate = 0.1 # в % для трелинг стоп лосса
        try:
            order_answer = self.tralling_stop_order(self.symbol, qty, side, callbackRate)            
        except Exception as ex:
            print(ex)
        return self.response_order_logger(order_answer, side, 'TRAILING_STOP_MARKET')
    
    @log_exceptions_decorator
    def make_sl_tp_template(self, qty, market_type_list, target_price_list):
        order_answer = None
        response_success_list = []
        side = 'BUY' if self.direction == -1 else 'SELL'
        for market_type, target_price in zip(market_type_list, target_price_list):
            try:
                order_answer = self.make_order(self.symbol, qty, side, market_type, target_price)
                response_success_list.append(self.response_order_logger(order_answer, side, market_type))
                time.sleep(0.1)
            except Exception as ex:
                print(ex)
        return all(response_success_list)
    
    @log_exceptions_decorator
    def pre_trading_info_template(self):
        symbol_info = self.get_excangeInfo() 
        self.cur_klines_data = self.get_klines(self.symbol) 
        cur_price = self.cur_klines_data['Close'].iloc[-1]
        qty, price_precession = self.usdt_to_qnt_converter(self.symbol, self.depo, symbol_info, cur_price)
        print("qty, cur_price:")
        print(f"{qty}, {price_precession}")
        if self.last_message:
            self.last_message.text = self.connector_func(self.last_message, "qty, cur_price:")
            self.last_message.text = self.connector_func(self.last_message, f"{qty}, {price_precession}") 
            
        self.from_anomal_view_to_normal([qty, cur_price]) 
        return cur_price, qty, price_precession   
    
    @log_exceptions_decorator
    def post_open_true_info_template(self, response_trading_list, qty, cur_price):
        # //////////////////////////////////////////////////////////////////
        executed_qty = float(response_trading_list[0].get('executedQty', qty))
        enter_price = float(response_trading_list[0].get('avgPrice', cur_price)) 
        # order_id = response_trading_list[0].get('orderId', None)
        print("qty, enter_price:")
        print(f"{executed_qty}, {enter_price}")
        if self.last_message:
            self.last_message.text = self.connector_func(self.last_message, "qty, enter_price:")
            self.last_message.text = self.connector_func(self.last_message, f"{executed_qty}, {enter_price}") 
            
        self.from_anomal_view_to_normal([executed_qty, enter_price])  
        return enter_price, executed_qty 
    
    @log_exceptions_decorator
    def post_trade_info_viwer(self, last_signal, last_win_los):
        post_trade_piece_message = ""
        if last_signal == 'LONG_SIGNAL':
            post_trade_piece_message = 'Лонговая' 
        elif last_signal == 'SHORT_SIGNAL':
            post_trade_piece_message = 'Шортовая' 
        print(f"{post_trade_piece_message} позиция была закрыта")
        if self.last_message:
            self.last_message.text = self.connector_func(self.last_message, f"{post_trade_piece_message} позиция была закрыта") 
                
        if last_win_los == 1:
            print(f"Последняя {post_trade_piece_message} сделка была закрыта в плюс") 
            if self.last_message: 
                self.last_message.text = self.connector_func(self.last_message, f"Последняя {post_trade_piece_message} сделка была закрыта в плюс") 
                
        elif last_win_los == -1:
            print(f"Последняя {post_trade_piece_message} сделка была закрыта в минус") 
            if self.last_message:                    
                self.last_message.text = self.connector_func(self.last_message, f"Последняя {post_trade_piece_message} сделка была закрыта в минус")    
        else:
            print(f"Bo время попытки проанализировать последнюю сделку возникли какие то трудности. Рекомундуем войти в интерфейс фьючерсной торговли вашего приложения Binance и проверить ситуацию. Скоро бот будет остановлен")
            if self.last_message:
                self.last_message.text = self.connector_func(self.last_message, f"Bo время попытки проанализировать последнюю сделку возникли какие то трудности. Рекомундуем войти в интерфейс фьючерсной торговли вашего приложения Binance и проверить ситуацию. Скоро бот будет остановлен") 
                
            return False
        return True
    
    @log_exceptions_decorator
    def response_order_logger(self, order_answer, side, market_type): 
        if order_answer is not None:  
            if order_answer['status'] == 'FILLED' or order_answer['status'] == 'NEW':
                print(f'{side} позиция {market_type} типа была открыта успешно!')
                # print(order_answer)
                if self.last_message:
                    self.last_message.text = self.connector_func(self.last_message, f'{side} позиция {market_type} типа была открыта успешно!') 
                    self.last_message.text = self.connector_func(self.last_message, str(order_answer))
                    
                return True
            elif order_answer['status'] == 'PARTIALLY_FILLED':
                print(f'{side} позиция {market_type} типа была открыта co статусом PARTIALLY_FILLED')
                # print(order_answer)
                if self.last_message:
                    self.last_message.text = self.connector_func(self.last_message, f'{side} позиция {market_type} типа была открыта co статусом PARTIALLY_FILLED') 
                    self.last_message.text = self.connector_func(self.last_message, str(order_answer))
                    
                return True
        print(f'{side} позиция {market_type} типа не была открыта...')
        # print(order_answer)
        if self.last_message: 
            self.last_message.text = self.connector_func(self.last_message, f'{side} позиция {market_type} типа не была открыта...') 
            self.last_message.text = self.connector_func(self.last_message, str(order_answer))
            
        return False
    
    @log_exceptions_decorator
    def martin_gale_regulator(self, last_win_los):
        if self.cur_martin_gale_counter == self.max_martin_gale_level:
            self.cur_martin_gale_counter = 0
            self.depo = self.start_depo
            return False
        if last_win_los == -1:                        
            self.depo = round(self.depo*self.martin_gale_ratio, 2)
            self.cur_martin_gale_counter += 1
        elif last_win_los == 1: 
            if self.cur_martin_gale_counter != 0:
                self.cur_martin_gale_counter -= 1
                self.depo = round(self.depo/self.martin_gale_ratio, 2)
        # if self.depo < self.start_depo:
        #     self.depo = self.start_depo
        return True       

class MAIN_CONTROLLER(TEMPLATES):
    def __init__(self):  
        super().__init__() 

    @log_exceptions_decorator
    def set_leverage_template(self):
        print("Устанавливаем кредитное плечо:")
        if self.last_message:
            self.last_message.text = self.connector_func(self.last_message, "Устанавливаем кредитное плечо:")
            
        set_leverage_resp = self.set_leverage(self.symbol, self.lev_size)
        print(set_leverage_resp)
        if self.last_message: 
            self.last_message.text = self.connector_func(self.last_message, str(set_leverage_resp))
            
        return True 

    @log_exceptions_decorator
    def main_func(self):
        if not is_tg_interface_true:
            print(f"Привет {self.my_name}! Да благословит вас Бог!")
            if self.switch_coins_filter:
                recomended_coins = []            
                recomended_coins = self.get_top_coins_template()
                if recomended_coins:
                    mess_resp = ""
                    print("Фильтр монет нашел следующие рекомендации:")                
                    mess_resp = '\n'.join(recomended_coins)
                    print(mess_resp)                
                else:
                    print("На данный момент нет ни одной рекомендации согласно заданным условиям фильтра")
            input_varios = input("Продолжить/сменить торговые параметры?(1/2)", )
            if input_varios.strip() == "2":
                new_trades_input_data = input("Введите торговую пару, размер ставки позиции (в usdt) и кредитное плечо. Например: btcusdt 20 2", )
                dataa = [x for x in new_trades_input_data.split(' ') if x and x.strip()]
                self.symbol = dataa[0].upper()  
                self.start_depo = self.depo = round(float(dataa[1]), 2)
                self.lev_size = int(float(dataa[2])) 
                print(f"Текущая торговая пара: {self.symbol}")
                print(f"Текущий депозит: {self.depo}")
                if self.set_leverage_template():
                    print(f"Текущее кредитное плечо: {self.lev_size}")
                    self.was_change_leverage_true = True
                else:
                    print(f"Не удалось установить кредитное плеч...")

        self.run_flag = True
        in_position = False
        create_order_success_flag = False
        last_signal = None
        last_win_los = 0
        init_order_price, oposit_order_price = 0, 0
        last_depo = 0
        is_no_signal_counter = 0
        is_no_signal_count_until = 20
        first_iter_flag = True
        is_show_statistic_true = False
        next_show_statistic_time = self.get_next_show_statistic_time()
        
        # Устанавливаем тип маржи
        marga_mess = 'Устанавливаем тип маржи'
        print(marga_mess)
        if self.last_message: 
            self.last_message.text = self.connector_func(self.last_message, marga_mess)
            
        set_margin_resp = self.set_margin_type(self.symbol, self.margin_type)
        print(set_margin_resp)
        if self.last_message: 
            self.last_message.text = self.connector_func(self.last_message, str(set_margin_resp))

        if not self.was_change_leverage_true:    
            # Устанавливаем кредитное плечо
            self.set_leverage_template()
        
        # Выводим торговые данные
        trade_data = f"Ваши торговые данные:\nМонета: {self.symbol}\nРазмер ставки: {self.depo}\nКредитное плечо: {self.lev_size}"
        print(trade_data)
        if self.last_message:
            self.last_message.text = self.connector_func(self.last_message, trade_data)
            
        # Включаем или отключаем Мартин Гейл
        martin_gale_status = "включен" if self.martin_gale_flag else "отключен"
        print(f"Мартин Гейл {martin_gale_status}")
        if self.last_message: 
            self.last_message.text = self.connector_func(self.last_message, f"Мартин Гейл {martin_gale_status}")

        while True:
            self.cur_klines_data = None
            get_signal_val = None
            if self.stop_bot_flag:
                if self.last_message: 
                    self.last_message.text = self.connector_func(self.last_message, "EMA bot остановлен!")                    
                print("EMA bot остановлен!")
                self.run_flag = False
                return
            # //////////////////////////////////////////////////////////////////////
            time_arg = 1
            if first_iter_flag:
                first_iter_flag = False
                mess_str = "Бот ищет сигнал для входа в позицию. Процесс поиска может занять неопределенное время. Хорошего вам дня!"
                print(mess_str)
                if self.last_message: 
                    self.last_message.text = self.connector_func(self.last_message, mess_str)                    
                time_arg = self.kline_time
            wait_time = self.time_calibrator(time_arg, self.time_frame)
            time.sleep(wait_time)

            try:
                if not in_position:
                    self.cur_klines_data = self.get_klines(self.symbol)
                    get_signal_val = self.get_signals(self.strategy_name, self.smoothing_crossover_condition, self.cur_klines_data, self.ema_list)
                    if get_signal_val:
                        is_no_signal_counter = 0                    
                        print(get_signal_val)
                        if self.last_message:                                
                            self.last_message.text = self.connector_func(self.last_message, get_signal_val)
                        last_signal = get_signal_val
                        qty = None
                        cur_price = None
                        price_precession = None
                        self.direction = None
                        response_trading_list = None
                        cur_price, qty, price_precession = self.pre_trading_info_template()
                        # /////////////////// create order logic//////////////////////////////
                        self.direction = 1 if get_signal_val == "LONG_SIGNAL" else -1                                      
                        response_trading_list, create_order_success_flag = self.make_orders_template(qty, 'MARKET', None)             
                    else:
                        is_no_signal_counter += 1
                        if is_no_signal_counter % is_no_signal_count_until == 0:
                            print(f"Нет сигнала на протяжение {is_no_signal_counter} минут")
                            if self.last_message:
                                self.last_message.text = self.connector_func(self.last_message, f"Нет сигнала на протяжение {is_no_signal_counter} минут")                                
                        continue 
                else:
                    if self.is_closing_position_true(self.symbol):
                        in_position = False
                        #//////////////// закрываем сотавшиеся ордера если таковые имеются:
                        cancel_all_open_orders_replay = self.cancel_all_open_orders(self.symbol)
                        print(cancel_all_open_orders_replay)
                        if is_tg_interface_true:
                            log_file = total_log_instance.get_logs()
                            if self.last_message:
                                self.bot.send_document(self.last_message.chat.id, log_file)  
                        # //////////// show statistic: ///////////////////////////////
                        last_win_los = 0
                        init_order_price, oposit_order_price = 0, 0
                        last_depo = 0
                        last_win_los, init_order_price, oposit_order_price, last_depo = self.last_statistic(self.symbol)  
                        self.daily_trade_history_list.append((last_win_los, init_order_price, oposit_order_price, last_depo))                  
                        if not self.post_trade_info_viwer(last_signal, last_win_los):
                            self.stop_bot_flag = True
                            continue                 

                        is_show_statistic_true, next_show_statistic_time = self.show_statistic_signal(next_show_statistic_time)
                        if is_show_statistic_true:
                            result_statistic_dict = ""
                            result_statistic_dict = self.statistic_calculations(self.daily_trade_history_list)
                            print(f"Показатели торгов за сутки:\n{result_statistic_dict}")
                            if self.last_message:
                                self.last_message.text = self.connector_func(self.last_message, f"Показатели торгов за сутки:\n{result_statistic_dict}")                                
                            self.daily_trade_history_list = []

                        # ////////////////// мартин гейл футкция: //////////////////////////////
                        if self.martin_gale_flag:
                            if not self.martin_gale_regulator(last_win_los):
                                print(f"Размер депозита был сброшен до начального и составляет: {self.depo}")
                                if self.last_message:
                                    self.last_message.text = self.connector_func(self.last_message, f"Размер депозита был сброшен до начального и составляет: {self.depo}")                                    
                                continue 
                            else:
                                print(f"Размер депозита был изменен и составляет: {self.depo}\n Tекущий Мартин Гейл счетчик равен {self.cur_martin_gale_counter}")
                                if self.last_message:
                                    self.last_message.text = self.connector_func(self.last_message, f"Размер депозита был изменен и составляет: {self.depo}\n Tекущий Мартин Гейл счетчик равен {self.cur_martin_gale_counter}")
                        # ///////////////////////////////////////////////////////////////                   
                    else:
                        # print("Позиция еще открыта")
                        continue
                
                if create_order_success_flag:
                    in_position = True
                    create_order_success_flag = False  
                    executed_qty = None 
                    enter_price = None 
                    stop_loss_ratio = None                   
                    # //////////////////////////////////////////////////////////////////
                    enter_price, executed_qty = self.post_open_true_info_template(response_trading_list, qty, cur_price)                     
                    # /////////////////////////////////////////////////////////////////////
                    stop_loss_ratio = self.calculate_stop_loss_ratio(self.direction, enter_price, self.cur_klines_data, self.stop_loss_type, self.default_stop_loss_ratio_val)  
                    print(f"стоп лосс коэффициент: {stop_loss_ratio}")

                    if self.stop_loss_global_type == 'TRAILLING_GLOBAL_TYPE':
                        if not self.make_tralling_sl_template(executed_qty, stop_loss_ratio):
                            print("Что-то пошло не так... закройте позицию вручную!!") 
                            if self.last_message:
                                self.last_message.text = self.connector_func(self.last_message, "Что-то пошло не так... закройте позицию вручную!!")                                                        
                            self.stop_bot_flag = True
                            continue          
                        
                    elif self.stop_loss_global_type == 'FIXED_GLOBAL_TYPE':
                        target_sl_price = None
                        target_tp_price = None
                        tp_multipliter = float(self.ricks_earnings_ratio.split(':')[1].strip())
                        target_sl_price = round((enter_price* (1 - self.direction*stop_loss_ratio)), price_precession)
                        target_tp_price = round((enter_price* (1 + self.direction*stop_loss_ratio*tp_multipliter)), price_precession)
                        if not self.make_sl_tp_template(executed_qty, ['STOP_MARKET', 'TAKE_PROFIT_MARKET'], [target_sl_price, target_tp_price]):
                            print("Что-то пошло не так... закройте позицию вручную!!") 
                            if self.last_message: 
                                self.last_message.text = self.connector_func(self.last_message, "Что-то пошло не так... закройте позицию вручную!!")  
                                
                            self.stop_bot_flag = True
                            continue
            except Exception as ex:
                print(ex)

class TG_MANAGER(MAIN_CONTROLLER):
    def __init__(self):
        super().__init__()  
        self.stop_redirect_flag = False  
        self.settings_redirect_flag = False    

    def run(self):  
        try: 
            @self.bot.message_handler(commands=['start'])
            @self.bot.message_handler(func=lambda message: message.text == 'START')
            def handle_start_input(message):
                if self.block_acess_flag:
                    response_message = "Это вам не пароль от вифи взламывать!!!"
                    message.text = self.connector_func(message, response_message)
                else:   
                    self.start_day_date = self.date_of_the_month()          
                    self.bot.send_message(message.chat.id, "Пожалуйста введите код доступа..", reply_markup=self.menu_markup)                   
                    self.start_flag = True

            @self.bot.message_handler(func=lambda message: self.start_flag)
            def handle_start_redirect(message): 
                self.start_flag = False               
                try:
                    cur_day_date = None                    
                    value_token = message.text.strip()
                    cur_day_date = self.date_of_the_month()

                    if self.start_day_date != cur_day_date:
                        self.start_day_date = cur_day_date
                        self.block_acess_flag = False 
                        self.block_acess_counter = 0

                    if value_token == self.seq_control_token and not self.block_acess_flag:
                        self.seq_control_flag = True  
                        # ////////////////////////////////////////////////////////////////////
                        try:                                                       
                            # self.bot.send_message(message.chat.id, response_message, reply_markup=self.menu_markup)
                            self.last_message = message
                            if self.run_flag:
                                message.text = self.connector_func(message, "Сперва остановите робота ..")
                            else:
                                self.init_all_params() 
                                message.text = self.connector_func(message, "Здравствуйте! Для начала работы выберите одну из опций.(Начать торговлю нажмите 'GO')")                               
                                # self.main_func()  
                        except Exception as ex:
                            print(ex) 
                        # ////////////////////////////////////////////////////////////////////                       

                    elif value_token != self.seq_control_token and not self.block_acess_flag:                               
                        self.block_acess_counter += 1
                        if self.block_acess_counter >= self.veryf_attemts_number:
                            self.block_acess_flag = True                            
                            response_message = "Попытки доступа исчерпаны. Попробуйте в другой раз"
                            message.text = self.connector_func(message, response_message)
                        else:
                            response_message = "Пожалуйста введите действителный код доступа"
                            message.text = self.connector_func(message, response_message)
                except Exception as ex:
                    print(ex)  
            # ////////////////////////////////////////////////////////////////////////////
            @self.bot.message_handler(func=lambda message: message.text == 'GO')             
            def handle_go(message):
                if self.seq_control_flag:
                    self.last_message = message                    
                    self.bot.send_message(message.chat.id, f'Да благословит вас Бог {self.my_name}!')
                    self.main_func()
                else:
                    self.bot.send_message(message.chat.id, "Нажмите START для верификации")      
            # ////////////////////////////////////////////////////////////////////////////
            @self.bot.message_handler(func=lambda message: message.text == 'STOP')             
            def handle_stop(message):
                if self.seq_control_flag:
                    self.last_message = message
                    self.bot.send_message(message.chat.id, "Остановить бота? (y/n)")
                    self.stop_redirect_flag = True
                else:
                    self.bot.send_message(message.chat.id, "Нажмите START для верификации")

            @self.bot.message_handler(func=lambda message: self.stop_redirect_flag)             
            def handle_stop_redirect(message):
                self.last_message = message
                self.stop_redirect_flag = False
                if message.text.strip().upper() == 'Y':                    
                    self.stop_bot_flag = True 
                    self.bot.send_message(message.chat.id, "Немного подождите...")                   
                else:
                    self.bot.send_message(message.chat.id, "Бот не был остановлен...") 
            # /////////////////////////////////////////////////////////////////////////////// 
            @self.bot.message_handler(func=lambda message: message.text == 'SEARCH_COINS')             
            def handle_search_coins(message):
                self.last_message = message
                candidate_symbols_list = []
                if self.seq_control_flag:
                    candidate_symbols_list = self.get_top_coins_template()
                    if candidate_symbols_list:
                        mess_resp = ""
                        pre_recomend_remark = "Фильтр монет нашел следующие рекомендации:"
                        print(pre_recomend_remark)
                        self.bot.send_message(message.chat.id, pre_recomend_remark)
                        mess_resp = '\n'.join(candidate_symbols_list)
                        print(mess_resp)
                        self.bot.send_message(message.chat.id, mess_resp)
                    else:
                        is_empty_recomend_list_str = "На данный момент нет ни одной рекомендации согласно заданным условиям фильтра"
                        print(is_empty_recomend_list_str)
                        self.bot.send_message(message.chat.id, is_empty_recomend_list_str)

                else:
                    self.bot.send_message(message.chat.id, "Нажмите START для верификации")
            # ////////////////////////////////////////////////////////////////////////////
            @self.bot.message_handler(func=lambda message: message.text == 'SETTINGS')             
            def handle_settings(message):
                self.last_message = message
                if self.seq_control_flag:
                    self.bot.send_message(message.chat.id, "Введите торговую пару, размер депозита (в usdt) и кредитное плечо. Например: btcusdt 20 2")
                    self.settings_redirect_flag = True
                else:
                    self.bot.send_message(message.chat.id, "Нажмите START для верификации")

            @self.bot.message_handler(func=lambda message: self.settings_redirect_flag)             
            def handle_settings_redirect(message):
                self.settings_redirect_flag = False
                dataa = [x for x in message.text.split(' ') if x and x.strip()]
                self.symbol = dataa[0].upper()  
                self.start_depo = self.depo = round(float(dataa[1]), 2)
                self.lev_size = int(float(dataa[2])) 
                self.bot.send_message(message.chat.id, f"Текущая торговая пара: {self.symbol}")
                self.bot.send_message(message.chat.id, f"Текущий депозит: {self.depo}")
                if self.set_leverage_template():
                    self.bot.send_message(message.chat.id, f"Текущее кредитное плечо: {self.lev_size}")
                    self.was_change_leverage_true = True
                else:
                    self.bot.send_message(message.chat.id, f"Не удалось установить кредитное плеч...") 
            # /////////////////////////////////////////////////////////////////////////////// 
            # self.bot.polling()
            self.bot.infinity_polling()
        except Exception as ex: 
            print(ex)

if __name__=="__main__":    
    if not is_tg_interface_true:
        MAIN_CONTROLLER().main_func()
    else:
        print('Пожалуйста перейдите в интерфейс вашего телеграм бота!')     
        bot = TG_MANAGER()   
        bot.run()
