import os
import json
import matplotlib.pyplot as plt


def plot_box(os_version):
    data_sections = ["0-cluster","1-relevant"]
    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path,data_sec)
        for os_name,os_arch,os_ver in os_version:
            dir_path = os.path.join(root_path,f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path,"result.json")
            fig_path = os.path.join(dir_path,"result_box.png")
            with open(data_path, 'r') as f:
                data = json.load(f)
            # 提取评分数据
            scores = [data[key] for key in data]
            # 绘制箱线图
            plt.figure(figsize=(8, 6))
            plt.boxplot(scores, vert=False, patch_artist=True, meanline=True)
            plt.title('Boxplot of Random Data')
            plt.xlabel('Value')
            plt.grid(True)
            plt.show()
            plt.savefig(fig_path)
            # plt.show()


if __name__=="__main__":
    os_versions = [
        # ("fedora", "x86_64", "38"),
        # ('centos', 'x86_64', '7'),
        ("openEuler", "x86_64", "openEuler-23.09"),

    ]
    plot_box(os_versions)