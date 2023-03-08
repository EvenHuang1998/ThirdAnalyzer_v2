#coding: utf-8
from depen_analyze.utils import data_reader, base_util, ca_util

class PrivateAnalyzer:
    '''
        根据sld、san、soa判断某个other是否为私有提供商
        执行的前提是要求ca和soa数据都存在
    '''
    def __init__(self):
        '''初始化,要求soa和ca数据存在'''
        self.ca_dict = data_reader.load_ca()
        self.soa_dict = data_reader.load_soa()
    
    def find_soa(self, domain):
        '''读取soa,不存在则在线查询'''
        if domain in self.soa_dict:
            return self.soa_dict[domain]
        else:
            return base_util.get_soa(domain)

    def find_san(self, domain):
        '''从ca数据中获取san信息'''
        san = []
        if domain in self.ca_dict:
            return self.ca_dict[domain]["san"]
        else:
            context = ca_util.ssl_ctx()
            hostname = "www." + domain
            ca = ca_util.get_ca(context, hostname)
            if ca:
                san = ca_util.get_san(ca)
            return san

    def is_other_private(self, domain, other):
        '''根据sld、san、soa判断某个other是否为私有提供商'''
        sld_domain = base_util.extract_sld(domain)
        sld_other = base_util.extract_sld(other)
        if sld_domain and sld_other and sld_domain == sld_other:
            return True

        san = self.find_san(domain)
        if base_util.is_sld_in_san(sld_other, san):
            return True

        soa_domain = self.find_soa(sld_domain)
        soa_other = self.find_soa(sld_other)
        if soa_domain and soa_other and soa_domain == soa_other:
            return True

        return False