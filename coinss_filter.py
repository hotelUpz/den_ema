import requests
import math
from api_binance import BINANCE_API
from log import log_exceptions_decorator

class COInN_FILTERR(BINANCE_API):
    def __init__(self) -> None:
        super().__init__()

    @log_exceptions_decorator
    def top_coins_engin(self, api_key, limit):
        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }
        params = {
            'start': '1',
            'limit': limit,
            'convert': 'USD',  
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            top_coins = data['data']
            return top_coins
        return None

    @log_exceptions_decorator
    def coin_market_cup_top(self, api_key, limit):
        top_coins_total_list = []
        top_coins = self.top_coins_engin(api_key, limit)
        if top_coins:
            for coin in top_coins:
                try:
                    top_coins_total_list.append(f"{coin['symbol']}USDT")
                except:
                    pass
            return top_coins_total_list
        return
    
    @log_exceptions_decorator   
    def get_top_coins_template(self):
        def go_filter(all_binance_tickers, coinsMarket_tickers):
            top_pairs = []            
            exclusion_contains_list = ['UP', 'DOWN', 'RUB', 'EUR']

            if all_binance_tickers:
                if not self.price_filter_flag:
                    self.MIN_FILTER_PRICE = 0
                    self.MAX_FILTER_PRICE = math.inf                   

                top_pairs = [ticker for ticker in all_binance_tickers if
                                ticker['symbol'].upper().endswith('USDT') and
                                not any(exclusion in ticker['symbol'].upper() for exclusion in exclusion_contains_list) and
                                (float(ticker['lastPrice']) >= self.MIN_FILTER_PRICE) and (
                                        float(ticker['lastPrice']) <= self.MAX_FILTER_PRICE)]
                if self.slice_volum_flag:
                    top_pairs = sorted(top_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
                    top_pairs = top_pairs[:self.SLICE_VOLUME_BINANCE_PAIRS]

                if self.min_volume_usdtFilter_flag:
                    top_pairs = [x for x in top_pairs if float(x['quoteVolume']) >= self.MIN_VOLUM_USDT]

                if self.slice_volatilyty_flag:
                    top_pairs = sorted(top_pairs, key=lambda x: abs(float(x['priceChangePercent'])), reverse=True)
                    top_pairs = top_pairs[:self.SLICE_VOLATILITY]
                if self.daily_filter_direction == 1:
                    top_pairs = [x for x in top_pairs if float(x['priceChange']) > 0]
                elif self.daily_filter_direction == -1:
                    top_pairs = [x for x in top_pairs if float(x['priceChange']) < 0]
                if self.volume_range_true:
                    top_pairs = sorted(top_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
                if self.volatility_range_true:
                    top_pairs = sorted(top_pairs, key=lambda x: abs(float(x['priceChangePercent'])), reverse=True)
                if self.in_coinMarketCup_is:
                    return [x['symbol'] for x in top_pairs if x['symbol'] not in self.black_coins_list and x['symbol'] in coinsMarket_tickers]
                return [x['symbol'] for x in top_pairs if x['symbol'] not in self.black_coins_list]
        all_binance_tickers = self.get_all_tickers()
        coinsMarket_tickers = []
        if self.in_coinMarketCup_is:
            coinsMarket_tickers = self.coin_market_cup_top(self.coinMarketCup_api_token, self.TOP_MARKET_CUP) 
        return go_filter(all_binance_tickers, coinsMarket_tickers) 