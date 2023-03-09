class Node:
    def __init__(self, value: str) -> None:
        self.value = value
        self.children = []

def build_tree(root: Node, edges: list, visited: list, node_set: set) -> Node:
    node_start = False
    global has_cycle
    for i in range(0, len(visited)):
        if visited[i]:
            continue
        if node_start and edges[i][0] != root.value:
            break
        if edges[i][0] == root.value:
            if edges[i][1] in node_set:
                has_cycle = True
                # break
            node_start = True
            visited[i] = True
            child = Node(edges[i][1])
            root.children.append(child)
            node_set.add(child.value)
            build_tree(child, edges, visited, node_set)

def get_edges(initiators: list)->list:
    edges = []
    for ini_item in initiators:
        for i in range(0, len(ini_item)-1):
            edges.append([ini_item[i],ini_item[i+1]])
    return edges

def traverse(tree: Node, weights: dict) -> int:
    node_weight = 0
    for child in tree.children:
        if not child.children:
            child_node_weight = 1
        else:
            child_node_weight = 1 + traverse(child, weights)
        # if child.value in weights:
        #     weights[child.value] = max(weights[child.value], child_node_weight)
        # else:
        #     weights[child.value] = child_node_weight
        weights[child.value] = child_node_weight
        node_weight += child_node_weight
    weights[tree.value] = node_weight
    return node_weight

def get_node_weight(tree: Node) -> dict:
    weights = {}
    traverse(tree, weights)
    return weights

if __name__ == "__main__":
    root = Node("https://www.baidu.com/")
    initiators = [['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://www.baidu.com/',
              'https://pss.bdstatic.com/r/www/cache/static/protocol/https/bundles/es6-polyfill_5645e88.js'],
             ['https://www.baidu.com/',
              'https://pss.bdstatic.com/r/www/cache/static/protocol/https/bundles/polyfill_9354efa.js'],
             ['https://www.baidu.com/',
              'https://pss.bdstatic.com/r/www/cache/static/protocol/https/global/js/all_async_search_7000885.js'],
             ['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js'],
             ['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/s_super_index-3fffae8d60.js'],
             ['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/min_super-aad56eb874.js'],
             ['https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/components/hotsearch-5af0f864cf.js'],
             ['https://www.baidu.com/',
              'https://hectorstatic.baidu.com/cd37ed75a9387c5b.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://pss.bdstatic.com/r/www/cache/static/protocol/https/global/js/all_async_search_7000885.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://pss.bdstatic.com/r/www/cache/static/protocol/https/global/js/all_async_search_7000885.js'],
             ['https://pss.bdstatic.com/r/www/cache/static/protocol/https/soutu/js/tu_4c09212.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://pss.bdstatic.com/r/www/cache/static/protocol/https/amd_modules/@baidu/search-sug_d74c14f.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://www.baidu.com/',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/min_super-aad56eb874.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/min_super-aad56eb874.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/min_super-aad56eb874.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://hectorstatic.baidu.com/cd37ed75a9387c5b.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/components/qrcode-0e4b67354f.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js',
              'https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/jquery-1-edb203c114.10.2.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/lib/esl-d776bfb1aa.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js'],
             ['https://dss0.bdstatic.com/5aV1bjqh_Q23odCf/static/superman/js/sbase-829e78c5bb.js']]
    edges = get_edges(initiators)
    # edges = [["baidu.com", "a"],["baidu.com", "b"], ["a","c"],["a","d"],["d","b"]]
    visited = [False] * len(edges)
    node_set = set(["https://www.baidu.com/"])
    has_cycle = False
    build_tree(root, edges, visited, node_set)
    weights = get_node_weight(root)
    weights = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
    print(has_cycle)
    print(weights)