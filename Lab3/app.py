from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'book-catalog-secret-key'

# ── База даних ──────────────────────────────────────────
# Файл books.db буде створено автоматично в папці проєкту
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ── Модель ──────────────────────────────────────────────
class Book(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    title  = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    year   = db.Column(db.Integer)

    def __repr__(self):
        return f'<Book {self.id}: {self.title}>'


# Створити таблиці при першому запуску
with app.app_context():
    db.create_all()


# ── Маршрути ────────────────────────────────────────────

# Редірект з головної на список книг
@app.route('/')
def index():
    return redirect(url_for('books_list'))


# GET /books — список усіх книг
@app.route('/books')
def books_list():
    books = Book.query.order_by(Book.id.desc()).all()
    return render_template('books_list.html', books=books)


# GET /books/add — форма додавання
@app.route('/books/add', methods=['GET'])
def book_add_form():
    return render_template('book_add.html')


# POST /books/add — збереження нової книги
@app.route('/books/add', methods=['POST'])
def book_add():
    title  = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    year   = request.form.get('year', '').strip()

    # Валідація
    errors = {}
    if not title:
        errors['title'] = "Назва є обов'язковим полем."

    if errors:
        # Повертаємо форму з помилками і введеними значеннями
        form_data = {'title': title, 'author': author, 'year': year}
        return render_template('book_add.html', errors=errors, form=form_data), 400

    # Конвертуємо рік
    year_int = int(year) if year.isdigit() else None

    new_book = Book(title=title, author=author or None, year=year_int)
    db.session.add(new_book)
    db.session.commit()

    flash(f'Книгу «{title}» успішно додано!', 'success')
    return redirect(url_for('books_list'))


# GET /books/<id>/edit — форма редагування
@app.route('/books/<int:book_id>/edit', methods=['GET'])
def book_edit_form(book_id):
    book = db.get_or_404(Book, book_id)
    return render_template('book_edit.html', book=book)


# POST /books/<id>/update — збереження змін
@app.route('/books/<int:book_id>/update', methods=['POST'])
def book_update(book_id):
    book   = db.get_or_404(Book, book_id)
    title  = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    year   = request.form.get('year', '').strip()

    # Валідація
    errors = {}
    if not title:
        errors['title'] = "Назва є обов'язковим полем."

    if errors:
        return render_template('book_edit.html', book=book, errors=errors), 400

    book.title  = title
    book.author = author or None
    book.year   = int(year) if year.isdigit() else None
    db.session.commit()

    flash(f'Книгу «{title}» оновлено!', 'success')
    return redirect(url_for('books_list'))


# POST /books/<id>/delete — видалення книги
@app.route('/books/<int:book_id>/delete', methods=['POST'])
def book_delete(book_id):
    book = db.get_or_404(Book, book_id)
    title = book.title
    db.session.delete(book)
    db.session.commit()

    flash(f'Книгу «{title}» видалено.', 'success')
    return redirect(url_for('books_list'))


# ────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)