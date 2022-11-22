from math import ceil
import datetime as dt


def calc_grade(pos_ans, all_ans):
    percent = (pos_ans / all_ans) * 100
    if percent < 45:
        return 2
    elif percent < 65 and percent >= 45:
        return 3
    elif percent < 85 and percent >= 65:
        return 4
    return 5


def calc_date():
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    quarter = ceil(month/3)
    return (year, month, quarter)
