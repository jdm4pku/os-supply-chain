import matplotlib.pyplot as plt
import json
import os
from matplotlib.patches import Patch

def plot_box(os_version):
    data_sections = ["1-relevant"]
    plt.figure(figsize=(10, 6))  # 创建一个图形对象，用于绘制所有箱线图
    position = 1  # 初始箱线图位置
    legend_labels = []  # 存储图例标签
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightpink']  # 每个文件的颜色
    legend_handles = []  # 存储图例句柄

    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path, data_sec)
        
        for i, (os_name, os_arch, os_ver) in enumerate(os_version):
            dir_path = os.path.join(root_path, f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path, "result.json")
            fig_path = os.path.join(root_path, "result_box_test.png")

            with open(data_path, 'r') as f:
                data = json.load(f)
                
            # 提取评分数据
            scores = [data[key] for key in data]
            
            # 配置箱线颜色和图例标签
            box_props = dict(facecolor=colors[i], color='blue')  # 箱线样式
            legend_labels.append(f"{os_name}_{os_arch}_{os_ver}")  # 图例标签
            
            # 绘制每个数据文件的箱线图
            bp = plt.boxplot(scores, positions=[position], vert=False, patch_artist=True, meanline=True, boxprops=box_props)
            legend_handles.append(Patch(facecolor=colors[i], edgecolor='blue'))  # 添加当前箱线图的句柄
            plt.xlabel('Value')
            plt.grid(True)
            plt.title('Boxplot of Random Data')
            plt.xticks(rotation=45)
            
            position += 1  # 更新箱线图位置

    # 添加图例
    plt.legend(legend_handles, legend_labels, loc='lower right')
    
    plt.tight_layout()  # 调整布局以确保不重叠
    plt.savefig(fig_path)
    plt.show()



if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('centos', 'x86_64', '7'),
        ("openEuler", "x86_64", "openEuler-23.09"),
        # ('anolis', 'x86_64', '8.8'),
        # ('openCloudOS', 'x86_64', '8'),
    ]
    plot_box(os_versions)