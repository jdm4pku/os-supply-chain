import os
import json
import matplotlib.pyplot as plt

def plot_pie(os_versions):
    data_sections = ["4-distribution"]
    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path,data_sec)
        for os_name,os_arch,os_ver in os_versions:
            dir_path = os.path.join(root_path,f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path,"result.json")
            fig_path = os.path.join(dir_path,"result.png")
            with open(data_path, 'r') as file:
                data = json.load(file)
            labels = data.keys()
            sizes = data.values()
            colors = plt.cm.Pastel1(range(len(labels)))  # 生成颜色
            plt.figure(figsize=(10, 7))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title('组内包的分布')
            plt.axis('equal')  # 保证饼状图是圆的
            plt.show()
            plt.savefig(fig_path)

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
    ]
    plot_pie(os_versions)
