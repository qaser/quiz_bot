import datetime as dt
from math import ceil


def calc_grade(pos_ans, all_ans) -> int:
    '''
    расчет оценки в зависимости от процента правильных ответов
    '''
    percent = (pos_ans / all_ans) * 100
    if percent < 45:
        return 2
    elif percent < 65 and percent >= 45:
        return 3
    elif percent < 85 and percent >= 65:
        return 4
    return 5


def calc_date() -> tuple:
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    quarter = ceil(month/3)
    return (year, month, quarter)


def word_conjugate(number: int, words: list) -> str:
    last_digit = number % 10
    last_two_digit = number % 100  # для проверки 11...14
    if last_digit == 1 and last_two_digit != 11:
        return f'{words[0]}'  # заявка
    if 1 < last_digit < 5 and last_two_digit not in range(11, 15):
        return f'{words[1]}'  # заявки
    return f'{words[2]}'  # заявок


def calc_test_type(month: int) -> str:
    '''
    Определение типа теста по текущему месяцу.
    Тест может быть "входной", "выходной", "внеплановый"
    '''
    if month in [1, 2, 4, 5, 7, 8, 10, 11]:
        return 'input'
    elif month in [3, 6, 9, 12]:
        return 'output'
    return 'special'
