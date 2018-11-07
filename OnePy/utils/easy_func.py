from itertools import count

import arrow

from OnePy.utils.awesome_func import dict_to_table


def check_setting(dict_data, name, check_only=False):
    if dict_data == {}:
        print('>'*10, f'Attention!! There is No {name}!!!', '<'*10)
    else:
        if not check_only:
            counter = count(1)
            dict_to_table({f'{name}_{next(counter)}': key
                                 for key in dict_data})


def format_date(date):
    return arrow.get(date).format('YYYY-MM-DD HH:mm:ss')


def get_day_ratio(frequency: str):
    """
    (S5, S10, S30, M1, M2, M4, M5) <- BAD Interval
    M10, M15, M30, H1, H2, H3, H4, H6, H8, H12
    """

    if frequency == "S5":
        return 5 / 60 / 60 / 24
    elif frequency == "S10":
        return 10 / 60 / 60 / 24
    elif frequency == "S30":
        return 30 / 60 / 60 / 24
    elif frequency == "M1":
        return 1 / 60 / 24
    elif frequency == "M2":
        return 2 / 60 / 24
    elif frequency == "M4":
        return 4 / 60 / 24
    elif frequency == "M5":
        return 5 / 60 / 24
    elif frequency == "M10":
        return 10 / 60 / 24
    elif frequency == "M15":
        return 15 / 60 / 24
    elif frequency == "M30":
        return 30 / 60 / 24
    elif frequency == "H1":
        return 1 / 24
    elif frequency == "H2":
        return 2 / 24
    elif frequency == "H3":
        return 3 / 24
    elif frequency == "H4":
        return 4 / 24
    elif frequency == "H8":
        return 8 / 24
    elif frequency == "H12":
        return 12 / 24
    elif frequency == "D":
        return 1


