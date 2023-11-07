---
title: Matploitlib
date: 2023-11-04 20:37:58
tags: Matpolitlib
categories: Learning-Python
---

学习使用Matploitlib包绘制各类图形。

<!-- more -->



示例代码

```python
import matplotlib.pyplot as plt
import numpy as np

# 导入绘制三维的模块
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(20,10))

# 绘制三维曲线
axl = fig.add_subplot(221,projection='3d')
theta = np.linspace(-4*np.pi, 4*np.pi, 500)
z = np.linspace(-2,2,500)
r = z**2 + 1
x = r*np.sin(theta)
y = r*np.conj(theta)

# 方法与绘制二维曲线图相同
axl.plot(x,y,z)
axl.set_xlabel('x', fontsize=15)
axl.set_ylabel('y', fontsize=15)
axl.set_zlabel('z', fontsize=15)

# 绘制三维散点图
axl2 = fig.add_subplot(222,projection='3d')

x = np.random.randn(500)
y = np.random.randn(500)
z = np.random.randn(500)


# 方法与绘制二维曲线图相同
axl2.scatter(x,y,z,c='r')
axl2.set_xlabel('x', fontsize=15)
axl2.set_ylabel('y', fontsize=15)
axl2.set_zlabel('z',fontsize=15)

# 绘制三维曲面图
axl3 = fig.add_subplot(223,projection='3d')
x = np.linspace(-2,2,500)
y = np.linspace(-2,2,500)
x,y = np.meshgrid(x,y)
z = np.sqrt(x**2 + y**2)
axl3.plot_surface(x,y,z,cmap=plt.cm.winter)
axl3.set_xlabel('x', fontsize=15)
axl3.set_ylabel('y', fontsize=15)
axl3.set_zlabel('z', fontsize=15)


# 绘制三维条形图
axl4 = fig.add_subplot(224, projection='3d')
for z in np.arange(0,40,10):
    x = np.arange(20)
    y = np.random.randn(20)
    axl4.bar(x,y,zs=z,zdir='y')

axl4.set_xlabel('x',fontsize=15)
axl4.set_ylabel('y',fontsize=15)
axl4.set_zlabel('z',fontsize=15)


plt.show()
```

