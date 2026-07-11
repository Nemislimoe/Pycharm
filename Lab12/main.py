"""
Python 3.14 / NumPy 2.5.1 / Pandas 3.0.4 / scikit-learn
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

print("=" * 70)
print("1. ЗАВАНТАЖЕННЯ ТА АНАЛІЗ ДАНИХ")
print("=" * 70)

df = pd.read_csv("customers.csv")

print("\n--- Перші 5 рядків ---")
print(df.head())

print("\n--- Типи даних (df.dtypes) ---")
print(df.dtypes)

print("\n--- Кількість пропущених значень ---")
print(df.isnull().sum())

print("""
Проблеми в даних:
- Salary має 1 пропущене значення (клієнт #4, Odesa).
- Experience має 1 пропущене значення (клієнт #6, Kyiv).
- City та Education - текстові (категоріальні) стовпці, ML-алгоритми
  не можуть працювати з ними напряму - потрібне кодування.
- Age і Salary мають дуже різні масштаби (роки проти десятків тисяч),
  тому без масштабування алгоритми, чутливі до відстаней, будуть
  надавати штучно завищену вагу Salary.
""")

print("=" * 70)
print("2. ОБРОБКА ПРОПУЩЕНИХ ЗНАЧЕНЬ")
print("=" * 70)

df["Age"] = df["Age"].fillna(df["Age"].mean())
df["Salary"] = df["Salary"].fillna(df["Salary"].mean())
df["Experience"] = df["Experience"].fillna(df["Experience"].median())

print("\n--- Пропуски після заповнення ---")
print(df.isnull().sum())
print("\n--- DataFrame після заповнення пропусків ---")
print(df)

print("=" * 70)
print("3. FEATURE ENGINEERING")
print("=" * 70)

# 1. Salary per year of experience
# Experience = 0 не зустрічається в даних після заповнення медіаною,
# але про всяк випадок захищаємось від ділення на нуль.
df["SalaryPerExperience"] = df["Salary"] / df["Experience"].replace(0, np.nan)
df["SalaryPerExperience"] = df["SalaryPerExperience"].fillna(df["Salary"])


def age_category(age):
    if age < 30:
        return "young"
    elif age <= 50:
        return "middle"
    else:
        return "senior"


df["AgeCategory"] = df["Age"].apply(age_category)

df["IsHighIncome"] = (df["Salary"] > 70000).astype(int)

print("\n--- Нові ознаки ---")
print(df[["Age", "Salary", "Experience", "SalaryPerExperience",
          "AgeCategory", "IsHighIncome"]])

print("""
Навіщо ці ознаки корисні:
- SalaryPerExperience показує "ефективність" зарплати відносно
  досвіду - двоє з однаковою зарплатою, але різним досвідом,
  насправді знаходяться в різному становищі.
- AgeCategory перетворює вік у зрозумілу групу, що допомагає моделі
  вловлювати нелінійні залежності (наприклад, поведінка покупця
  може різнитись за віковими групами, а не лінійно зростати з віком).
- IsHighIncome - явний бінарний сигнал "високий дохід", який може
  напряму корелювати з цільовою змінною Purchased і полегшити
  моделі пошук закономірності.
""")

print("=" * 70)
print("4. КОДУВАННЯ КАТЕГОРІАЛЬНИХ ЗМІННИХ")
print("=" * 70)

df_encoded = pd.get_dummies(
    df,
    columns=["City", "Education", "AgeCategory"],
)

print("\n--- DataFrame після One-Hot Encoding ---")
print(df_encoded.head())
print("\nСтовпці:", list(df_encoded.columns))

print("=" * 70)
print("5. МАСШТАБУВАННЯ ДАНИХ")
print("=" * 70)

numeric_cols = ["Age", "Salary", "Experience", "SalaryPerExperience"]

minmax_scaler = MinMaxScaler()
X_normalized = minmax_scaler.fit_transform(df_encoded[numeric_cols])
df_normalized = pd.DataFrame(X_normalized, columns=numeric_cols)

std_scaler = StandardScaler()
X_standardized = std_scaler.fit_transform(df_encoded[numeric_cols])
df_standardized = pd.DataFrame(X_standardized, columns=numeric_cols)

print("\n--- Normalization (MinMaxScaler): перші рядки ---")
print(df_normalized.head())

print("\n--- Standardization (StandardScaler): перші рядки ---")
print(df_standardized.head())

comparison = pd.DataFrame({
    "mean_normalized": df_normalized.mean(),
    "std_normalized": df_normalized.std(),
    "min_normalized": df_normalized.min(),
    "max_normalized": df_normalized.max(),
    "mean_standardized": df_standardized.mean(),
    "std_standardized": df_standardized.std(),
    "min_standardized": df_standardized.min(),
    "max_standardized": df_standardized.max(),
})

print("\n--- Порівняння: середнє / стд / діапазон ---")
print(comparison.round(3))

print("""
Висновок:
- Normalization (MinMaxScaler) завжди приводить значення точно
  у діапазон [0, 1], але середнє та стандартне відхилення
  відрізняються для кожної ознаки і залежать від min/max вихідних
  даних (тобто чутливі до викидів).
- Standardization (StandardScaler) робить середнє близьким до 0,
  а стандартне відхилення - до 1 для КОЖНОЇ ознаки, але при цьому
  діапазон значень не фіксований (може виходити за межі [0, 1] і
  навіть бути від'ємним).
- Для нашого маленького датасету з викидом (Salary=120000 проти
  Salary=48000) видно, що після нормалізації діапазон завжди [0, 1],
  а після стандартизації розкид значень (min/max) більший і залежить
  від того, наскільки далеко викид від середнього.
""")

print("=" * 70)
print("6. TRAIN / TEST SPLIT")
print("=" * 70)

X = df_encoded.drop(columns=["Purchased"])
y = df_encoded["Purchased"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nРозмір X_train: {X_train.shape}")
print(f"Розмір X_test:  {X_test.shape}")
print(f"Розмір y_train: {y_train.shape}")
print(f"Розмір y_test:  {y_test.shape}")

print("=" * 70)
print("7. ДОДАТКОВО: Logistic Regression")
print("=" * 70)

# Масштабуємо X перед навчанням моделі (весь набір ознак числовий
# після One-Hot Encoding, тому масштабуємо все через StandardScaler)
final_scaler = StandardScaler()
X_train_scaled = final_scaler.fit_transform(X_train)
X_test_scaled = final_scaler.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

accuracy = model.score(X_test_scaled, y_test)
print(f"\nAccuracy на тестовій вибірці: {accuracy:.3f}")
print("""
(Через дуже малий розмір датасету (лише 10 рядків, 2 з яких у тесті)
результат accuracy має ілюстративний характер і не є статистично
показовим - у реальних задачах потрібні тисячі спостережень.)
""")