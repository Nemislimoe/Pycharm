from flask import Flask, request

app = Flask(__name__)


# ─────────────────────────────────────────────
# Завдання 1. Таблиця множення
# GET /multiply/<n>
# ─────────────────────────────────────────────
@app.route('/multiply/<int:n>')
def multiply(n):
    lines = [f"{n} x {i} = {n * i}" for i in range(1, 11)]
    return "\n".join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# ─────────────────────────────────────────────
# Завдання 2. Факторіал через query-параметр
# GET /factorial?num=<n>
# ─────────────────────────────────────────────
@app.route('/factorial')
def factorial():
    num_str = request.args.get('num')
    if num_str is None:
        return "Please provide a valid number", 400

    try:
        num = int(num_str)
        if num < 0:
            return "Please provide a valid number", 400
    except ValueError:
        return "Please provide a valid number", 400

    result = 1
    for i in range(2, num + 1):
        result *= i

    return f"Factorial of {num} is {result}"


# ─────────────────────────────────────────────
# Завдання 3. Парне / непарне
# GET /even_odd/<n>
# ─────────────────────────────────────────────
@app.route('/even_odd/<int:n>')
def even_odd(n):
    if n % 2 == 0:
        return f"Number {n} is even"
    return f"Number {n} is odd"


# ─────────────────────────────────────────────
# Завдання 4. Простий калькулятор
# GET /calc?a=<a>&b=<b>&op=<add|sub|mul|div>
# ─────────────────────────────────────────────
@app.route('/calc')
def calc():
    a_str = request.args.get('a')
    b_str = request.args.get('b')
    op    = request.args.get('op')

    if a_str is None or b_str is None or op is None:
        return "Error: please provide parameters a, b and op", 400

    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        return "Error: a and b must be numbers", 400

    supported = ('add', 'sub', 'mul', 'div')
    if op not in supported:
        return f"Error: op must be one of {supported}", 400

    if op == 'div' and b == 0:
        return "Error: division by zero is not allowed", 400

    match op:
        case 'add': result = a + b
        case 'sub': result = a - b
        case 'mul': result = a * b
        case 'div': result = a / b

    def fmt(v):
        return int(v) if v == int(v) else v

    return f"Result of {fmt(a)} {op} {fmt(b)} = {fmt(result)}"


# ─────────────────────────────────────────────
# Завдання 5. Генератор простих чисел
# GET /primes?limit=<n>
# ─────────────────────────────────────────────
def sieve(limit: int) -> list[int]:
    """Решето Ератосфена."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i, p in enumerate(is_prime) if p]


@app.route('/primes')
def primes():
    limit_str = request.args.get('limit')

    if limit_str is None:
        return "Provide a number greater than 1", 400

    try:
        limit = int(limit_str)
    except ValueError:
        return "Provide a number greater than 1", 400

    if limit < 2:
        return "Provide a number greater than 1", 400

    result = sieve(limit)
    return f"Primes up to {limit}: {', '.join(map(str, result))}"


# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)