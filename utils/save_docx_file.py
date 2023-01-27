from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Mm
from config.mongo_config import questions, themes


def create_docx_file(plan):
    department = plan.get('department')
    quarter = plan.get('quarter')
    year = plan.get('year')
    DOC_HEADER = (
        'Тестовое задание\n'
        'по входному и выходному контролю знаний технической учёбы\n'
        f'{department} на {quarter} квартал {year}г.'
    )
    TABLE_HEADERS = (
        '№ п/п',
        'Тема технической учёбы',
        '№ вопроса',
        'Содержание вопроса',
        'Варианты ответов',
        '',
    )
    document = Document()
    section = document.sections[0]
    # левое поле в миллиметрах
    section.left_margin = Mm(25)
    # правое поле в миллиметрах
    section.right_margin = Mm(15)
    # верхнее поле в миллиметрах
    section.top_margin = Mm(15)
    # нижнее поле в миллиметрах
    section.bottom_margin = Mm(15)

    style = document.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    header = document.add_paragraph(DOC_HEADER)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.style = document.styles['Normal']

    table = document.add_table(rows=2, cols=6, style='Table Grid')
    table_hdr = table.rows[0].cells  # заголовки таблицы
    table_num = table.rows[1].cells  # нумерация таблицы
    table.columns[0].width = Mm(10)
    table.columns[1].width = Mm(30)
    table.columns[2].width = Mm(20)
    table.columns[3].width = Mm(53)
    table.columns[4].width = Mm(7)
    table.columns[5].width = Mm(58)

    for id, cell in enumerate(table_hdr):
        cell.text = TABLE_HEADERS[id]
        table_num[id].text = str(id + 1)

    table_hdr[4].merge(table_hdr[5])

    questions_list = plan.get('questions')

    current_rows = 2  # текущее количество строк в таблице
    for num, q_id in enumerate(questions_list):
        q = questions.find_one({'_id': q_id})
        num_answers = q.get('num_answers')
        main_row = table.add_row().cells
        main_row[0].text = str(num + 1)
        main_row[1].text = themes.find_one({'code': q.get('theme')}).get('name')
        main_row[2].text = str(num + 1)
        main_row[3].text = q.get('question')
        main_row[4].text = '1'
        main_row[5].text = q.get('answers')[0]
        for i in range(1, num_answers):
            row_ans = table.add_row().cells
            row_ans[-2].text = str(i + 1)
            row_ans[-1].text = q.get('answers')[i]
        for row_id in range(current_rows, current_rows + num_answers - 1):
            for cell_id in range(0, 4):
                table.rows[row_id].cells[cell_id].merge(table.rows[row_id+1].cells[cell_id])
        current_rows += num_answers

    path = f'static/reports/Тест {department} ({quarter} кв. {year}г).docx'
    document.save(path)
