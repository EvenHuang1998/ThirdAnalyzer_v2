#coding: utf-8
from depen_analyze.get_data import soa_data, ns_data, ca_data, js_data
from depen_analyze.utils import base_util
from depen_analyze.constant import path, count

def initialize(src:str = path.SRC_PATH, soa_path = path.DEST_SOA_PATH, ca_path = path.DEST_CA_PATH):
    print("initializing...")
    soa_data.get_soa_data(src = src, dest = soa_path)
    # ca_data.get_ca_data(src = src, dest = ca_path)

def get_data():
    pass

def default_measure():
    pass

class InfraAnalyzer:
    def __init__(self, need_init = False) -> None:
        if need_init:
            initialize()

    def get_data(self):
        '''获取所有数据,包含基础数据及private和third信息的表格'''
        all_ns_data = ns_data.get_ns_data()
        all_ca_data = ca_data.get_ca_data()
        # all_cdn_data = cdn_data.get_cdn_data()

        return all_ns_data, all_ca_data

    def analyze(self):
        '''根据获取的数据进行分析,包括基本分析、集中度分析等等'''
        pass

    def plot(self):
        pass

    def run(self, step_size = count.STEP_SIZE):
        self.get_data(step_size)

class LoadingAnalyzer:
    def __init__(self, need_init) -> None:
        if need_init:
            initialize()

    def get_data(self, src = path.SRC_PATH, dest = path.DEST_JS_PATH, step_size = count.STEP_SIZE):
        js_data.get_js_data(src, dest, step_size)

    def run(self, src = path.SRC_PATH, dest = path.DEST_JS_PATH, step_size = count.STEP_SIZE):
        self.get_data(src, dest, step_size)
        # base_util.combine_results(src = "./result/loading/", dest = "./result/loading/all_js.json")