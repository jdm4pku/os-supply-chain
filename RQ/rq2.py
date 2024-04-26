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
import numpy as np
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
    # df_sorted.to_csv(path,index=False)
    average_score = sum / count
    return df_sorted, average_score

def name_simi_score(str1,str2):
    # 计算编辑距离（Edit Distance）
    def edit_distance(s1, s2):
        m, n = len(s1), len(s2)
        dp = np.zeros((m+1, n+1))
        
        for i in range(m+1):
            for j in range(n+1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j],      # 删除
                                       dp[i][j-1],      # 插入
                                       dp[i-1][j-1])   # 替换
        return dp[m][n]
    
    # 计算字符串长度
    len_str1 = len(str1)
    len_str2 = len(str2)
    
    # 计算编辑距离
    ed = edit_distance(str1, str2)
    
    # 计算最大字符串长度
    max_len = max(len_str1, len_str2)
    
    # 计算相似度
    similarity = 1 - (ed / max_len)
    
    return similarity


# def jaccard_similarity(pl_i, pl_j):
#     # 转换列表为集合
#     set_i = set(pl_i)
#     set_j = set(pl_j)
    
#     # 计算交集和并集
#     intersection = set_i.intersection(set_j)
#     union = set_i.union(set_j)
    
#     # 计算Jaccard相似度
#     similarity = len(intersection) / len(union)
#     return similarity

# 加权 jaccard_similarity

def weighted_jaccard_similarity(dict1,dict2):
    # 将字典的格式转换为集合格式
    set_1 = {(elem,eltype)for elem,eltype in dict1.items()}
    set_2 = {(elem,eltype)for elem,eltype in dict2.items()}
    # 类型到权重的映射
    type2weight = {"mandatory":1,"default":0.7,"conditional":0.4,"optional":0.1}
    intersection_weight = sum(min(type2weight[type_1],type2weight[type_2])
                       for (elem_1,type_1) in set_1
                       for (elem_2,type_2) in set_2
                       if elem_1 == elem_2)
    union_dict = {}
    for elem,eltype in set_1:
        union_dict[elem] = type2weight[eltype]
    for elem,eltype in set_2:
        if elem in union_dict:
            union_dict[elem] = max(union_dict[elem], type2weight[eltype])
        else:
            union_dict[elem] = type2weight[eltype]
    union_weight = sum(union_dict.values())
    similarity = intersection_weight / union_weight if union_weight else 0
    return similarity


def save_relevant_result(pkg_name_list,cosine_score,path):
    print(f"---{len(pkg_name_list)}---")
    print(f"---{cosine_score.shape}")
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
    # df_sorted.to_csv(path,index=False)
    average_score = sum / count
    return df_sorted, average_score

def save_difference(all_group_name,desc_cosine_socre,name_edit_simi,pl_jaccard_simi,path):
    count = 0
    data = []
    headers = ["g1","g2","desc_simi","name_simi","pl_simi","total_simi"]
    desc_average_simi = 0
    name_average_simi = 0
    pl_average_simi = 0
    total_average_simi = 0
    count = 0
    for i in range(desc_cosine_socre.shape[0]):
        for j in range(desc_cosine_socre.shape[1]):
            total_simi = ((desc_cosine_socre[i][j]+1)/2 + name_edit_simi[i][j] + pl_jaccard_simi[i][j]) / 3
            desc_average_simi +=desc_cosine_socre[i][j]
            name_average_simi +=name_edit_simi[i][j]
            pl_average_simi +=pl_jaccard_simi[i][j]
            total_average_simi +=total_simi
            row = []
            row.append(all_group_name[i])
            row.append(all_group_name[j])
            row.append(desc_cosine_socre[i][j])
            row.append(name_edit_simi[i][j])
            row.append(pl_jaccard_simi[i][j])
            row.append(total_simi)
            count +=1
    df = pd.DataFrame(data,columns=headers)
    df_sorted = df.sort_values(by='total_simi',ascending=False)
    # df_sorted.to_csv(path,index=False)
    desc_average_simi /=count
    name_average_simi /=count
    pl_average_simi /=count
    total_average_simi /=count
    return df_sorted, desc_average_simi,name_average_simi,pl_average_simi,total_average_simi

def count_pkgnum_eachgroup(all_groups):
    print(f"group num:{len(all_groups)}")
    pkg_group = {}
    for item in all_groups.values():
        pkg_num = len(item['packagelist'])
        if pkg_num in pkg_group:
            pkg_group[pkg_num] +=1
        else:
            pkg_group[pkg_num] = 1
    pkg_group_sorted = dict(sorted(pkg_group.items()))
    logger.info(pkg_group_sorted)
    return pkg_group_sorted   

