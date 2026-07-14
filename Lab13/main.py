"""
Python 3.14 | NumPy 2.5.1 | Pandas 3.0.4
Matplotlib, Seaborn
P.s. треба створити папку imgs
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)

# =========================================================
# Завдання 1. Лінійний графік
# =========================================================
print("=" * 60)
print("ЗАВДАННЯ 1. Лінійний графік")
print("=" * 60)

days = list(range(1, 8))
temperature = [18, 20, 21, 19, 22, 24, 23]

print("Дні:", days)
print("Температура:", temperature)

plt.figure(figsize=(8, 5))
plt.plot(days, temperature, marker="o", color="tab:blue", linewidth=2)
plt.xlabel("День")
plt.ylabel("Температура, °C")
plt.title("Зміна температури протягом тижня")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("imgs/1_line_plot.png", dpi=150)
plt.close()
print("Графік збережено: imgs/1_line_plot.png\n")

# =========================================================
# Завдання 2. Стовпчиковий графік
# =========================================================
print("=" * 60)
print("ЗАВДАННЯ 2. Стовпчиковий графік")
print("=" * 60)

subjects = ["Math", "English", "Biology", "History"]
scores = [85, 90, 78, 88]

print("Предмети:", subjects)
print("Оцінки:", scores)

plt.figure(figsize=(8, 5))
plt.bar(subjects, scores, color="tab:orange")
plt.xlabel("Предмет")
plt.ylabel("Оцінка")
plt.title("Оцінки за предметами")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("imgs/2_bar_chart.png", dpi=150)
plt.close()
print("Графік збережено: imgs/2_bar_chart.png\n")

# =========================================================
# Завдання 3. Гістограма
# =========================================================
print("=" * 60)
print("ЗАВДАННЯ 3. Гістограма")
print("=" * 60)

random_values = np.random.normal(loc=70, scale=10, size=100)

print("Кількість значень:", len(random_values))
print(f"Середнє: {random_values.mean():.2f}")
print(f"Стандартне відхилення: {random_values.std():.2f}")
print(f"Мінімум: {random_values.min():.2f}, Максимум: {random_values.max():.2f}")

plt.figure(figsize=(8, 5))
plt.hist(random_values, bins=12, color="tab:green", edgecolor="black", alpha=0.8)
plt.xlabel("Значення")
plt.ylabel("Частота")
plt.title("Гістограма розподілу 100 випадкових значень (μ=70, σ=10)")
plt.tight_layout()
plt.savefig("imgs/3_histogram.png", dpi=150)
plt.close()
print("Графік збережено: imgs/3_histogram.png")
print(
    "Опис розподілу: значення утворюють симетричний дзвоноподібний розподіл,\n"
    "зосереджений навколо середнього ~70, що відповідає нормальному\n"
    "(гаусовому) закону розподілу з заданими параметрами.\n"
)

# =========================================================
# Завдання 4. Scatter plot
# =========================================================
print("=" * 60)
print("ЗАВДАННЯ 4. Scatter plot")
print("=" * 60)

height = [150, 155, 160, 165, 170, 175, 180, 185, 190, 195]
weight = [50, 53, 58, 62, 65, 70, 75, 80, 85, 92]

print("Зріст (см):", height)
print("Вага (кг):", weight)

corr = np.corrcoef(height, weight)[0, 1]
print(f"Коефіцієнт кореляції: {corr:.3f}")

plt.figure(figsize=(8, 5))
plt.scatter(height, weight, color="tab:red", s=60)
plt.xlabel("Зріст, см")
plt.ylabel("Вага, кг")
plt.title("Залежність ваги від зросту")
plt.tight_layout()
plt.savefig("imgs/4_scatter.png", dpi=150)
plt.close()
print("Графік збережено: imgs/4_scatter.png")
print(
    "Висновок: точки формують чітку висхідну лінію, коефіцієнт кореляції "
    f"({corr:.3f}) близький до 1, що свідчить про сильну позитивну лінійну\n"
    "залежність — чим більший зріст, тим більша вага.\n"
)

# =========================================================
# Завдання 5. Виявлення аномалій
# =========================================================
print("=" * 60)
print("ЗАВДАННЯ 5. Виявлення аномалій (boxplot)")
print("=" * 60)

normal_data = np.random.normal(loc=100, scale=15, size=50).tolist()
anomalies = [10, 15, 220]  # аномально малі та велике значення
data_with_anomalies = normal_data + anomalies

print(f"Розмір вибірки: {len(data_with_anomalies)} (з них {len(anomalies)} аномалії)")
print("Додані аномальні значення:", anomalies)

q1 = np.percentile(data_with_anomalies, 25)
q3 = np.percentile(data_with_anomalies, 75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
detected = [x for x in data_with_anomalies if x < lower_bound or x > upper_bound]

print(f"Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f}")
print(f"Межі норми: [{lower_bound:.2f}, {upper_bound:.2f}]")
print("Виявлені аномалії (виходять за межі 'вусів'):", [round(x, 2) for x in detected])

plt.figure(figsize=(7, 5))
sns.boxplot(y=data_with_anomalies, color="tab:purple")
plt.ylabel("Значення")
plt.title("Boxplot з аномальними значеннями")
plt.tight_layout()
plt.savefig("imgs/5_boxplot.png", dpi=150)
plt.close()
print("Графік збережено: imgs/5_boxplot.png")
print(
    "Висновок: точки за межами 'вусів' boxplot (нижче "
    f"{lower_bound:.1f} або вище {upper_bound:.1f}) є аномаліями — "
    "це три спеціально додані значення (10, 15 та 220), які значно\n"
    "відхиляються від основного розподілу даних.\n"
)

print("=" * 60)
print("Роботу виконано успішно.")
print("=" * 60)