from dotenv import load_dotenv
load_dotenv("../.env")
import os
import json
from pyecharts.charts import Graph
from pyecharts import options as opts


class KnowledgeGraphBuilder:
    def __init__(self, triplets_path: str = os.getenv("TRIPLETS_PATH")):
        with open(triplets_path, "r", encoding="UTF-8") as triplets_file:
            self.triplets = [json.loads(line) for line in triplets_file.readlines()]

    def extract_relevant_records(self, entity: str, top_k: int = 20) -> list:
        relevant_list = []
        for line in self.triplets:
            if entity in line["head"] or entity in line["tail"]:
                relevant_list.append(line)
            if len(relevant_list) == top_k:
                break
        return relevant_list

    def build_graphs(self, records_data: list[dict], title: str) -> str:
        unique_nodes = set()
        for item in records_data:
            unique_nodes.add(item["head"])
            unique_nodes.add(item["tail"])

        # Build node data
        nodes_data = [
            opts.GraphNode(name=node, symbol_size=40) for node in unique_nodes
        ]

        # Build edge data
        links_data = [
            opts.GraphLink(source=item["head"], target=item["tail"], value=item["relation"])
            for item in records_data
        ]

        # Create graph
        graph = (
            Graph()
            .add(
                "",
                nodes_data,
                links_data,
                repulsion=2000,
                edge_label=opts.LabelOpts(
                    is_show=True,
                    position="middle",
                    formatter="{c}",
                    # 英文字体优先 Times New Roman，中文字体为宋体
                    font_family="Times New Roman, SimSun, serif"
                ),
                label_opts=opts.LabelOpts(
                    is_show=True,
                    font_family="Times New Roman, SimSun, serif"
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    title_textstyle_opts=opts.TextStyleOpts(
                        # 标题字体使用黑体
                        font_family="SimHei"
                    )
                )
            )
        )
        json_str = graph.dump_options_with_quotes()
        return json_str



if __name__ == '__main__':
    knowledge_graph_builder = KnowledgeGraphBuilder("../assets/triplets/triples.txt")

    knowledge_graph_builder.build_graphs("车次功能号注册",  "车次功能号注册失败", 20)

