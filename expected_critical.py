import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# クリティカル率（c）とクリティカルダメージ倍率（d）をそれぞれ5%刻みで生成
c_values = np.arange(0.0, 1.01, 0.05)  # 0%〜100%
d_values = np.arange(1.0, 3.01, 0.05)  # 100%〜300%

# 期待値関数
def expected_value(c, d):
    return 1 + c * (d - 1)

# ヒートマップデータを計算
increase_by_crit_rate = np.zeros((len(c_values), len(d_values)))
increase_by_crit_damage = np.zeros((len(c_values), len(d_values)))
increase_diff = np.zeros((len(c_values), len(d_values)))

for i, c in enumerate(c_values):
    for j, d in enumerate(d_values):
        # cが1%増加したときの期待値差分
        delta_c = expected_value(c + 0.01, d) / expected_value(c, d) -1
        increase_by_crit_rate[i, j] = delta_c

        # dが1%増加したときの期待値差分
        delta_d = expected_value(c, d + 0.02) / expected_value(c, d) -1
        increase_by_crit_damage[i, j] = delta_d

        increase_diff[i, j] = (delta_d - delta_c) 

# 描画関数
def plot_heatmap(data, title, xlabel, ylabel):
    plt.figure(figsize=(12, 8))
    sns.heatmap(data, xticklabels=np.round(d_values, 2), yticklabels=np.round(c_values, 2), cmap='coolwarm', center=0)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"heatmap_{title}.png")  # 保存先のファイル名を指定
    plt.close()  # プロットを閉じる

# ヒートマップ描画
plot_heatmap(increase_by_crit_rate, 'Increased Value (Critical Rate +1%)', 'Cricical Damage', 'Critical Rate')
plot_heatmap(increase_by_crit_damage, 'Increased Value (Critical Damage +2%)', 'Critical Damage', 'Critical Rate')
plot_heatmap(increase_diff, 'Difference in Increased Value (Critical Damage - Critical Rate)', 'Critical Damage', 'Critical Rate')
