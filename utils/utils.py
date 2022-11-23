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


def word_conjugate(number, words):
    int_num = int(number)
    last_digit = int_num % 10
    last_two_digit = int_num % 100  # для проверки 11...14
    if last_digit == 1 and last_two_digit != 11:
        return f'{words[0]}'  # заявка
    if 1 < last_digit < 5 and last_two_digit not in range(11, 15):
        return f'{words[1]}'  # заявки
    return f'{words[2]}'  # заявок
