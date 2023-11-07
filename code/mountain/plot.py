import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams['font.family'] = 'SimHei'

def read_from_file(path):
    z = []
    y_ticklabels = []
    with open("./mountain.txt") as f:
        lines = f.readlines()
        x_ticklabels = lines[2].strip().split('\t')
        for line in lines[3:]:
            line = line.strip().split('\t')
            if len(line) != 0:
                y_ticklabels.append(line[0])
            z.append([int(i) for i in line[1:]])
    return np.array(z) , np.array(x_ticklabels), np.array(y_ticklabels)
            

# 创建一个3D图形对象
fig = plt.figure()
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122, projection='3d')

# 创建网格数据
x = np.arange(15)
y = np.arange(14)
x, y = np.meshgrid(x, y)
z, x_ticklabels , y_ticklabels = read_from_file("./mountain.txt")

# 绘制3D曲面图，应用颜色映射
colormap = plt.get_cmap('plasma')
for ax in [ax1, ax2]:
    surf = ax.plot_surface(x, y, z, cmap=colormap)

    # 设置轴标签
    ax.set_xlabel('步长\n(x8 bytes)')
    ax.set_ylabel('大小(bytes)')
    ax.set_zlabel('读吞吐量(MB/s)')

    ax.set_xticks(range(len(x_ticklabels)))
    ax.set_yticks(range(len(y_ticklabels)))
    ax.set_xticklabels(x_ticklabels)
    ax.set_yticklabels(y_ticklabels)

ax1.view_init(azim=-90)
ax2.view_init(elev=90, azim=0)

# 显示图形
plt.show()
