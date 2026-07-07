import pandas as pd
import matplotlib.pyplot as plt

# 1. Використовуємо очищений CSV з попереднього завдання
df = pd.read_csv("students_cleaned.csv")

# 2. Базова інформація про dataset
print("Розмір dataset (shape):", df.shape)

print("\nНазви колонок (columns):")
print(df.columns.tolist())

print("\nСтатистика числових колонок (describe()):")
print(df.describe())

# 3. Візуалізація
# Гістограма віку студентів
plt.figure(figsize=(6, 4))
df["Age"].hist(bins=8, color="skyblue", edgecolor="black")
plt.title("Розподіл віку студентів")
plt.xlabel("Age")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("hist_age.png", dpi=120)
plt.close()

# Scatter plot оцінки (Grade) від віку (Age)
plt.figure(figsize=(6, 4))
plt.scatter(df["Age"], df["Grade"], color="green")
plt.title("Залежність Grade від Age")
plt.xlabel("Age")
plt.ylabel("Grade")
plt.tight_layout()
plt.savefig("scatter_grade_age.png", dpi=120)
plt.close()

# 4. Унікальні міста та кількість студентів у кожному
print("\nКількість студентів по містах (value_counts()):")
print(df["City"].value_counts())
