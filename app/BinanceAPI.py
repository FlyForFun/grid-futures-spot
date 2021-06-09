# author-wechat：findpanpan

import requests, time, hmac, hashlib
# from app.authorization import recv_window,api_secret,api_key
from app.authorization import recv_window,api_secret,api_key

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

class BinanceAPI(object):
    BASE_URL = "https://www.binance.com/api/v1"
    FUTURE_URL = "https://fapi.binance.com"
    BASE_URL_V3 = "https://api.binance.com/api/v3"
    PUBLIC_URL = "https://www.binance.com/exchange/public/product"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def timestamp_to_date(self, ts_minsecond):
        try:
            ts_minsecond = int(ts_minsecond)
            time_local = time.localtime(int(ts_minsecond / 1000))
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            return dt
        except Exception as e:
            print(e)

    def Bolinger_Bands(self, stock_price, window_size, num_of_std):

        rolling_mean = stock_price.rolling(window=window_size).mean()
        rolling_std = stock_price.rolling(window=window_size).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return rolling_mean, upper_band, lower_band

    def ping(self):
        path = "%s/ping" % self.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    def get_spot_ticker_data(self,market):
        path = "%s/ticker/price" % self.BASE_URL_V3
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        # time.sleep(2)
        return res

    def get_ticker_24hour(self,market):
        path = "%s/ticker/24hr" % self.BASE_URL_V3
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        return res

    def get_spot_klines(self, market, interval, startTime=None, endTime=None, limit=500):
        path = "%s/klines" % self.BASE_URL_V3
        params = None
        if startTime is None:
            params = {"symbol": market, "interval":interval, 'limit': limit}
        else:    
            params = {"symbol": market, "interval":interval, "startTime":startTime, "endTime":endTime, 'limit': limit}
        return self._get_no_sign(path, params)

    def buy_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "BUY", rate)
        return self._post(path, params)

    def sell_limit(self, market, quantity, rate):
        path = "%s/order" % self.BASE_URL_V3
        params = self._order(market, quantity, "SELL", rate)
        return self._post(path, params)

    ### --- 合约 --- ###
    def get_future_ticker_data(self,market):
        path = "%s/fapi/v1/ticker/price" % self.FUTURE_URL
        params = {"symbol":market}
        res =  self._get_no_sign(path,params)
        # time.sleep(2)
        return res

    def get_future_klines(self, market, interval, contracttype = 'PERPETUAL', startTime=None, endTime=None, limit=500):
        path = "%s/fapi/v1/continuousKlines" % self.FUTURE_URL
        params = None
        if startTime is None:
            params = {"pair": market, 'contractType': contracttype, "interval": interval, 'limit': limit}
        else:
            params = {"pair": market, 'contractType': contracttype, "interval": interval, "startTime": startTime,
                      "endTime": endTime, 'limit': limit}
        return self._get_no_sign(path, params)

    def set_leverage(self,symbol, leverage):
        
        ''' 调整开仓杠杆
            :param symbol 交易对
            :param leverage 杠杆倍数
        '''
        path = "%s/fapi/v1/leverage" % self.BASE_URL
        params = {'symbol':symbol, 'leverage': leverage}
        return self._post(path, params)
    
    def limit_future_order(self,side, market, quantity, price):
        
        ''' 合约限价单
            :param side: 做多or做空 BUY SELL
            :param market:币种类型。如：BTCUSDT、ETHUSDT
            :param quantity: 购买量
            :param price: 开仓价格
        '''
        path = "%s/fapi/v1/order/test" % self.FUTURE_URL
        params = self._order(market, quantity, side, price)
        return self._post(path, params)

    ### ----私有函数---- ###
    def _order(self, market, quantity, side, price=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(price)
            params["timeInForce"] = "GTC"
        else:
            params["type"] = "MARKET"

        params["symbol"] = market
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True,
                            proxies={'http':'http://127.0.0.1:7890','https':'http://127.0.0.1:7890'}).json()

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _post(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = self._sign(params)
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query,timeout=180, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)

if __name__ == "__main__":
    instance = BinanceAPI(api_key,api_secret)
    # print(instance.buy_limit("EOSUSDT",5,2))
    # print(instance.get_ticker_price("WINGUSDT"))
    print(instance.limit_future_order("SELL", "EOSUSDT", 2, 3))