# coding: utf-8
from collections import defaultdict
from tqdm import tqdm
import requests
import json
import os

from depen_analyze.constant import path, count
from depen_analyze.utils import (
    js_util,
    private_analyzer,
    cdn_util,
    chrome_driver,
    base_util,
)


class JsBaseAnalyzer:
    def __init__(self):
        self.target_rank_list = [100, 1000, 10000, 20000]

    def get_third_js_ratio(
        self,
        src: str = path.DEST_JS_PATH + "all_js.json",
        dest: str = path.DEST_JS_ANALYZE_PATH + "third_js_ratio.json",
    ):
        with open(src, "r") as f:
            js_data = json.load(f)
        third_set, all_set = set(), set()
        result = {}

        for _, js_info in js_data.items():
            third_set = third_set.union(set(js_info["third"]))
            all_set = all_set.union(set(js_info["third"] + js_info["private"]))
            if int(js_info["rank"]) in self.target_rank_list:
                result[js_info["rank"]] = len(third_set) / len(all_set)

        with open(dest, "w") as f:
            json.dump(result, f, indent=2)

    def get_js_cnt_cdf(
        self,
        src: str = path.DEST_JS_PATH + "all_js.json",
        dest: str = path.DEST_JS_ANALYZE_PATH + "js_cnt_cdf.json",
    ):
        with open(src, "r") as f:
            js_data = json.load(f)
        cnt_dict = defaultdict(int)
        result = {}

        for _, js_info in js_data.items():
            cnt_dict[len(js_info["third"])] += 1

        domain_sum = 0
        cnt_dict = dict(sorted(cnt_dict.items(), key=lambda x: x[0]))
        for rank, cnt in cnt_dict.items():
            domain_sum += cnt
            result[rank] = domain_sum

        with open(dest, "w") as f:
            json.dump(result, f, indent=2)

    def get_js_concen(
        self,
        src: str = path.DEST_JS_PATH + "all_js.json",
        dest: str = path.DEST_JS_ANALYZE_PATH + "js_concen.json",
    ):
        with open(src, "r") as f:
            js_data = json.load(f)
        result = defaultdict(int)

        for _, js_info in js_data.items():
            for js_url in js_info["third"]:
                result[js_url] += 1

        result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
        with open(dest, "w") as f:
            json.dump(result, f, indent=2)

    def analyze(self):
        self.get_third_js_ratio()
        self.get_js_cnt_cdf()
        self.get_js_concen()


