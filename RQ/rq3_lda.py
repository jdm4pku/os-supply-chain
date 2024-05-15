import os,sys
print(os.getcwd())
sys.path.append(os.getcwd())
import os
from utils.json import load_file
from utils.logger import get_logger
from download_file.download_repomd import download_repo_metadata
from group.group_label import __repomd_get_group_file,get_groups_info,merge_groups
from pkg.pkg import __repomd_get_primary_file,get_pkgs_info,merge_pkgs
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance, TextGeneration
from huggingface_hub import login
import transformers
from umap import UMAP
from hdbscan import HDBSCAN
from torch import bfloat16
import gensim
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS

# # login()
# logger = get_logger(__name__)

def preprocess(text):
    return [word for word in simple_preprocess(text) if word not in STOPWORDS]


def RQ3(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
    for os_name,os_arch,os_ver in os_arch_ver:
        # logger.info(f"-------{os_name}-{os_arch}-{os_ver}------")
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
        # logger.info("------------RQ3:bert-topic----------------")
        pkg_in_group = []
        for group,info in all_groups.items():
            for pkg in info["packagelist"]:
                pkg_in_group.append(pkg)
        desc_in_group = []
        name_in_group = []
        desc_not_in_group = []
        name_not_in_group = []
        for pkg,info in all_pkgs.items():
            if pkg in pkg_in_group:
                if info["description"] is not None:
                    name_in_group.append(pkg)
                    desc_in_group.append(info["description"])
            else:
                if info["description"] is not None:
                    name_not_in_group.append(pkg)
                    desc_not_in_group.append(info["description"])
        # fig_in_group = get_bert_topic(desc_in_group)
        # fig_not_in_group = get_bert_topic(desc_not_in_group)
        dir_path = f"results/RQ3/{os_name}_{os_arch}_{os_ver}"
        if not os.path.exists(dir_path):
                os.mkdir(dir_path)
        # 构建词典
        desc_not_in_group = [preprocess(document) for document in desc_not_in_group]
        dictionary = corpora.Dictionary(desc_not_in_group)

        # 构建词袋
        corpus = [dictionary.doc2bow(text) for text in desc_not_in_group]

        # 训练LDA模型
        ldamodel = LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)

        # 打印主题
        topics = ldamodel.print_topics(num_words=5)
        for topic in topics:
            print(topic)
        import pyLDAvis    
        import pyLDAvis.gensim_models as gensimvis
        # pyLDAvis.enable_notebook()
        vis = gensimvis.prepare(ldamodel, corpus, dictionary)
        fig_not_in_group_path = os.path.join(dir_path,"lda_llmfig_not_in_group.html")
        # pyLDAvis.display(vis,fig_in_group_path)
        pyLDAvis.save_html(vis, fig_not_in_group_path)
        # fig_in_group_path = os.path.join(dir_path,"fig_in_group.png")
        # fig_not_in_group_path = os.path.join(dir_path,"fig_not_in_group.png")
        llmfig_in_group_path = os.path.join(dir_path,"lda_llmfig_in_group.png")
        llmfig_not_in_group_path = os.path.join(dir_path,"lda_llmfig_not_in_group.png")
        # fig_in_group.write_image(fig_in_group_path)
        # fig_not_in_group.write_image(fig_not_in_group_path)
        # llmfig_in_group.write_image(llmfig_in_group_path)
        # llmfig_not_in_group.write_image(llmfig_not_in_group_path)

        
            
        

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
    ]
    RQ3(os_versions,False)