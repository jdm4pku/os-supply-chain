"""
这个研究问题是想探究当前Linux操作系统软件包分组的合理性
(1) 同一个分组内包含的软件包的功能聚合程度
(2) 分组的描述信息与包含的软件包的相关性
(3) 不同分组的差异性
(4) 分组与其包含软件包的数量的分布情况
"""

import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import os
import json
import pandas as pd
from utils.json import load_file
from download_file.download_repomd import download_repo_metadata
from group.group_label import __repomd_get_group_file,get_groups_info,merge_groups
from pkg.pkg import __repomd_get_primary_file,get_pkgs_info,merge_pkgs
from sentence_transformers import SentenceTransformer,util
from utils.logger import get_logger

logger = get_logger(__name__)

def save_cluter_result(pkg_name_list,cosine_score,path):
    sum = 0
    count = 0
    data = []
    headers = ["pkg1","pkg2","simi"]
    for i in range(cosine_score.shape[0]):
        for j in range(cosine_score.shape[1]):
            row = []
            row.append(pkg_name_list[i])
            row.append(pkg_name_list[j])
            row.append(cosine_score[i][j])
            data.append(row)
            sum += cosine_score[i][j]
            count +=1
    df = pd.DataFrame(data,columns=headers)
    df_sorted = df.sort_values(by='simi',ascending=False)
    df_sorted.to_csv(path,index=False)
    average_score = sum / count
    return df_sorted, average_score


def save_relevant_result(pkg_name_list,cosine_score,path):
    sum = 0
    count = 0
    data = []
    headers = ["pkg","relevant"]
    for i in range(cosine_score.shape[1]):
        row = []
        row.append(pkg_name_list[i])
        row.append(cosine_score[0][i])
        sum += cosine_score[0][i]
        count +=1
    df = pd.DataFrame(data,columns=headers)
    df_sorted = df.sort_values(by='relevant',ascending=False)
    df_sorted.to_csv(path,index=False)
    average_score = sum / count
    return df_sorted, average_score

def RQ2(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    model = SentenceTransformer("all-MiniLM-L6-v2",device="cuda:1")
    for os_name,os_arch,os_ver in os_arch_ver:
        logger.info(f"-------{os_name}-{os_arch}-{os_ver}------")
        all_groups = None
        all_pkgs = None
        for os_k,os_url in metas[os_name].items():
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            group_file = __repomd_get_group_file(os_path)
            if group_file:
                os_groups, os_cate, os_env, os_langp = get_groups_info(os.path.join(os_path, group_file).replace('\\', '/'))
                all_groups = merge_groups(all_groups,os_groups)
        for os_k, os_url in metas[os_name].items():
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
        logger.info("------------RQ2:cluster----------------")
        # 第一问
        for group, info in all_groups:
            cluster_result = {}
            pkg_name_list = info["packagelist"]
            pkg_desc_list = [all_pkgs[name]["description"] for name in pkg_name_list]
            embeddings = model.encode(pkg_desc_list,convert_to_tensor=True)
            cosine_score = util.cos_sim(embeddings,embeddings)
            group_path = f"results/RQ2/0-cluster/{os_name}_{os_arch}_{os_ver}/{group}.csv"
            pair_simi,average_socre = save_cluter_result(pkg_name_list,cosine_score,group_path)
            logger.info(group)
            logger.info(pair_simi.head(5))
            logger.info(f"average_socre:{average_socre}")
            cluster_result[group] = average_socre
        cluster_result_path = f"results/RQ2/0-cluster/{os_name}_{os_arch}_{os_ver}/result.json"
        with open(cluster_result_path,'w') as f:
            json.dump(cluster_result,indent=4)
        
        # 第二问
        for group,info in all_groups:
            relevant_result = {}
            group_label = [info["description"][0]]
            pkg_name_list = info["packagelist"]
            pkg_desc_list = [all_pkgs[name]["description"] for name in pkg_name_list]
            embed1 = model.encode(group_label,convert_to_tensor=True)
            embed2 = model.encode(pkg_desc_list,convert_to_tensor=True)
            cosine_score = util.cos_sim(embed1,embed2)
            relevant_path = f"results/RQ2/1-relevant/{os_name}_{os_arch}_{os_ver}/{group}.csv"
            relevant_pair,average_socre = save_relevant_result(pkg_name_list,cosine_score,relevant_path)
            logger.info(group)
            logger.info(relevant_pair.head(5))
            logger.info(f"average_socre:{average_socre}")
            relevant_result[group] = average_socre
        relevant_result_path = f"results/RQ2/1-relevant/{os_name}_{os_arch}_{os_ver}/result.json"
        with open(relevant_result_path,'w') as f:
            json.dump(relevant_result,indent=4)
        
        # 第三问
        


            
        
        

            
                
            
        print("hello")


if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
    ]
    RQ2(os_versions,False)
