import multiprocessing
import multiprocessing.dummy as threading
import sys
import time
from functools import wraps

from retry import retry
from six import iteritems


def run_multiprocessing(func, params: list, max_worker: int=None, join=True):
    pool = multiprocessing.Pool(max_worker)

    if not params:
        return

    if isinstance(params[0], tuple):
        pool.starmap(func, params)
    else:
        pool.map(func, params)
    pool.close()

    if join:
        pool.join()


def run_multithreading(func, params: list, max_worker: int=None, join=True):
    pool = threading.Pool(max_worker)

    if isinstance(params[0], tuple):
        pool.starmap(func, params)
    else:
        pool.map(func, params)
    pool.close()

    if join:
        pool.join()


def show_process(finished_len: int, total_len: int):
    i = int(finished_len/total_len*100)
    k = i + 1
    output = '>'*(i//2)+' '*((100-k)//2)
    sys.stdout.write('\r'+output+'[%s%%]' % (i+1))
    sys.stdout.flush()


def dict_to_table(dict_data):
    for key, value in dict_data.items():
        if not isinstance(value, str):
            dict_data[key] = str(value)

    max_key_len = max([len(i) for i in dict_data])+1
    max_value_len = max([len(i) for i in dict_data.values()])+1
    total_len = max_key_len+max_value_len+3

    print(f'+{total_len*"-"}+')

    for key, value in dict_data.items():
        print(f'|{key.ljust(max_key_len)} | {value.rjust(max_value_len)}|')
    print(f'+{total_len*"-"}+')


def run_fuction(*funcs):
    for func in funcs:
        print(20*'=', f'Function: {func.__name__}', 20*'=')
        begin = time.time()
        func()
        end = time.time()
        print(f'Finished in {end-begin:.2f}s')


def handle_error(tries=20, delay=0.01):

    def decorate(func):

        @wraps(func)
        @retry(tries=tries, delay=delay)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as error:
                print(f'Raise an error: {error}')
                print(f'Start to retry!!!!!')
                raise Exception

        return wrapper

    return decorate


if __name__ == "__main__":

    # Functions below are just for test.
    def just_sleep(index, test_list):
        i = len(test_list)
        time.sleep(0.01)
        show_process(i, 200)
        test_list.append(index)

    def test_multithreading():
        print('Start test MultiThreading')
        finished_list = multiprocessing.Manager().list()
        run_multithreading(
            just_sleep, [(i, finished_list) for i in range(200)], 2)

    def test_multiprocessing():
        print('Start test MultiProcessing')
        finished_list = multiprocessing.Manager().list()
        run_multiprocessing(
            just_sleep, [(i, finished_list) for i in range(200)], 2)

    # run_fuction(test_multithreading, test_multiprocessing)
    raw = [i for i in range(100)]
    finish = []

    for i in raw:
        time.sleep(0.1)
        finish.append(i)
        show_process(len(finish), len(raw))