class JsReliabilityAnalyzer:
    def __init__(self):
        pass

    def get_js_host_reliability(self, js_url, priv_analyzer, obtainer, extractor):
        try:
            ns_reli = js_util.get_js_ns_redundancy_degree(priv_analyzer, js_url)
            cdn_reli = js_util.get_js_cdn_redundancy_degree(obtainer, extractor, js_url)
            https_reli = js_util.is_js_support_https(js_url)
            ocsp_reli = js_util.is_support_ocsp_(js_url)
            return (ns_reli + cdn_reli + https_reli + ocsp_reli) / 4
        except:
            return 0

    def get_js_trans_reliability(self, resp):
        try:
            x_xss_protection_reli = js_util.get_x_xss_protection_score(resp)
            csp_reli = js_util.get_content_security_policy_score(resp)
            x_content_type_reli = js_util.get_x_content_type_score(resp)
            return (x_xss_protection_reli + csp_reli + x_content_type_reli) / 3
        except:
            return 0

    def get_js_code_reliability(self, resp):
        try:
            outdated_js_api_score = js_util.get_outdated_js_api_score(resp)
            # return 1 - outdated_js_api_score
            return 0 - outdated_js_api_score
        except:
            return 0

    def get_js_self_reliability(self, driver, url, js_url):
        try:
            score = js_util.get_js_dom_change_score(driver, url, js_url)
            return score
        except:
            return 0

    def get_all_js_self_reliability(self, driver, all_js):
        all_js_dom_change_score = {}  # {js_url: [ domain_cnt, score_sum ]}
        with tqdm(total=len(all_js)) as pbar:
            pbar.set_description("get js self reliability")
            for domain, js_info in all_js.items():
                for js_url in js_info["third"]:
                    if js_url not in all_js_dom_change_score:
                        all_js_dom_change_score[js_url] = [0, 0]
                        dom_score = self.get_js_self_reliability(
                            driver, "http://" + domain, js_url
                        )
                    all_js_dom_change_score[js_url][0] += 1
                    all_js_dom_change_score[js_url][1] += dom_score
                pbar.update(1)

        for key, score_list in all_js_dom_change_score.items():
            all_js_dom_change_score[key] = score_list[1] / score_list[0]
        return all_js_dom_change_score

    def get_js_reliability(
        self,
        all_js_src=path.DEST_JS_PATH + "all_js.json",
        js_score_src=path.DEST_JS_PATH + "js_score.json",
        dest=path.DEST_JS_ANALYZE_PATH + "all_js_reliability.json",
    ):
        try:
            with open(js_score_src, "r") as f:
                all_js_score = json.load(f)
            priv_analyzer = private_analyzer.PrivateAnalyzer()
            obtainer = cdn_util.InternalUrlObtainer()
            extractor = cdn_util.CdnExtractor()
            driver = chrome_driver.get_driver()
        except:
            return

        with tqdm(total=len(all_js_score)) as pbar:
            pbar.set_description("get js reliablity")
            for js_url, _ in all_js_score.items():
                host_reli = self.get_js_host_reliability(
                    js_url, priv_analyzer, obtainer, extractor
                )
                try:
                    resp = requests.get(js_url)
                    if resp.status_code == 200:
                        trans_reli = self.get_js_trans_reliability(resp)
                        code_reli = self.get_js_code_reliability(resp)
                except:
                    pass
                # all_js_score[js_url] = (host_reli + trans_reli + 0.5*code_reli) / 3
                score = 0.6 * host_reli + 0.1 * trans_reli + 0.3 * code_reli
                # print(js_url, score)
                all_js_score[js_url] = score
                pbar.update(1)

        # try:
        #     with open(all_js_src, "r") as f:
        #         all_js = json.load(f)
        #     all_js_self_reli = self.get_all_js_self_reliability(driver, all_js)
        # except:
        #     all_js_self_reli = {}

        # if not all_js_self_reli:
        #     return all_js_score

        # for js_url, score in all_js_score.items():
        #     if js_url in all_js_self_reli:
        #         all_js_score[js_url] = (score + all_js_self_reli[js_url]) / 2
        return all_js_score

    def analyze(
        self,
        all_js_src=path.DEST_JS_PATH + "all_js.json",
        js_score_src=path.DEST_JS_PATH + "js_score.json",
        dest=path.DEST_JS_ANALYZE_PATH + "all_js_reliability.json",
    ):
        all_js_reliability = self.get_js_reliability(all_js_src, js_score_src, dest)
        with open(dest, "w") as f:
            json.dump(all_js_reliability, f, indent=2)


def get_all_ns(src: str, dest: str, start: int = 1) -> None:
    result = {}
    priv_analyzer = private_analyzer.PrivateAnalyzer()
    with open(src, "r") as f:
        js_data = json.load(f)
    with tqdm(total=len(js_data)) as pbar:
        pbar.set_description("get all ns of js")
        for rank, js_url in js_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            private, third = js_util.get_js_ns(priv_analyzer, js_url)
            result[js_url] = {
                "rank": rank,
                "private" : private,
                "third": third
            }
            if int(rank) % 100 == 0:
                filename = f"{dest}ns_start{start}_end{rank}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
    if not os.path.exists(dest):
        os.makedirs(dest)
    dest_filename = f"{dest}ns_start{start}.json"
    with open(dest_filename, "w") as f:
        json.dump(result, f, indent=2)
    # base_util.notify("JS的NS获取完毕")


def get_all_cdn(src: str, dest: str, start: int = 1) -> None:
    result = {}
    obtainer = cdn_util.InternalUrlObtainer()
    extractor = cdn_util.CdnExtractor()
    with open(src, "r") as f:
        js_data = json.load(f)
    with tqdm(total=len(js_data)) as pbar:
        pbar.set_description("get all cdn of js")
        for rank, js_url in js_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            cdns = js_util.get_js_cdn(obtainer, extractor, js_url)
            result[js_url] = {
                "rank": rank,
                "cdns": cdns
            }
            if int(rank) % count.STEP_SIZE == 0:
                filename = f"{dest}cdn_start{start}_end{rank}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
    if not os.path.exists(dest):
        os.makedirs(dest)
    dest_filename = f"{dest}cdn_start{start}.json"
    with open(dest_filename, "w") as f:
        json.dump(result, f, indent=2)
    # base_util.notify("JS的CDN获取完毕")


