
import os
import json
import matplotlib.pyplot as plt
import numpy as np

def plot_bar(os_version):
    data_sections = ["0-cluster","1-relevant"]
    for data_sec in data_sections:
        dir_path = "results/RQ2"
        root_path = os.path.join(dir_path,data_sec)
        for os_name,os_arch,os_ver in os_version:
            dir_path = os.path.join(root_path,f"{os_name}_{os_arch}_{os_ver}")
            data_path = os.path.join(dir_path,"result.json")
            fig_path = os.path.join(dir_path,"result_histogram.png")
            with open(data_path, 'r') as f:
                data = json.load(f)
            keys = data.keys()
            values = data.values()
            values = [float(v) for v in values]
            bins = np.linspace(0, 1, 11)
            hist, bin_edges = np.histogram(values, bins=bins)
            labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(bin_edges)-1)]
            # Create the bar chart
            plt.figure(figsize=(10, 6))
            plt.bar(labels, hist, color='skyblue')
            plt.xlabel('Value Ranges')
            plt.ylabel('Number of Categories')
            plt.title('Histogram of Categories by Value Range')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(fig_path)

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
    ]
    plot_bar(os_versions)
