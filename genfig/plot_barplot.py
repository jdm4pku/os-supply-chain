
import os
import json
import matplotlib.pyplot as plt

def plot_bar(os_version):
    data_sections = ["0-cluster","1-relevant"]
    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path,data_sec)
        for os_name,os_arch,os_ver in os_version:
            dir_path = os.path.join(root_path,f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path,"result.json")
            fig_path = os.path.join(dir_path,"result_bar.png")
            with open(data_path, 'r') as f:
                data = json.load(f)
            keys = data.keys()
            values = data.values()
            sorted_keys = [x for _, x in sorted(zip(values, keys), reverse=True)]
            sorted_values = sorted(values, reverse=True)
            plt.figure(figsize=(10, 8))
            plt.barh(sorted_keys, sorted_values, color='skyblue')
            plt.xlabel('Value')
            plt.title(f'{os_name}_{os_arch}_{os_ver}')
            plt.gca().invert_yaxis()  # Invert y-axis to display the highest value on top
            # plt.show()
            plt.savefig(fig_path)

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
        ('centos', 'x86_64', '7'),
    ]
    plot_bar(os_versions)
