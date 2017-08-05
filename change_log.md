Onepy  
===========

##### 2017.8.5
  - version 1.2.1
  - fix trailingstop
  - fix the computation of avg_price, unre_profit

##### 2017.8.4
  - version 1.1.1
  - fix update_timeindex
  - fix commission bug
  - fix trailstoploss bug
  - change name: limit --> takeprofit， stop --> stoploss
  - fix the position of check_pending_order function
  - fix drawdown

##### 2017.8.1
  - version 1.00.1
  - del utils folder, which copied from backtrader
  - make code more clear
  - change csv.reader to csv.Dictreader in feed
  - fix tlog, before lots of trades with 0 zip are confusing
  - fix computation of tlog bug, before cum_total in tlog is wrong
  - fix bug in strategy.py: when Exitall and other orders
     appeared at the same time, executions
    are confusing, now if Exitall exit, only execute Exitall


##### 2017.7.28
  - version:0.99.1
  - Abandon Python2.x, all code are upgraded to Python3
  - fix feed indexing.
  - fix drawdown computation

##### 2017.7.27
  - version:0.81.1
  - All code are converted to support Python3.6!
  - fix commission computation bug
  - fix limit&stop bug

##### 2017.7.24
  - version: 0.80.1
  - add get_analysis func
  - fix tlog


##### 2017.7.23
  - version: 0.70.1
  - add stock mode
  - fix update_info bug: should update info first
  - add new plot : plotly engine
  - add futures mode
  - clean code of plotter
  - add Futures feed
  - add trade_log
  - clean code of strategy

##### 2017.7.22
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

##### 2017.7.21
  - version: 0.60.1
  - add indicator module
  - add SimpleMovingAverage indicator
  - add pip install

##### 2017.7.20
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

##### 2017.7.19
  - version: 0.21
  - fixed a Huge Bug: add update_timeindex function
  - fixed the cumpute method of Fill
  - add set_pricetype function
  - fix fill logic
  - add pips and pct method for buy&sell

##### 2017.7.17
  - version: 0.2
  - add limit, stop, 挂单
  - add notify
  - add Exitall


##### 2017.7.16
  - version: 0.1
  - Finally can run!!!!!!!!!!
  - add Buy and Sell
  - Most of modules are completed


##### 2017.7.14
  - version: 0.01
  - add feed module
  - add OnePy--the Main Event Loop

##### 2017.7.11
  - version: 0.00000001
  - add to_MongoDB tool
