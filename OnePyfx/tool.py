import pandas as pd
import os,sys
import tushare as ts


def tushare_clean(csv_path, override=True, pickle_name=None):
    """
    1. save to local csv
    2. save to local pickle
    """
    def clean(df):
        df.reset_index(drop=True, inplace=True)
        df['date'] = pd.DatetimeIndex(df['date'])
        df.set_index('date', inplace=True)
        return df

    walk_list = os.walk(csv_path).next()
    csv_list=[]
    pickle_dict ={}

    for i in walk_list[2]:
        if 'csv' in i:
            df = pd.read_csv(os.path.join(csv_path, '%s' % i),
                                            parse_dates=True,index_col=0)
            cleaned_df = clean(df)

            # override CSV
            if override:
                cleaned_df.to_csv(os.path.join(csv_path, '%s' % i))

            # create pickle
            if type(pickle_name) is str:
                symbol = i.replace('.csv','')
                pickle_dict[symbol] = cleaned_df

    # Save to pickle
    if type(pickle_name) is str:
        pd.to_pickle(pickle_dict, os.path.join(csv_path, '%s.pkl' % pickle_name))

def tushare_online(code, start='', end='', ktype='D', autype='qfq',
                   index=False, retry_count=3, pause=0.001):
    df = ts.get_k_data(code, start, end, ktype, autype,
                       index, retry_count, pause)

    df.reset_index(drop=True, inplace=True)
    df['date'] = pd.DatetimeIndex(df['date'])
    df.set_index('date', inplace=True)
    return df