def get_all_https(src: str, dest: str, start: int = 1) -> None:
    result = {}
    with open(src, "r") as f:
        js_data = json.load(f)
    with tqdm(total=len(js_data)) as pbar:
        pbar.set_description("get https of js")
        for rank, js_url in js_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            support_https = js_util.is_js_support_https(js_url)
            support_ocsp = js_util.is_support_ocsp(js_url)
            result[js_url] = {
                "rank": rank,
                "https": support_https,
                "ocsp": support_ocsp
            }
            if int(rank) % count.STEP_SIZE == 0:
                filename = f"{dest}https_start{start}_end{rank}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
        if not os.path.exists(dest):
            os.makedirs(dest)
        dest_filename = f"{dest}https_start{start}.json"
        with open(dest_filename, "w") as f:
            json.dump(result, f, indent=2)
    # base_util.notify("JS的HTTPS获取完毕")


def get_trans(src: str, dest: str, start: int) -> None:
    result = {}
    with open(src,"r") as f:
        js_data = json.load(f)
    with tqdm(total=len(js_data)) as pbar:
        for rank, js_url in js_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            try:
                resp = requests.get(js_url)
                if resp.status_code == 200:
                    x_xss = js_util.get_x_xss_protection(resp)
                    csp = js_util.get_content_security_policy(resp)
                    x_content_type = js_util.get_x_content_type(resp)
            except:
                pass
            result[js_url]={
                "rank": rank,
                "x_xss": x_xss,
                "csp": csp,
                "x_content_type": x_content_type,
            }
            if int(rank) % count.STEP_SIZE== 0:
                filename = f"{dest}trans_start{start}_end{rank}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
    if not os.path.exists(dest):
        os.makedirs(dest)
    dest_filename = f"{dest}trans_start{start}.json"
    with open(dest_filename, "w") as f:
        json.dump(result, f, indent=2)
    # base_util.notify("JS的HTTP安全头获取完毕")


def get_eval_docwrite(src: str, dest: str, start: int) -> None:
    result = {}
    
    with open(src,"r") as f:
        js_data = json.load(f)
    with tqdm(total=len(js_data)) as pbar:
        for rank, js_url in js_data.items():
            pbar.update(1)
            if int(rank) < start:
                continue
            try:
                resp = requests.get(js_url)
                if resp.status_code == 200:
                    eval_cnt, doc_write_cnt = js_util.get_outdated_js_api(resp)
            except:
                pass
            result[js_url]={
                "rank": rank,
                "eval": eval_cnt,
                "doc_write": doc_write_cnt
            }
            if int(rank)%count.STEP_SIZE == 0:
                filename=f"{dest}eva_start{start}_end{rank}.json"
                with open(filename,"w") as f:
                    json.dump(result,f,indent=2)
    if not os.path.exists(dest):
        os.makedirs(dest)
    dest_filename = f"{dest}eval_start{start}.json"
    with open(dest_filename, "w") as f:
        json.dump(result, f, indent=2)
    # base_util.notify("JS的eval获取完毕")


def get_dependency(src: str, dest: str, start: int):
    result={}
    driver = chrome_driver.get_driver()
    with open(src, "r") as f:
        data = json.load(f)
    with tqdm(total=len(data)) as pbar:
        pbar.set_description("get js dependency")
    for rank, domain in data.items():
        info = {
            "rank": rank,
            "has_cycle": False,
            "weights": {}
        }
        root_url = ""
        try:
            har = js_util.get_har_log(driver, domain)
            initiators = js_util.get_initiators(har)
            for item_ in initiators:
                for url in item_:
                    if not url.endswith(".js"):
                        root_url = url
                        break
            if not root_url:
                if int(rank) % count.STEP_SIZE == 0:
                    filename=f"{dest}js_depen{start}_end{rank}.json"
                with open(filename,"w") as f:
                    json.dump(result,f,indent=2)
                result = {}
                continue

            root_node = js_util.Node(root_url)
            edges = js_util.get_edges(initiators)
            visited = [False] * len(edges)
            has_cycle = False
            node_set = set([root_url])

            js_util.build_tree(root_node, edges, visited, node_set)
            weights = js_util.get_node_weight(root_node)
            weights = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
            info["has_cycle"] = has_cycle
            info["weights"] = weights
            result[domain] = info

            if int(rank) % count.STEP_SIZE == 0:
                filename=f"{dest}js_depen{start}_end{rank}.json"
                with open(filename,"w") as f:
                    json.dump(result,f,indent=2)
                result = {}
        except Exception as e:
            raise(e)
        finally:
            filename=f"{dest}js_depen_error{start}_end{rank}.json"
            with open(filename,"w") as f:
                json.dump(result,f,indent=2)
                