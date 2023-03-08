#coding: utf-8
import json

from depen_analyze.constant import path

def load_data(src: str = path.SRC_PATH):
    '''加载网页排名数据'''
    try:
        with open(src, "r") as f:
            data = json.load(f)
            return data
    except:
        print("文件不存在")
        return {}

def load_ca(src: str = path.DEST_CA_PATH + "all_ca.json"):
    '''加载ca数据'''
    try:
        with open(src, "r") as f:
            ca = json.load(f)
    except:
        ca = {}
    return ca

def load_soa(src: str = "../result/soa.json"):
    try:
        with open(src, "r") as f:
            soa = json.load(f)
    except:
        soa = {}
    return soa