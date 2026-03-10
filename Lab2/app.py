from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('planets'))


# ─────────────────────────────────────────────
# Завдання 1. Сторінка планет Сонячної системи
# GET /planets
# ─────────────────────────────────────────────
PLANETS = [
    {"name": "Mercury",  "moons": 0,   "description": "Smallest planet; closest to the Sun with extreme temperatures."},
    {"name": "Venus",    "moons": 0,   "description": "Hottest planet; covered by thick clouds of sulfuric acid."},
    {"name": "Earth",    "moons": 1,   "description": "Our home; the only known planet to harbour life."},
    {"name": "Mars",     "moons": 2,   "description": "The Red Planet; has the tallest volcano in the Solar System."},
    {"name": "Jupiter",  "moons": 95,  "description": "Largest planet; Great Red Spot is a storm older than 350 years."},
    {"name": "Saturn",   "moons": 146, "description": "Famous for its stunning ring system made of ice and rock."},
    {"name": "Uranus",   "moons": 27,  "description": "Rotates on its side; has faint rings and an icy composition."},
    {"name": "Neptune",  "moons": 16,  "description": "Windiest planet; winds can reach over 2 000 km/h."},
]

@app.route('/planets')
def planets():
    return render_template('planets.html', planets=PLANETS)


# ─────────────────────────────────────────────
# Завдання 2. Філософські цитати
# GET /quotes
# ─────────────────────────────────────────────
QUOTES = {
    "Сократ":      "Я знаю, що нічого не знаю.",
    "Платон":      "Необізнаність — це не нестача знань, а відмова від їх пошуку.",
    "Арістотель":  "Ми — те, що ми постійно робимо. Досконалість — це не вчинок, а звичка.",
    "Марк Аврелій":"Якщо щось тебе не вбиває, воно робить тебе сильнішим.",
    "Епіктет":     "Не вимагай, щоб події відповідали твоїм бажанням. Бажай, щоб події розгорталися так, як вони є.",
}

@app.route('/quotes')
def quotes():
    return render_template('quotes.html', quotes=QUOTES)


# ─────────────────────────────────────────────
# Завдання 3. Форма для улюбленого небесного тіла
# GET /favorite_celestial  → показує форму
# POST /favorite_celestial → обробляє відповідь
# ─────────────────────────────────────────────
@app.route('/favorite_celestial', methods=['GET', 'POST'])
def favorite_celestial():
    result = None
    error = False

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            result = "Please enter a celestial body."
            error = True
        else:
            result = f"Your favorite celestial body is {name}!"

    return render_template('favorite_celestial.html', result=result, error=error)


# ─────────────────────────────────────────────
# Завдання 4. Рейтинг відкриттів астрономії
# GET /discoveries
# ─────────────────────────────────────────────
DISCOVERIES = [
    {"name": "Геліоцентрична модель (Коперник)",   "year": 1543},
    {"name": "Закони Кеплера про рух планет",       "year": 1609},
    {"name": "Відкриття Галілеєм місяців Юпітера",  "year": 1610},
    {"name": "Відкриття Сатурна (Гюйгенс)",         "year": 1655},
    {"name": "Закон всесвітнього тяжіння (Ньютон)", "year": 1687},
    {"name": "Відкриття Урана (Гершель)",           "year": 1781},
    {"name": "Відкриття Нептуна",                   "year": 1846},
    {"name": "Відкриття Плутона",                   "year": 1930},
    {"name": "Перша людина в космосі (Гагарін)",    "year": 1961},
    {"name": "Посадка на Місяць (Аполлон-11)",      "year": 1969},
    {"name": "Перше фото чорної діри (M87*)",       "year": 2019},
]

@app.route('/discoveries')
def discoveries():
    return render_template('discoveries.html', discoveries=DISCOVERIES)


# ─────────────────────────────────────────────
# Завдання 5. Форма з вибором філософської школи
# GET /philosophy_quiz  → показує форму
# POST /philosophy_quiz → обробляє відповідь
# ─────────────────────────────────────────────
@app.route('/philosophy_quiz', methods=['GET', 'POST'])
def philosophy_quiz():
    result = None
    error = False

    if request.method == 'POST':
        school = request.form.get('school', '').strip()
        if not school:
            result = "Please select a school."
            error = True
        else:
            result = f"You chose {school}. Learn more about its main ideas!"

    return render_template('philosophy_quiz.html', result=result, error=error)


# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)