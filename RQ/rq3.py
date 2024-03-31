"""
对组内的pkg和组外的pkg进行主题建模, 利用了Llama大语言模型，
"""
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
from huggingface_hub import notebook_login
import transformers
from umap import UMAP
from hdbscan import HDBSCAN
from torch import bfloat16


logger = get_logger(__name__)

def get_bert_topic(sentences):
    topic_model = BERTopic(language="english", calculate_probabilities=False, verbose=True)
    topics, probs = topic_model.fit_transform(sentences)
    freq = topic_model.get_topic_info()
    logger.info(freq.head(5))
    logger.info(topic_model.get_topic(0))
    fig = topic_model.visualize_topics()
    return fig


def get_bert_llama_topic(sentences):
    model_id = 'meta-llama/Llama-2-7b-chat-hf'
    device = f'cuda:0'
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,  # 4-bit quantization
        bnb_4bit_quant_type='nf4',  # Normalized float 4
        bnb_4bit_use_double_quant=True,  # Second quantization after the first
        bnb_4bit_compute_dtype=bfloat16  # Computation type
    )
    # Llama 2 Tokenizer
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)
    # Llama 2 Model
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        quantization_config=bnb_config,
        device_map='auto',
    )
    model.eval()
    # Our text generator
    generator = transformers.pipeline(
        model=model, 
        tokenizer=tokenizer,
        task='text-generation',
        temperature=0.1,
        max_new_tokens=500,
        repetition_penalty=1.1
    )
    system_prompt = """
    <s>[INST] <<SYS>>
    You are a helpful, respectful and honest assistant for labeling topics.
    <</SYS>>
    """
    example_prompt = """
    I have a topic that contains the following documents:
    - Traditional diets in most cultures were primarily plant-based with a little meat on top, but with the rise of industrial style meat production and factory farming, meat has become a staple food.
    - Meat, but especially beef, is the word food in terms of emissions.
    - Eating meat doesn't make you a bad person, not eating meat doesn't make you a good one.

    The topic is described by the following keywords: 'meat, beef, eat, eating, emissions, steak, food, health, processed, chicken'.

    Based on the information about the topic above, please create a short label of this topic. Make sure you to only return the label and nothing more.

    [/INST] Environmental impacts of eating meat
    """
    main_prompt = """
    [INST]
    I have a topic that contains the following documents:
    [DOCUMENTS]

    The topic is described by the following keywords: '[KEYWORDS]'.

    Based on the information about the topic above, please create a short label of this topic. Make sure you to only return the label and nothing more.
    [/INST]
    """
    prompt = system_prompt + example_prompt + main_prompt
    # Pre-calculate embeddings
    embedding_model = SentenceTransformer("BAAI/bge-small-en")
    embeddings = embedding_model.encode(sentences, show_progress_bar=True)
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=150, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    # Pre-reduce embeddings for visualization purposes
    reduced_embeddings = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine', random_state=42).fit_transform(embeddings)
    # KeyBERT
    keybert = KeyBERTInspired()
    # MMR
    mmr = MaximalMarginalRelevance(diversity=0.3)
    # Text generation with Llama 2
    llama2 = TextGeneration(generator, prompt=prompt)
    # All representation models
    representation_model = {
        "KeyBERT": keybert,
        "Llama2": llama2,
        "MMR": mmr,
    }
    topic_model = BERTopic(
        # Sub-models
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        representation_model=representation_model,
        # Hyperparameters
        top_n_words=10,
        verbose=True
    )
    # Train model
    topics, probs = topic_model.fit_transform(sentences, embeddings)
    # Show topics
    freq = topic_model.get_topic_info()
    logger.info(freq.head(5))
    logger.info(topic_model.get_topic(1, full=True)["KeyBERT"])
    llama2_labels = [label[0][0].split("\n")[0] for label in topic_model.get_topics(full=True)["Llama2"].values()]
    topic_model.set_topic_labels(llama2_labels)
    fig = topic_model.visualize_documents(reduced_embeddings)
    return fig





def RQ3(os_arch_ver,override=False):
    metas = load_file('./os_urls.json')
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
        logger.info("------------RQ3:bert-topic----------------")
        pkg_in_group = []
        for group,info in all_groups.items():
            for pkg in info["packagelist"]:
                pkg_in_group.append(pkg)
        desc_in_group = []
        desc_not_in_group = []
        for pkg,info in all_pkgs.items():
            if pkg in pkg_in_group:
                if info["description"] is not None:
                    desc_in_group.append(info["description"])
            else:
                if info["description"] is not None:
                    desc_not_in_group.append(info["description"])
        fig_in_group = get_bert_topic(desc_in_group)
        fig_not_in_group = get_bert_topic(desc_not_in_group)
        llmfig_in_group = get_bert_llama_topic(desc_in_group)
        llmfig_not_in_group = get_bert_llama_topic(desc_not_in_group)
        dir_path = f"results/RQ3/{os_name}_{os_arch}_{os_ver}"
        fig_in_group_path = os.path.join(dir_path,"fig_in_group.png")
        fig_not_in_group_path = os.path.join(dir_path,"fig_not_in_group.png")
        llmfig_in_group_path = os.path.join(dir_path,"llmfig_in_group.png")
        llmfig_not_in_group_path = os.path.join(dir_path,"llmfig_not_in_group.png")
        fig_in_group.write_image(fig_in_group_path)
        fig_not_in_group.write_image(fig_not_in_group_path)
        llmfig_in_group.write_image(llmfig_in_group_path)
        llmfig_not_in_group.write_image(llmfig_not_in_group_path)

        
            
        

if __name__=="__main__":
    os_versions = [
        ("fedora", "x86_64", "38"),
        ('fedora', 'aarch64', '38'),
    ]
    RQ3(os_versions,False)