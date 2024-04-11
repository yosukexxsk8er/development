
import numpy as np

# 2つの点の座標
x1, y1 = 0, 1
x2, y2 = 2, 4

# 直線の係数を計算
coefficients = np.polyfit([x1, x2], [y1, y2], 1)

# 多項式を表す関数を生成
polynomial_func = np.poly1d(coefficients)

print("直線の係数:", coefficients)
print("多項式の式:")
print(polynomial_func)
