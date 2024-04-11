import numpy as np
import matplotlib.pyplot as plt

# 元のデータポイント
set      = np.array([0, 1, 2, 3, 4])
measured = set * 1.2 + 0.05

print(set)
print(measured)

# 線形補間する新しいデータポイント
for i in range(5):
    calibrated_set = np.interp(i, measured , set)
    print(f"measured={i}, calibrated_set={calibrated_set:.3f}")
