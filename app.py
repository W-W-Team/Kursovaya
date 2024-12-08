from flask import Flask, request, render_template_string

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

    except (ValueError, TypeError):
        return render_template_string(HTML_ERROR)

if __name__ == '__main__':
    app.run()
