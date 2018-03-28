from OnePy.base_reader import CSVReader
from OnePy.sys_model.bars import Bar
from OnePy.utils.awesome_func import run_fuction


def test_csv_reader():
    csv_reader = CSVReader('../data/000001.csv', '000001')
    data = csv_reader.load()
    print(next(data))
    print(csv_reader.env.reader_dict)


def test_ohlc_type():
    csv_reader = CSVReader('../data/000001.csv', '000001')
    bar = Bar(csv_reader)
    bar.next()

    assert isinstance(bar.open, float)
    assert isinstance(bar.high, float)
    assert isinstance(bar.low, float)
    assert isinstance(bar.close, float)
    assert isinstance(bar.volume, float)


# TODO: marketorder的执行价格和pending order计算pct使用的executeprice一样

if __name__ == "__main__":
    run_fuction(test_csv_reader, test_ohlc_type)
