import matplotlib.pyplot as plt


path = "/home/jindongming/project/1-OsSupplyChain/os-supply-chain/genfig/openEuler.txt"
# 读取数据文件
with open(path, 'r') as file:
    lines = file.readlines()

# 初始化三个列表
g_values = []
inpkg_values = []
tolpkg_values = []

# 提取数据并存储到列表中
for line in lines:
    parts = line.strip().split(',')
    for part in parts:
        if part.startswith('g-'):
            g_values.append(int(part.split('-')[1]))
        elif part.startswith('inpkg-'):
            inpkg_values.append(int(part.split('-')[1]))
        elif part.startswith('tolpkg-'):
            tolpkg_values.append(int(part.split('-')[1]))

# 绘制并保存折线图
plt.plot(g_values, label='g values')
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('g Values Trend')
plt.legend()
plt.savefig('g_values_trend_openEuler.png')
plt.close()

plt.plot(inpkg_values, label='inpkg values')
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('inpkg Values Trend')
plt.legend()
plt.savefig('inpkg_values_trend_openEuler.png')
plt.close()

plt.plot(tolpkg_values, label='tolpkg values')
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('tolpkg Values Trend')
plt.legend()
plt.savefig('tolpkg_values_trend_openEuler.png')
plt.close()