TIME_ZONE = 'Asia/Yekaterinburg'
# TIME_ZONE = 'Europe/Moscow'

HELP_TEXT = (
    'Команды для пользователей:\n'
    '/terms - Термины и определения\n'
    '/key_rules - Ключевые правила безопасности\n'
    '/vnimanie - Информационные листы ВНИМАНИЕ\n'
    '/answers - Ответы на билеты по отдельным вопросам\n'
    '/tickets - Ответы на билеты одним файлом\n'
    '/my_stats - Статистика проверки знаний\n\n'
    'Команды для администраторов:\n'
    '/unsolve_test - Пользователи, не прошедшие тестирование\n'
    '/users_stats - Просмотр статистики пользователей\n'
    '/export_tests - Экспорт тестовых вопросов в docx-файл\n'
    '/report - Экспорт квартального отчёта о прохождении тестирования в pdf-файл\n'
    '/results - Экспорт результатов тестирования в docx-файл'
)

DEPARTMENTS = [
    'КЦ-1,4',
    'КЦ-2,3',
    'КЦ-5,6',
    'КЦ-7,8',
    'КЦ-9,10',
    'МРУ ГКС',
]

TEST_TYPE = {
    'input': 'входной',
    'output': 'выходной',
    'special': 'внеплановый',
}

TU = {
    '16.01.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-16012023-01-14',
    '23.01.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-23012023-01-22',
    '30.01.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-30012023-01-22',
    '06.02.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-06022023-02-05',
    '13.02.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-13022023-02-09',
    '20.02.2023': 'https://telegra.ph/Tehnicheskaya-uchyoba-20022023-02-19',
}

EXAMEN = {
    'Машинист ТК': {
        'Билет №1': {
            'Вопрос 1': 'https://telegra.ph/Bilet-1-Vopros-1-01-17',
            'Вопрос 2': 'https://telegra.ph/Bilet-1-Vopros-2-01-17',
            'Вопрос 3': 'https://telegra.ph/Bilet-1-Vopros-3-01-17',
            'Вопрос 4': 'https://telegra.ph/Bilet-1-Vopros-4-01-17',
            'Вопрос 5': 'https://telegra.ph/Bilet-1-Vopros-5-01-17',
            # 'Вопрос 6': 'Ответ отсутствует',
            'Вопрос 7': 'https://telegra.ph/Bilet-1-Vopros-7-01-17',
            # 'Вопрос 8': 'Ответ отсутствует',
            'Вопрос 9': 'https://telegra.ph/Bilet-1-Vopros-9-01-17',
            'Вопрос 10': 'https://telegra.ph/Bilet-1-Vopros-10-01-17',
        },
    },
}
