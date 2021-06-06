# -*- coding: utf-8 -*-
from app.BinanceAPI import BinanceAPI
from app.authorization import api_key, api_secret
from data.runBetData import RunBetData
from app.dingding import Message
import time

binan = BinanceAPI(api_key, api_secret)
runbet = RunBetData()
msg = Message()

# time_start = time.time()
# spot_data = binan.get_spot_ticker_data('ETHUSDT')
# future_data = binan.get_future_ticker_data('ETHUSDT')
# time_end = time.time()
# print('spot: ' + str(spot_data))
# print('future: ' + str(future_data))
# print('Server time: %s' % binan.timestamp_to_date(future_data['time']))
# print('time cost', time_end - time_start, 's')

kline_1m_data = binan.get_klines('ETHUSDT', '1m', limit=10)
#%%

# tmp = binan.get_klines('ETHUSDT', 1, startTime=None, endTime=None)
# time_cost = 0
# num = 10
# for i in range(0, num):
#     time_start = time.time()
#     cur_market_price = binan.get_ticker_price('ETHUSDT')
#     time_end = time.time()
#     print(cur_market_price)
#     time_cost = time_cost+(time_end-time_start)/num
#     # time.sleep(1)
# print('time cost', time_cost, 's')
