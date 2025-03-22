# 销量可视化和预测

import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import curve_fit

# 使用机器学习中非线性最小二乘拟合预测销量数据

sales = pd.read_csv("crawler/2101_2212新能源汽车总体销量数据.csv")
group = sales.groupby("3")

def month_sales(sales):
    start = int(sales[0][-1])
    month_sale = {start: 0}
    for sale in sales:
        time_key = sale[-1]
        if time_key in month_sale:
            month_sale[time_key] += sale[3]
        else:
            month_sale[time_key] = 0
        pass
    return month_sale

def plot_sale(x, y, title, density = True):
    plt.scatter(x, y, c='red',  # 点的颜色
                label='Sales')
    # 设置图表大小
    # plt.rcParams['figure.figsize'] = (3, 3)  # 设置figure
    # 设置dpi
    # plt.rcParams['figure.dpi'] = 300  # 设置分辨率
    plt.legend()  #显示上面的label
    plt.xticks(rotation=70)
    plt.xlabel('Time/Month') #x_label
    plt.ylabel('Sales/Vehicle')#y_label
    plt.title(title)
    # #plt.ylim(-1,1)#仅设置y轴坐标范围
    if density:
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(15))
    plt.show()

# 案例分析
# 比亚迪
byd = group.get_group("比亚迪").values
byd_month_sale = month_sales(byd)
x = list(byd_month_sale.keys())
x.sort()
plot_sale([str(i) for i in x], 
          [byd_month_sale[i] for i in x], 
          "BYD Sales")

# 销量预测
# 自定义函数，curve_fit支持自定义函数的形式进行拟合，这里定义的是指数函数的形式
# 包括自变量x和a，b，c三个参数
def func_byd(x, a, b, c):
    return a * np.exp(-b * x) + c
 
x = list(byd_month_sale.keys())
x.sort()
# 产生数据
xdata = np.array([i for i in range(len(x))])
y = np.array([byd_month_sale[i] for i in x])
 
# 在y上产生一些扰动模拟真实数据
np.random.seed(1729)
# 产生均值为0，标准差为1，维度为xdata大小的正态分布随机抽样0.2倍的扰动
y_noise = 0.2 * np.random.normal(size=xdata.size) 
ydata = y + y_noise

x_pred = [i for i in range(202301, 202313)]
# 利用真实数据进行曲线拟合
popt, pcov = curve_fit(func_byd, xdata, ydata) # 拟合方程，参数包括func，xdata，ydata，
# 有popt和pcov两个个参数，其中popt参数为a，b，c，pcov为拟合参数的协方差

plt.scatter([str(i) for i in x + x_pred], func_byd(np.array([i for i in range(len(x + x_pred))]), *popt), c='blue',
         label='Pred.',s=5)
plt.scatter([str(i) for i in x], y, c='red',  # 点的颜色
            label='Sales',s=5)

 
# plot出拟合曲线，其中的y使用拟合方程和xdata求出
plt.plot([str(i) for i in x + x_pred], func_byd(np.array([i for i in range(len(x + x_pred))]), *popt), 'g-',
         label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
    
 
#     如果参数本身有范围，则可以设置参数的范围，如 0 <= a <= 3,
#     0 <= b <= 1 and 0 <= c <= 0.5:
# popt, pcov = curve_fit(func_byd, xdata, ydata, bounds=(0, [3., 1., 0.5])) # bounds为限定a，b，c参数的范围
 
# plt.plot(xdata, func_byd(xdata, *popt), 'g--',
#               label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
plt.xticks(rotation=70)
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(5))
plt.xlabel('Time/Month')
plt.ylabel('Sales/Vehicle')
plt.title("BYD Sales")
plt.legend()
plt.show()
