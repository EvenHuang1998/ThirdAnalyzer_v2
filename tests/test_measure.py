#coding: utf-8
from depen_analyze import measure

def test_initialize():
    measure.initialize()

def test_js():
    js_analyzer = measure.LoadingAnalyzer(False)
    js_analyzer.run(step_size=100)

def test_infra():
    infra_analyzer = measure.InfraAnalyzer(False)
    infra_analyzer.run()

if __name__ == "__main__":
    # test_initialize()
    test_js()
    # test_infra()