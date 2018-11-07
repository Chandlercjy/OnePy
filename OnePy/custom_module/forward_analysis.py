import logging
import multiprocessing
import os
import time

import arrow

import OnePy as op
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.awesome_func import run_multiprocessing
from OnePy.utils.easy_func import get_day_ratio


class ForwardAnalysis(OnePyEnvBase):

    def __init__(self):
        self.workers = os.cpu_count()
        self.total_iter_times = None
        self.show_summary = False

    def run(self, fromdate: str, length_month: int=3, rolling_month: int=3,
            times: int=2, show_summary=True, warning: bool=True):
        """
        fromdate: 起始日期
        length_month: 每次回测长度
        rolling_month: 每次向前长度
        times: 滚动回测次数
        """
        self.show_summary = show_summary

        if not warning:
            logging.basicConfig(level=logging.CRITICAL)
        first_todate = arrow.get(fromdate).shift(
            months=length_month).format("YYYY-MM-DD")
        self.total_iter_times = times

        last_todate = arrow.get(first_todate).shift(
            months=(times-1)*rolling_month).format("YYYY-MM-DD")
        print(f'Begin Forward Analysis!\n+{"-"*40}+',
              f'\nFromdate: {fromdate}, Todate: {last_todate}'
              f'\nTimescale: {length_month} Months.'
              f'\nRollingscale: {rolling_month} Months.'
              f'\nTotal roll {times} times.\n+{"-"*40}+')

        cache_list: list = multiprocessing.Manager().list()
        params = [(fromdate, first_todate, cache_list, index*rolling_month)
                  for index in range(times)]
        run_multiprocessing(self._analysis_func, params, self.workers)
        print('Done!')

    def _analysis_func(self, fromdate, todate, cache, index):
        t1 = time.time()
        go = op.OnePiece()

        fromdate = arrow.get(fromdate).shift(
            months=index).format("YYYY-MM-DD")
        todate = arrow.get(todate).shift(
            months=index).format("YYYY-MM-DD")
        go.env.fromdate = fromdate
        ratio = get_day_ratio(go.env.sys_frequency)
        go.env.sys_date = arrow.get(fromdate).shift(
            days=-ratio).format('YYYY-MM-DD HH:mm:ss')
        go.env.todate = todate

        go.sunny(self.show_summary)
        summary = 1
        cache.append(summary)
        t2 = time.time()
        self._compute_running_time(t1, t2, len(cache))

    def _compute_running_time(self, start: float, end: float, finished_times: int):
        diff = end - start
        left = diff*(self.total_iter_times-finished_times)/60/self.workers

        print(f'当前是第 {finished_times} 次, 剩余 {left:.2f} mins')
