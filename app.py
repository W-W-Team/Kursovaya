from flask import Flask, request, render_template_string, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.lib import colors

app = Flask(__name__)

# Главная страница с пометками обязательных полей
HTML_INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Калькулятор сдельной зарплаты</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f9f9f9;
            color: #000;
        }
        .container {
            text-align: center;
            padding: 20px;
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        label {
            display: block;
            margin: 10px 0 5px;
        }
        input {
            padding: 8px;
            width: 80%;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            margin-top: 15px;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background: #000;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover {
            background: #444;
        }
        .note {
            margin-top: 15px;
            font-size: 12px;
            color: #555;
        }
        .required {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Калькулятор сдельной зарплаты</h1>
        <form action="/calculate" method="post">
            <label for="units">Количество изделий<span class="required">*</span>:</label>
            <input type="number" id="units" name="units" required>
            
            <label for="rate">Оплата за единицу изделия (руб)<span class="required">*</span>:</label>
            <input type="number" id="rate" name="rate" required>
            
            <label for="deduction">Удержание (руб):</label>
            <input type="number" id="deduction" name="deduction" placeholder="0">
            
            <label for="bonus">Бонусы/премии (руб):</label>
            <input type="number" id="bonus" name="bonus" placeholder="0">
            
            <button type="submit">Рассчитать</button>
        </form>
        <p class="note"><span class="required">*</span> - обязательные поля</p>
        <p class="note">Сделано студентами группы ПИ-330Б: Хайриддинов Б.Ф., Мухамедов Д.А., Кильмухаметов Р.У.</p>
    </div>
</body>
</html>
"""

# Страница ошибки
HTML_ERROR = """
<!DOCTYPE html>
<html>
<head>
    <title>Ошибка</title>
    <style>
        body { text-align: center; padding: 50px; background: white; color: red; font-family: Arial, sans-serif; }
        a {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background: red;
            color: white;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }
        a:hover {
            background: #f44336;
        }
    </style>
</head>
<body>
    <h1>Ошибка</h1>
    <p>Некорректные значения. Попробуйте еще раз.</p>
    <a href="/">Вернуться на главную</a>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INDEX)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Получение данных из формы
        units = float(request.form['units'])  # Количество изделий
        rate = float(request.form['rate'])  # Оплата за единицу изделия
        
        # Удержания и бонусы, если не указаны - присваиваем 0
        deduction = float(request.form.get('deduction', 0) or 0)  # Если поле пустое, будет 0
        bonus = float(request.form.get('bonus', 0) or 0)  # Если поле пустое, будет 0

        # Проверка на отрицательные значения
        if units < 0 or rate < 0 or deduction < 0 or bonus < 0:
            return render_template_string(HTML_ERROR)

        # Основные расчеты
        gross_salary = units * rate  # Общая зарплата
        taxable_income = gross_salary + bonus - deduction  # Облагаемый доход
        tax = taxable_income * 0.13  # Налог 13%
        net_salary = taxable_income - tax  # Чистая зарплата

        # Генерация PDF с таблицей
        pdf_buffer = BytesIO()
        
        # Регистрация шрифта Arial
        pdfmetrics.registerFont(TTFont('Arial', 'static/fonts/arial.ttf'))
        addMapping('Arial', 0, 0, 'Arial')

        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.setFont("Arial", 12)

        c.setFont("Arial", 16)
        c.drawString(100, 800, "Итоги расчета сдельной оплаты труда")

        # Данные для таблицы
        data = [
            ["Параметр", "Значение"],
            ["Общая зарплата", f"{gross_salary:.2f} руб"],
            ["Бонусы", f"{bonus:.2f} руб"],
            ["Удержания", f"{deduction:.2f} руб"],
            ["Налоги (13%)", f"{tax:.2f} руб"],
            ["Чистая зарплата", f"{net_salary:.2f} руб"]
        ]
        
        # Позиции для таблицы
        x = 100
        y = 750
        row_height = 20
        col_width = 150

        # Рисуем заголовки таблицы
        c.setFont("Arial", 12)
        for col_num, column in enumerate(data[0]):
            c.setFillColor(colors.white)
            c.rect(x + col_num * col_width, y, col_width, row_height, fill=1)
            c.setFillColor(colors.black)
            c.drawString(x + col_num * col_width + 5, y + 5, column)

        # Рисуем строки таблицы
        c.setFont("Arial", 12)
        for row in data[1:]:
            y -= row_height
            for col_num, cell in enumerate(row):
                c.setFillColor(colors.white)
                c.rect(x + col_num * col_width, y, col_width, row_height, fill=1)
                c.setFillColor(colors.black)
                c.drawString(x + col_num * col_width + 5, y + 5, cell)

        c.save()

        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf")
    except (ValueError, TypeError):
        return render_template_string(HTML_ERROR)

if __name__ == '__main__':
    app.run()
