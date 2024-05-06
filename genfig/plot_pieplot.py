import os
import json
import matplotlib.pyplot as plt

def plot_pie(os_versions):
    data_sections = ["2-difference"]
    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path,data_sec)
        for os_name,os_arch,os_ver in os_versions:
            dir_path = os.path.join(root_path,f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path,"result.json")
            fig_path = os.path.join(dir_path,"result.png")
            with open(data_path, 'r') as file:
                data = json.load(file)
            if 'total_aver_score' in data:
                data.pop("total_aver_score", None)
            labels = data.keys()
            sizes = data.values()
            colors = plt.cm.Pastel1(range(len(labels)))  # 生成颜色
            plt.figure(figsize=(10, 7))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title(f'{os_name}_{os_arch}_{os_ver}')
            plt.axis('equal')  # 保证饼状图是圆的
            plt.show()
            plt.savefig(fig_path)

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('centos', 'x86_64', '7'),
        ("openEuler", "x86_64", "openEuler-23.09"),
    ]
    plot_pie(os_versions)
