# import math

# r = 1350
# l = 8600
# level = 1940
# full_s = math.pi * math.pow(r, 2)

# # определение стороны
# a = 2 * math.sqrt(math.pow(r, 2) - math.pow((r - level), 2))
# #  определение угла бета
# cos_alfa = a / (2 * r)
# alfa = math.acos(cos_alfa)
# beta = 180 - (2 * math.degrees(alfa))
# # определение площади сегмента
# s = (math.pow(r, 2) / 2) * (math.pi * (beta / 180) - math.sin(math.radians(beta)))
# if level > r:
#     s = full_s - s
# # определение объёма
# v = s * l / 1000000

# print(f'Сторона {a}\nУгол {beta}\nОбъём {v}')
