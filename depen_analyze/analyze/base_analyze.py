#coding: utf-8
import json
import os

from depen_analyze.constant import path

class js_analyzer:
    def __init__(self, src = path.DEST_JS_PATH+"all_js.json", dest = path.DEST_JS_ANALYZE_PATH) -> None:
        print("初始化")
        self.dest = dest
        
        if not os.path.exists(self.dest):
            os.makedirs(self.dest)
        
        try:
            with open(src, "r") as f:
                self.all_js = json.load(f)
        except:
            print("all_js.json文件不存在")

    def third_js_ratio(self):
        result = {
            "100": {
                "no_data":0,
                "third":0,
                "private":0
            },
            "1000": {
                "no_data":0,
                "third":0,
                "private":0
            },
            "10000": {
                "no_data":0,
                "third":0,
                "private":0
            },
            "20000": {
                "no_data": 0,
                "third": 0,
                "private": 0
            },
        }
        third_cnt, no_data_cnt = 0, 0
        for domain, js_info in self.all_js.items():
            if not js_info["third"] and not js_info["private"]:
                no_data_cnt += 1
            if js_info["third"]:
                third_cnt += 1
            rank = js_info["rank"]
            if rank in result.keys():
                result[rank]["no_data"] = no_data_cnt/int(rank)
                result[rank]["third"] = third_cnt/int(rank)
                result[rank]["private"] = (int(rank) - no_data_cnt - third_cnt)/int(rank)
        with open(self.dest+"third_ratio.json", "w") as f:
            json.dump(result, f, indent=2)