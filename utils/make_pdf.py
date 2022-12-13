from decimal import Decimal
from pathlib import Path

from borb.pdf import (PDF, Alignment, Document, Page, PageLayout, Paragraph,
                      SingleColumnLayout)
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.layout.image.barcode import Barcode, BarcodeType
from borb.pdf.canvas.layout.layout_element import LayoutElement
from borb.pdf.canvas.layout.table.fixed_column_width_table import \
    FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell

TABLE_HEADERS = [
    '№ п/п',
    'Сотрудник',
    'Входной тест',
    'Результат',
    'Выходной тест',
    'Результат'
]


def report_department_pdf(year, quarter, department, results_set):
    # create Document
    doc = Document()
    page = Page()
    doc.add_page(page)

    # set a PageLayout
    layout: PageLayout = SingleColumnLayout(
        page,
        vertical_margin=Decimal(40)
    )

    # используемые шрифты
    font_path = Path('static/fonts')
    regular_font = TrueTypeFont.true_type_font_from_file(
        font_path / 'Inter-Regular.ttf'
    )
    # thin_font = TrueTypeFont.true_type_font_from_file(
    #     font_path / 'Inter-Thin.ttf'
    # )
    semibold_font = TrueTypeFont.true_type_font_from_file(
        font_path / 'Inter-SemiBold.ttf'
    )
    # italic_font = TrueTypeFont.true_type_font_from_file(
    #     font_path / 'Inter-Italic.ttf'
    # )
    # заголовок страницы
    layout.add(
        Paragraph(
            text=('Отчёт о тестировании знаний персонала '
                  f'{department} за {quarter} квартал {year} года'),
            font=regular_font,
            font_size=Decimal(14),
            text_alignment=Alignment.CENTERED,
            margin_right=Decimal(30),
            margin_left=Decimal(50),
        )
    )
    table = Table(
        number_of_rows=len(results_set)+1,
        number_of_columns=6,
        margin_top=Decimal(20),
        column_widths=[
            Decimal(0.7),
            Decimal(3),
            Decimal(2),
            Decimal(1.7),
            Decimal(2),
            Decimal(1.7),
        ],
    )
    for header in TABLE_HEADERS:
        table.add(
            TableCell(
                Paragraph(
                    header,
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=semibold_font,
                ),
            ),
        )
    for num, res in enumerate(results_set):
        table.add(
            TableCell(
                Paragraph(
                    str(num+1),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )
        table.add(
            TableCell(
                Paragraph(
                    res.get('user'),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )
        table.add(
            TableCell(
                Paragraph(
                    res.get('date_input'),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )
        table.add(
            TableCell(
                Paragraph(
                    str(res.get('grade_input')),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )
        table.add(
            TableCell(
                Paragraph(
                    res.get('date_output'),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )
        table.add(
            TableCell(
                Paragraph(
                    str(res.get('grade_output')),
                    horizontal_alignment=Alignment.CENTERED,
                    text_alignment=Alignment.CENTERED,
                    font=regular_font,
                ),
                padding_top=Decimal(10),
            ),
        )

    table.no_borders()
    layout.add(table)
    # Код для создания QR-кода LayoutElement
    qr_code: LayoutElement = Barcode(
        data='https://t.me/quiz_blpu_bot',
        width=Decimal(64),
        height=Decimal(64),
        type=BarcodeType.QR,
        vertical_alignment=Alignment.BOTTOM,
        horizontal_alignment=Alignment.RIGHT
    )
    layout.add(qr_code)

    # сохранение документа
    f_path = (
        f'static/reports/Отчёт ТУ {department} ({quarter} кв. {year}г).pdf'
    )
    with open(f_path, 'wb') as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)
