#coding: utf-8
from depen_analyze.utils import ca_util
from depen_analyze.get_data import ca_data

def test_ctx():
    ca_util.ssl_ctx()

def test_get_ca():
    ca_data.get_ca_data()

if __name__ == "__main__":
    # test_ctx()
    test_get_ca()