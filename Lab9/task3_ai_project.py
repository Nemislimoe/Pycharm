import pandas as pd

# 1. Збір даних

data = {

"product": ["A", "B", "C", "D"],

"sales_last_month": [100, 150, 50, 200]

}

df = pd.DataFrame(data)

print("1. Дані про продажі:")

print(df)


# 2. Підготовка даних

df["sales_last_month"] = df["sales_last_month"].fillna(0)


# 3. Аналіз (EDA)

print("\n3. Середні продажі:", df["sales_last_month"].mean())


# 4. Проста ML-модель (передбачення продажів наступного місяця)

df["predicted_next_month"] = df["sales_last_month"] * 1.1

print("\n4. Прогноз продажів на наступний місяць:")

print(df[["product", "predicted_next_month"]])