from py2neo import *
from pyvis.network import Network

class GetAnswer:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))

    def get_data(self, index, param):
        query = ''
        if index == 0:
            # 某人写过什么诗
            query = "MATCH (a:Author)-[:Author_THE_Poem]->(p:Poem) WHERE a.name='{}' RETURN p.name;".format(param)
        elif index == 1:
            # 某诗是某人写的
            query = "MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author) WHERE p.name='{}' RETURN a.name;".format(param)
        elif index == 2:
            # 某朝代有哪些诗人
            query = "MATCH (d:Dynasty)-[:Dynasty_THE_Author]->(a:Author) WHERE d.name='{}' RETURN a.name;".format(param)
        elif index == 3:
            # 某诗人生活在哪个朝代
            query = "MATCH (a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) WHERE a.name='{}' RETURN d.name;".format(param)
        elif index == 4:
            # 按诗名查询某诗内容
            query = "MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) " \
                    "WHERE p.name='{}' RETURN p.name,d.name,a.name,p.content;".format(param)
        elif index == 5:
            # 某诗属于某风格
            query = "MATCH (p:Poem)-[:Poem_IS_Tag]->(t:Tag) WHERE p.name='{}' RETURN t.name;".format(param)
        elif index == 6:
            # 某诗句出自某朝代某诗人写作的某诗
            query = "MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) " \
                    "WHERE p.content=~'.*{}.*' RETURN d.name,a.name,p.name, p.content;".format(param)
        result = self.graph.run(query).data()
        return result

    def generate_cypher_query(self, index, param):
        """
        根据索引和参数生成对应的 Cypher 查询
        """
        if index == 0:
            return f"MATCH (a:Author)-[:Author_THE_Poem]->(p:Poem) WHERE a.name='{param}' RETURN a, p"
        elif index == 1:
            return f"MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author) WHERE p.name='{param}' RETURN p, a"
        elif index == 2:
            return f"MATCH (d:Dynasty)-[:Dynasty_THE_Author]->(a:Author) WHERE d.name='{param}' RETURN d, a"
        elif index == 3:
            return f"MATCH (a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) WHERE a.name='{param}' RETURN a, d"
        elif index == 4:
            return f"MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) " \
                   f"WHERE p.name='{param}' RETURN d, a, p"
        elif index == 5:
            return f"MATCH (p:Poem)-[:Poem_IS_Tag]->(t:Tag) WHERE p.name='{param}' RETURN p, t"
        elif index == 6:
            return f"MATCH (p:Poem)-[:Poem_IS_Author]->(a:Author)-[:Author_IS_Dynasty]->(d:Dynasty) " \
                   f"WHERE p.content=~'.*{param}.*' RETURN d, a, p"
        else:
            return None

    def generate_knowledge_graph(self, cypher_query, output_file):
        """
        使用Cypher查询生成知识图谱并保存为HTML文件
        """
        # 执行Cypher查询
        result = self.graph.run(cypher_query).data()

        # 创建一个PyVis网络对象
        net = Network(height="1000px", width="100%", bgcolor="#F4F8F7", font_color="black")

        # 用来存储已添加的节点和边，避免重复
        added_nodes = set()
        added_edges = set()

        for record in result:
            # 遍历返回的每一行数据（字典）
            nodes = {}  # 存储当前记录中的节点
            for key, value in record.items():
                if isinstance(value, Node):
                    # 获取节点标签和属性
                    label = list(value.labels)[0]
                    name = value.get("name", f"{label}-{key}")  # 使用 "name" 属性或一个默认值
                    if name not in added_nodes:  # 避免重复添加节点
                        net.add_node(name, label=f"{label}: {name}", title=f"{label}: {name}")
                        added_nodes.add(name)
                    nodes[key] = name  # 存储节点名称以便创建边

            # 生成边（关系）
            if len(nodes) > 1:  # 至少两个节点才能形成边
                keys = list(nodes.keys())
                for i in range(len(keys) - 1):
                    start_node = nodes[keys[i]]
                    end_node = nodes[keys[i + 1]]
                    edge_key = (start_node, end_node)  # 唯一标识边
                    if edge_key not in added_edges:  # 避免重复添加边
                        net.add_edge(start_node, end_node, title="Linked")  # 可定制边的标题
                        added_edges.add(edge_key)

        # 设置物理模拟参数来优化布局
        net.set_options("""
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -20000,
              "centralGravity": 1,
              "springLength": 60,
              "springConstant": 0.001,
              "damping": 0.09
            },
            "maxVelocity": 146,
            "minVelocity": 0.1,
            "solver": "barnesHut",
            "timestep": 0.3,
            "stabilization": {
              "enabled": true,
              "iterations": 1000,
              "fit": true
            }
          }
        }
        """)

        # 将PyVis网络对象保存为HTML文件
        net.save_graph(output_file)
if __name__ == "__main__":
    ga = GetAnswer()
    answers = ga.get_data(0, '李白')
    for answer in answers:
        print(answer)
