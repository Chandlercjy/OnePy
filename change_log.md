Onepy  
===========

##### 2018.04.05
- 继续修复撮合引擎
- 新增MongoDB reader和saver
- 调整目录层级

##### 2018.04.04
- 撮合引擎写错，换个思路重写撮合引擎

##### 2018.04.03
- 添加撮合引擎，修复各种bug，详情见commits

##### 2018.04.02
- 添加todate日期过滤读取数据
- 添加barseries，添加plotly画图
- 添加output模块，可以输出结果

##### 2018.04.01
- 添加fromdate日期过滤读取数据

##### 2018.03.31
- 重构stock\_recorder基本完成，新增简易画图 

##### 2018.03.30
- 修复一些bug
- 新增stockrecorder和record\_series模块

##### 2018.03.29
- 添加OrderChecker模块，用于检查挂单是否被触发

##### 2018.03.28
- 完成Order部分逻辑封装，特别是trailing订单部分

##### 2018.03.27
- 使Order逻辑部分更加清晰
- 分离模块读取到config，便与扩展

##### 2018.03.26
- 添加Signal模块

##### 2018.03.25
- 初步完成Order部分逻辑判断

##### 2018.03.24
- 初步完成事件循环。

##### 2018.03.21
- 参照Rqalpha，初次重构

##### 2017.11.01
- version 1.54.1
- repair oandafill, oandabroker


##### 2017.10.30
- version 1.53.1
- add logger module, standardize the output of log
- change set_notify to set_logger

##### 2017.09.05
- version 1.52.1
- add bar class, combine all feed

##### 2017.09.04
- verison 1.51.1
- add more doc
- add abstractmethod to Base module

##### 2017.09.03
- version 1.50.1
- fit code to PEP8
- reconstruct code

##### 2017.08.31
- version 1.22.1
- fix copy_last bug in dataseries
- fix pip computation in Forex.

##### 2017.08.16
- version 1.21.1
- add dataseries and appiled it to others！！！
- clear code
  

##### 2017.08.13
- version 1.20.1
- rebuild Order class and appiled it to others！！！


##### 2017.08.11
- version 1.14.1
- add order module
- clear code
- add more OO logic


##### 2017.08.10
- version 1.13.1
- add order class
- fix json error in oanda api

##### 2017.08.09
- version 1.12.1
- improve oanda api
- strategy: improve Exitall function


##### 2017.08.08
- version 1.11.1
- fix tlog

##### 2017.08.07
- version 1.10.1
- add LiveFillEvent
- add OandaBroker

##### 2017.08.06
- version 1.9.1
- fix commission computation
- add commission plot
- clear code of indicator
- add tushare api to MongoEB

##### 2017.08.05
- version 1.8.1
- fix fill bug

##### 2017.08.04
- version 1.07.1
- Optimize oanda api
- fix commission bug
- fix trailstoploss bug
- change name: limit --> takeprofit， stop --> stoploss
- fix the position of check_pending_order function

##### 2017.08.03
- version 1.6.1
- Optimize Multi_Oanda_Candles_to_MongoDB function
- fix update_timeindex
- Optimize oanda api


##### 2017.08.02
- verison 1.5.1
- add Oanda live Feed


##### 2017.08.01
- verison 1.4.1
- add oanda_ohlc to Mongodb
- fix fill bug
- add Mongodb_Feed
- add buffer for MongoDB_Feed

##### 2017.07.31
- version 1.3.1
- del utils folder, which copied from backtrader
- make code more clear
- change csv.reader to csv.Dictreader in feed
- fix bug in strategy.py: when Exitall and other orders
     appeared at the same time, executions are confusing,
     now if Exitall exit, only execute Exitall
- add oanda api

##### 2017.07.30
- version: 1.2.1
- fix computation of tlog bug, before cum_total in tlog is wrong
- fix tlog, before lots of trades with 0 zip are confusing

##### 2017.07.29
- version: 1.1.1
- clear feed, use csv.Dictreader instead of csv.reader
- del with_metaclass, which copied from backtrader

##### 2017.07.29
- version: 1.00.1
- fix exitall, prevent exit too much

##### 2017.07.28
- version:0.99.1
- Abandon Python2.x, all code are upgraded to Python3
- fix feed indexing.
- fix drawdown computation

##### 2017.07.27
- version:0.81.1
- All code are converted to support Python3.6!
- fix commission computation bug
- fix limit&stop bug

##### 2017.07.24
- version: 0.80.1
- add get_analysis func
- fix tlog


##### 2017.07.23
- version: 0.70.1
- add stock mode
- fix update_info bug: should update info first
- add new plot : plotly engine
- add futures mode
- clean code of plotter
- add Futures feed
- add trade_log
- clean code of strategy

##### 2017.07.22
- version: 0.61.1
- fix indicator bugs
- fix limit and stop bug! A Huge One.
- add more detail output_summary
	- Final_value
	- Total_return
	- Max_Drawdown
	- Duration
	- Sharpe_Ratio
- add a new tool: dict_to_table

##### 2017.07.21
- version: 0.60.1
- add indicator module
- add SimpleMovingAverage indicator
- add pip install

##### 2017.07.20
- version: 0.30
- add trailingstop
- all '==' changed to 'is' to speed up
- fix bug： check whether cash is enough
- fix HUGE Bug： the compution of profit (takes me lots of time)
  - unrealized_profit
  - realized_profit
- add commission
- fix Exitall Bug
- add very easy plot module

##### 2017.07.19
- version: 0.21
- fixed a Huge Bug: add update_timeindex function
- fixed the cumpute method of Fill
- add set_pricetype function
- fix fill logic
- add pips and pct method for buy&sell

##### 2017.07.17
- version: 0.2
- add limit, stop, 挂单
- add notify
- add Exitall


##### 2017.07.16
- version: 0.1
- Finally can run!!!!!!!!!!
- add Buy and Sell
- Most of modules are completed


##### 2017.07.14
- version: 0.01
- add feed module
- add OnePy--the Main Event Loop

##### 2017.07.11
- version: 0.00000001
- add to_MongoDB tool
