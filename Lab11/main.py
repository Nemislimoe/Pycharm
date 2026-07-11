"""
main.py

Python 3.14, NumPy 2.5.1, Pandas 3.0.3
"""

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

# -----------------------------------------------------------------
# 2. Створення DataFrame з даними про студентів (мінімум 8 студентів,
#    значення різних рівнів: низькі / середні / високі)
# -----------------------------------------------------------------
data = {
    "name": [
        "Олена Ковальчук", "Іван Петренко", "Марія Ткаченко", "Андрій Бондар",
        "Софія Мельник", "Дмитро Кравець", "Юлія Шевченко", "Максим Гончар",
        "Тетяна Лисенко", "Роман Савчук",
    ],
    "age": [19, 20, 19, 21, 20, np.nan, 22, 20, 19, 21],
    "hours_studied": [8, 2, 6, np.nan, 9, 3, 7, 1, 5, 10],
    "attendance": [95, 60, 82, 70, np.nan, 55, 88, 45, 78, 97],
    "exam_score": [88, 52, 76, 65, 91, np.nan, 84, 40, 70, 95],
}

df = pd.DataFrame(data)

print("=" * 70)
print("Початковий DataFrame")
print("=" * 70)
print(df)

# -----------------------------------------------------------------
# 3. Базова обробка даних
# -----------------------------------------------------------------
print("\n" + "=" * 70)
print("Перевірка пропущених значень")
print("=" * 70)
print(df.isna().sum())

# Логіка заповнення пропусків:
#   age            -> медіана (вік майже не має викидів, ціле значення)
#   hours_studied  -> медіана (стійка до викидів характеристика активності)
#   attendance     -> середнє значення (безперервний показник)
#   exam_score     -> медіана (щоб не спотворити результат викидами)
df["age"] = df["age"].fillna(df["age"].median())
df["hours_studied"] = df["hours_studied"].fillna(df["hours_studied"].median())
df["attendance"] = df["attendance"].fillna(df["attendance"].mean())
df["exam_score"] = df["exam_score"].fillna(df["exam_score"].median())

print("\nDataFrame після заповнення пропущених значень:")
print(df)

# -----------------------------------------------------------------
# 4. Аналіз
# -----------------------------------------------------------------
mean_exam_score = df["exam_score"].mean()
min_hours = df["hours_studied"].min()
max_hours = df["hours_studied"].max()
high_attendance_count = (df["attendance"] > 80).sum()

print("\n" + "=" * 70)
print("Аналіз даних")
print("=" * 70)
print(f"Середній exam_score: {mean_exam_score:.2f}")
print(f"Мінімальна кількість годин навчання (hours_studied): {min_hours}")
print(f"Максимальна кількість годин навчання (hours_studied): {max_hours}")
print(f"Кількість студентів з attendance > 80%: {high_attendance_count}")

# -----------------------------------------------------------------
# 5. Фільтрація
# -----------------------------------------------------------------
high_scorers = df[df["exam_score"] >= 75]
low_hours = df[df["hours_studied"] < 5]

print("\n" + "=" * 70)
print("Студенти з exam_score >= 75")
print("=" * 70)
print(high_scorers)

print("\n" + "=" * 70)
print("Студенти з hours_studied < 5")
print("=" * 70)
print(low_hours)

# -----------------------------------------------------------------
# 6. Проста rule-based "модель"
# -----------------------------------------------------------------
def predict(row):
    if row["hours_studied"] >= 6 and row["attendance"] >= 80:
        return "pass"
    return "risk"

df["prediction"] = df.apply(predict, axis=1)

# -----------------------------------------------------------------
# 7. Вивід результатів
# -----------------------------------------------------------------
print("\n" + "=" * 70)
print("Перші 5 рядків фінального DataFrame")
print("=" * 70)
print(df.head())

print("\n" + "=" * 70)
print("Результати фільтрів (нагадування)")
print("=" * 70)
print("\n-- exam_score >= 75 --")
print(high_scorers)
print("\n-- hours_studied < 5 --")
print(low_hours)

print("\n" + "=" * 70)
print("Колонка prediction")
print("=" * 70)
print(df[["name", "prediction"]])
