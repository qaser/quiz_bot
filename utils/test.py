# from borb.pdf import Document
# from borb.pdf import Page
# from borb.pdf import SingleColumnLayout
# from borb.pdf import Paragraph
# from borb.pdf import PDF


import pymongo

# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['quiz_db']
themes = db['themes']
users = db['users']
admin_requests = db['admin_requests']
offers = db['offers']
results = db['results']
questions = db['questions']
plans = db['plans']

# import openpyxl
# from openpyxl.utils import get_column_letter

# TEXT = '123456789'

# # create an empty Document
# pdf = Document()

# # add an empty Page
# page = Page()
# pdf.add_page(page)

# # use a PageLayout (SingleColumnLayout in this case)
# layout = SingleColumnLayout(page)

# # add a Paragraph object
# layout.add(Paragraph(TEXT, font="Times-roman"))



# # store the PDF
# with open('output.pdf', "wb") as pdf_file_handle:
#     PDF.dumps(pdf_file_handle, pdf)

# THEMES = {
#     'АПК': 'apk',
#     'Агрегат ГПА-Ц-16': 'gpa-с-16',
#     'Агрегат ГТК-25И': 'gtk-25i',
#     'БПТПГ': 'bptpg',
#     'ГТД НК-16СТ': 'nk-16st',
#     'Газоопасные работы': 'gor',
#     'Земляные работы': 'zem',
#     'КИПиА': 'kip',
#     'Компрессорная станция (общая тема)': 'ks',
#     'Маслосистема КЦ': 'ms',
#     'Маслосистема НК-16СТ': 'ms_nk-16st',
#     'Маслосистема НЦ-16/76': 'ms_nc-16-76',
#     'Нагнетатель (теория)': 'pump',
#     'Нагнетатель НЦ-16/76': 'nc-16-76',
#     'Огневые работы': 'or',
#     'Охрана труда': 'ot',
#     'ПЭМГ': 'pemg',
#     'Первая помощь': 'first_aid',
#     'Промышленная безопасность': 'pb',
#     'Работы на высоте': 'vysota',
#     'СРД': 'srd',
#     'ТПА': 'tpa',
#     'Теория ГТУ (ГТД)': 'gtd'
# }

# wb = openpyxl.load_workbook('questions.xlsx')
# worksheet = wb['Темы']
# dict_len = len(THEMES)
# row = 1
# for name, code in THEMES.items():
#     worksheet['A' + str(row)].value = code
#     worksheet['B' + str(row)].value = name
#     row += 1

# wb.save('questions.xlsx')


THEMES = {
    'apk': 'АПК',
    'bptpg': 'БПТПГ',
    'first_aid': 'Первая помощь',
    'gor': 'Газоопасные работы',
    'gpa-с-16': 'Агрегат ГПА-Ц-16',
    'gtd': 'Теория ГТУ (ГТД)',
    'gtk-25i': 'Агрегат ГТК-25И',
    'kip': 'КИПиА',
    'ks': 'КС (общая тема)',
    'ms': 'Маслосистема КЦ',
    'ms_nc-16-76': 'Маслосистема НЦ-16/76',
    'ms_nk-16st': 'Маслосистема НК-16СТ',
    'nc-16-76': 'Нагнетатель НЦ-16/76',
    'nk-16st': 'ГТД НК-16СТ',
    'or': 'Огневые работы',
    'ot': 'Охрана труда',
    'pb': 'Промышленная безопасность',
    'pemg': 'ПЭМГ',
    'pump': 'Нагнетатель (теория)',
    'srd': 'СРД',
    'tpa': 'ТПА',
    'vysota': 'Работы на высоте',
    'zem': 'Земляные работы'
}
