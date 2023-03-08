#coding: utf-8
from depen_analyze.utils import base_util

def test_combine_results(src, dest, total_cnt, step_size):
    base_util.combine_results(src, dest, total_cnt, step_size)

if __name__ == "__main__":
    test_combine_results("./result/loading/", "./result/loading/all_js.json",
    total_cnt=6300, step_size=100)