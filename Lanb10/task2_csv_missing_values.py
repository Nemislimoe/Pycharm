import pandas as pd

# 1. Завантажуємо CSV файл students.csv
df = pd.read_csv("students.csv")

# 2. Виводимо перші 5 рядків dataset
print("Перші 5 рядків dataset:")
print(df.head())

# 3. Підраховуємо кількість пропущених значень по колонках
print("\nКількість пропущених значень по колонках:")
print(df.isnull().sum())

# 4. Заповнюємо пропущені значення:
# Age -- середнім значенням
df["Age"] = df["Age"].fillna(df["Age"].mean())

# Grade -- найчастішим значенням (модою)
df["Grade"] = df["Grade"].fillna(df["Grade"].mode()[0])

# City -- значенням "Unknown"
df["City"] = df["City"].fillna("Unknown")

print("\nDataset після заповнення пропущених значень:")
print(df)

# Зберігаємо очищений dataset для використання у Завданні 3
df.to_csv("students_cleaned.csv", index=False)
print("\nОчищений dataset збережено у students_cleaned.csv")
