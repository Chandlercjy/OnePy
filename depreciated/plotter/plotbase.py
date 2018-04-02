import pandas as pd


class plotBase(object):
    def __init__(self):
        pass

    def __to_df(self, data, instrument):
        try:
            data = data[instrument]
        except:
            pass

        df = pd.DataFrame(data)[1:]
        df.set_index('date', inplace=True)
        df.index = pd.DatetimeIndex(df.index)

        return df
