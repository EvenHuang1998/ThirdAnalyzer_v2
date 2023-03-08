#coding: utf-8
from tqdm import tqdm
import json
import os

from depen_analyze.utils import data_reader, ns_util, private_analyzer
from depen_analyze.constant import count

def get_ns_data(src: str = "./data/domain_rank.json", dest: str = "./result/infra/ns/", step_size = count.STEP_SIZE, start = 0, end = count.DOMAIN_CNT, step_save = False):
    '''
        获取所有的ns相关基础信息,并存储为json格式
        数据格式如下：
        {
            "example.com":{
                "rank": 1,
                "private": [],
                "third": []
            }
        }
    '''
    if not os.path.exists(dest):
        os.makedirs(dest)

    priv_analyzer = private_analyzer.PrivateAnalyzer()
    rank_data = data_reader.load_data(src)

    all_ns = {}
    all_ns_set = set()
    all_ns_set_filename = "{path}all_ns_set.json".format(path=dest)
    try:
        with open(all_ns_set_filename, "r") as f:
            ns_set = json.load(f)
            all_ns_set = set(ns_set["ns_set"])
    except:
        pass

    with tqdm(total = len(rank_data)) as pbar:
        pbar.set_description("get ns data")
        for rank, domain in rank_data.items():

            if int(rank) < start :
                continue
            if int(rank) > end:
                break
            pbar.update(1)
            domain_ns_info = {
                "rank": rank,
                "private": [],
                "third": []
            }

            ns_urls = ns_util.get_ns(domain)
            ns_set = ns_set.union(ns_urls)
            if not ns_urls:
                continue
            ns_entities = ns_util.divide_ns_entity(ns_urls)
            for entity in ns_entities: #entity是ns的url
                ns_provider = ns_util.get_ns_provider(entity)
                if priv_analyzer.is_other_private(domain, entity):
                    domain_ns_info["private"].append(ns_provider)
                else:
                    domain_ns_info["third"].append(ns_provider)

            all_ns[domain] = domain_ns_info

            if step_save:
            # 每100条数据保存一次
                if int(rank)%step_size == 0:
                    filename = "{path}top_{rank}.json".format(path = dest, rank = rank)
                    with open(filename, "w") as f:
                        json.dump(all_ns, f, indent = 2)
                    all_ns = {}
    
        if not step_save:
            filename = "{path}all_ns.json".format(path=dest)
            with open(filename, "w") as f:
                json.dump(all_ns, f, indent=2)
            with open(all_ns_set_filename, "w") as f:
                json.dump({"ns_set": list(all_ns_set)}, f, indent=2)
            return all_ns
