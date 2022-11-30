from decimal import Decimal
from pathlib import Path

from borb.pdf import (PDF, Alignment, Document, Page, PageLayout, Paragraph,
                      SingleColumnLayout)
from borb.pdf.canvas.color.color import HexColor
# not an easy import
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell


TABLE_HEADERS = [
    '№ п/п',
    'Сотрудник',
    'Входной тест',
    'Результат',
    'Выходной тест',
    'Результат'
]


def main():
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
    thin_font = TrueTypeFont.true_type_font_from_file(
        font_path / 'Inter-Thin.ttf'
    )
    semibold_font = TrueTypeFont.true_type_font_from_file(
        font_path / 'Inter-SemiBold.ttf'
    )
    italic_font = TrueTypeFont.true_type_font_from_file(
        font_path / 'Inter-Italic.ttf'
    )

    # заголовок страницы
    layout.add(
        Paragraph(
            'Отчёт о тестировании знаний персонала КС-5,6 за 1 квартал 2022 года',
            font=regular_font,
            font_size=Decimal(14),
            text_alignment=Alignment.CENTERED,
            margin_right=Decimal(30),
            margin_left=Decimal(50),
        )
    )

    table = Table(
        number_of_rows=5,
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
    # сделать цикл с данными результатов тестирования

    table.no_borders()
    layout.add(table)

    # сохранение документа
    with open('output.pdf', 'wb') as pdf_file_handle:
        PDF.dumps(pdf_file_handle, doc)


if __name__ == '__main__':
    main()
