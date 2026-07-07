import numpy as np
import pandas as pd

# 1. Створюємо масив чисел від 1 до 20 за допомогою NumPy
numbers = np.arange(1, 21)
print("Масив чисел від 1 до 20:")
print(numbers)

# 2. Ділимо масив на парні та непарні числа
even_numbers = numbers[numbers % 2 == 0]
odd_numbers = numbers[numbers % 2 != 0]
print("\nПарні числа:")
print(even_numbers)
print("\nНепарні числа:")
print(odd_numbers)

# 3. Створюємо DataFrame з колонками Number, Square, Cube
df = pd.DataFrame({
    "Number": numbers,
    "Square": numbers ** 2,
    "Cube": numbers ** 3
})

# 4. Виводимо перші 5 рядків DataFrame
print("\nПерші 5 рядків DataFrame:")
print(df.head())