def RQ2(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    model = SentenceTransformer("all-MiniLM-L6-v2",device="cuda:3")
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
            os_path,os_files =download_repo_metadata(os_url.format(arch=os_arch, ver=os_ver), "./data/", override)
            primary_file = __repomd_get_primary_file(os_path)
            if primary_file:
                os_pkgs = get_pkgs_info(os.path.join(os_path, primary_file).replace('\\', '/'))
                all_pkgs = merge_pkgs(all_pkgs,os_pkgs)
        logger.info("------------RQ2:cluster----------------")
        # 第一问
        cluster_result = {}
        for group, info in all_groups.items():
            pkg_name_list = info["packagelist"]
            pkg_desc_list = []
            new_pkg_name_list = []
            for name in pkg_name_list:
                if name not in all_pkgs:
                    logger.info("Below pkgs are not found in primary")
                    logger.info(name)
                    continue
                else:
                    pkg_desc_list.append(all_pkgs[name]["description"])
                    new_pkg_name_list.append(name)
            embeddings = model.encode(pkg_desc_list,convert_to_tensor=True)
            cosine_score = util.cos_sim(embeddings,embeddings)
            cosine_score = cosine_score.cpu().detach().numpy()
            group_path = f"results/RQ2/0-cluster/{os_name}_{os_arch}_{os_ver}"
            if not os.path.exists(group_path):
                os.mkdir(group_path)
            group_path = os.path.join(group_path,f"{group}.csv")
            pair_simi,average_socre = save_cluter_result(new_pkg_name_list,cosine_score,group_path)
            logger.info(group)
            logger.info(pair_simi.head(5))
            logger.info(f"average_socre:{average_socre}")
            cluster_result[group] = average_socre
        cluster_result_path = f"results/RQ2/0-cluster/{os_name}_{os_arch}_{os_ver}/result.json"
        with open(cluster_result_path,'w') as f:
            json.dump(cluster_result,f,indent=4)
        
        # # 第二问
        # logger.info("------------RQ2:relevant----------------")
        # relevant_result = {}
        # for group,info in all_groups.items():
        #     group_label = [info["description"][0]]
        #     pkg_name_list = info["packagelist"]
        #     new_pkg_name_list = []
        #     pkg_desc_list = []
        #     for name in pkg_name_list:
        #         if name not in all_pkgs:
        #             logger.info("Below pkgs are not found in primary")
        #             logger.info(name)
        #             continue
        #         else:
        #             pkg_desc_list.append(all_pkgs[name]["description"])
        #             new_pkg_name_list.append(name)
        #     embed1 = model.encode(group_label,convert_to_tensor=True)
        #     embed2 = model.encode(pkg_desc_list,convert_to_tensor=True)
        #     cosine_score = util.cos_sim(embed1,embed2)
        #     cosine_score = cosine_score.cpu().detach().numpy()
        #     relevant_path = f"results/RQ2/1-relevant/{os_name}_{os_arch}_{os_ver}"
        #     if not os.path.exists(relevant_path):
        #         os.mkdir(relevant_path)
        #     relevant_path = os.path.join(relevant_path,f"{group}.csv")
        #     relevant_pair,average_socre = save_relevant_result(new_pkg_name_list,cosine_score,relevant_path)
        #     logger.info(group)
        #     logger.info(relevant_pair.head(5))
        #     logger.info(f"average_socre:{average_socre}")
        #     relevant_result[group] = average_socre
        # relevant_result_path = f"results/RQ2/1-relevant/{os_name}_{os_arch}_{os_ver}/result.json"
        # with open(relevant_result_path,'w') as f:
        #     json.dump(relevant_result,f,indent=4)
        
        # # 第三问
        # logger.info("------------RQ2:differnce----------------")
        # all_group_desc = [info["description"] for group,info in all_groups.items()]
        # all_group_name = [info["name"][0] for group,info in all_groups.items()]
        # all_group_pkglist = [info["packagelist"] for group,info in all_groups.items()]
        # group_desc_embed = model.encode(all_group_desc,convert_to_tensor=True)
        # # # 范围是[-1,1]
        # desc_cosine_socre = util.cos_sim(group_desc_embed,group_desc_embed)
        # desc_cosine_socre = desc_cosine_socre.cpu().detach().numpy()
        # # 范围是[0,1]
        # name_edit_simi = []
        # for i,g1 in enumerate(all_group_name):
        #     row = []
        #     for j,g2 in enumerate(all_group_name):
        #         similarity = name_simi_score(g1, g2)
        #         row.append(similarity)
        #     name_edit_simi.append(row)
        # # 范围是[0,1]
        # pl_jaccard_simi = []
        # for i,pl1 in enumerate(all_group_pkglist):
        #     row = []
        #     for j,pl2 in enumerate(all_group_pkglist):
        #         similarity = weighted_jaccard_similarity(pl1,pl2)
        #         row.append(similarity)
        #     pl_jaccard_simi.append(row)
        # difference_path = f"results/RQ2/2-difference/{os_name}_{os_arch}_{os_ver}"
        # if not os.path.exists(difference_path):
        #         os.mkdir(difference_path)
        # difference_path = os.path.join(difference_path,"result.csv")
        # diff_result,desc_aver,name_aver,pl_aver,total_aver = save_difference(all_group_name,desc_cosine_socre,name_edit_simi,pl_jaccard_simi,difference_path)
        # logger.info(diff_result.head(5))
        # logger.info(f"desc_aver_socre:{desc_aver}")
        # logger.info(f"name_aver_socre:{name_aver}")
        # logger.info(f"pl_aver_socre:{pl_aver}")
        # logger.info(f"total_aver_socre:{total_aver}")
        # total_difference_result = {}
        # total_difference_path = f"results/RQ2/2-difference/{os_name}_{os_arch}_{os_ver}/result.json"
        # total_difference_result["desc_aver_score"] = desc_aver
        # total_difference_result["name_aver_score"] = name_aver
        # total_difference_result["pkglist_aver_score"] = pl_aver
        # total_difference_result["total_aver_score"] = total_aver
        # with open(total_difference_path,'w') as f:
        #     json.dump(total_difference_result,f,indent=4)
        # # 第四问
        # logger.info("------------RQ2:distribution----------------")
        # distribute_result = count_pkgnum_eachgroup(all_groups)
        # distribution_path = f"results/RQ2/4-distribution/{os_name}_{os_arch}_{os_ver}/result.json"
        # with open(distribution_path,'w') as f:
        #     json.dump(distribute_result,f,indent=4)
        # pass


if __name__=="__main__":
    os_versions = [
        # ("fedora", "x86_64", "38"),
        # ('centos', 'x86_64', '7'),
        ("openEuler", "x86_64", "openEuler-23.09")
    ]
    RQ2(os_versions,False)
