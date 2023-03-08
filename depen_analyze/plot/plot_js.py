# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
import json
import os

from depen_analyze.constant import path

def plot_thid_js_ratio(src=path.DEST_JS_ANALYZE_PATH,dest = path.DEST_JS_PLOT_PATH):
    # 数据处理
    with open(src+"third_ratio.json", "r") as f:
        js_ratio = json.load(f)
    x_axis = list(js_ratio.keys())
    no_data, third, private = [], [], []
    for rank, js_cnt in js_ratio.items():
        no_data.append(js_cnt["no_data"])
        third.append(js_cnt["third"])
        private.append(js_cnt["private"])
    no_data = np.array(no_data)
    third = np.array(third)
    private = np.array(private)
    
    # 图形设置
    fig, ax = plt.subplots(figsize = (6,5), dpi=100)
    width = 0.3 #设置条形图一个长条的宽度
    ax.bar(x=x_axis, height=no_data, width=width, color="white", linewidth = 1, edgecolor="black", hatch="xxx", label="no data")
    ax.bar(x=x_axis, height=third, width=width, color="grey", linewidth = 1, edgecolor="black", label="third", bottom=no_data)
    ax.bar(x=x_axis, height=private, width=width, color="white", linewidth=1, edgecolor="black", label="private", bottom=no_data+third)
    
    # 图片信息设置
    plt.xlabel("Rank")
    plt.ylabel("Ratio")
    plt.title("Ratio of Third-Party JavaScript")
    plt.ylim(0, 1)
    plt.legend(loc="upper left")
    plt.show()
