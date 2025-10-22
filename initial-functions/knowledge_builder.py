from dotenv import load_dotenv
load_dotenv("../.env")
import os
import json
from pathlib import Path
from pyecharts.charts import Graph
from pyecharts import options as opts
from pyecharts.render import make_snapshot
# from snapshot_selenium import snapshot as driver
from snapshot_phantomjs import snapshot as driver


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

    def build_graphs(self, records_data: list[dict], top_k: int = 20) -> str:
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

    import json

    def main(arg1: list[str]):
        rag_set, search_set = set(), set()

        for line in arg1:
            load_line = json.loads(line)
            search_chunks = [f"title: {result['title']}\ncontent: {result['content']}" for result in load_line["search"]["results"]]
            search_set.update(search_chunks)
            rag_set.update(load_line["rag_chunks"])

        return {
            "rag_result": list(rag_set),
            "search_result": list(search_set)
        }


    {
        "result": "{\"rag_chunks\": [\"车次功能号呼叫方法:可以用车次功能号呼叫 CIR 来确认车次功能号确认成 功注册。按车次号呼叫 CIR 的方法为:\", \"CIR 数据功能系统示意图\", \"7.7.6 CIR** 无法上电\", \"启 **CIR** 之后才生效。\\ne) 归属 GRIS IP\"], \"search_chunks\": \"[{'Uuid': '3dd75e73-438e-4e9e-893c-fba4fae6863b', 'query': 'CIR车次功能号注册失败', 'results': [{'content': '车次功能号注册或注销失败,CIR自动进行再注册或注销,间隔为5至30秒,不超过( )次。A. 2 B. 3 C. 4 D. 5 答案:B', 'date': '2025-08-23 22:23:13', 'score': 0.8941763775800844, 'title': '车次功能号注册或注销失败,CIR自动进行再注册或注销,间隔为5至30秒,不超过( )次。', 'url': 'https://aistudy.baidu.com/site/wjzsorv8/8cd47d9a-7797-42f3-9306-b902ded71161?botSourceType=124&eduFrom=196&examQuestionId=PtxRWek4CHV4HnsEpPxsFw'}, {'content': \\\"CIR设备在进出GSM-R区段不能自动注册或注销时要手动注册或注销｡遇CIR手动注册车次号不成功时,司机应使用GSM-R手持终端报告车站值班员(列车调度员),使用GSM-R手持终端进行通话() 热门试题 注册车次号不成功的处理要求有｡{ 在CIR电台正常工作的情况下,GSM-R手持终端注册车次号输入功能码必须输入81(即本务司机手持台),在CIR电台故障时,该功能号方可输入(即本务司机主机)() CIR在司机手动注册车次号时,或列车进入GSM-R工作模式区段后,如果出现CIR扬声器语音提示'车次号注册失败',表示CIR向GSM-R网络注册当前车次号失败｡\\\", 'date': '2024-12-24 02:57:51', 'score': 0.8843767801736606, 'title': '遇CIR注册车次号不成功时,司机应使用GSM-R手持终端报告车站值班员,使用GS-e考试网', 'url': 'https://www.eepw.com/shiti/ckpuvdivaxyc.html'}, {'content': \\\"判断题】 GSM-R 工作模式时,车次号注册不成功 如果出现'车次号注册失败'的提示,请按以下步骤进行检查及操作｡首先确认 CIR 屏幕左上角显示的车次号: 如果车次号不正确,请输入正确的车次号并注册; 如果车次号正确,请呼叫调度员并报告 ' XXX 次列车车次号注册失败',然后按调度员指示行车,同时机车乘务员应及时向维修人员报告｡ A. 正确 B. 错误 参考答案: A 复制 纠错 举一反三 \\\", 'date': '2025-09-20 19:23:15', 'score': 0.8704565980570484, 'title': 'GSM-R 工作模式时,车次号注册不成功 如果出现“车次号注册失败”的提示,请按-刷刷题APP', 'url': 'https://www.shuashuati.com/ti/adfb3e3db1dd4641b5b00a30a38140c5.html?fm=3719e7bd0120fc2e07204bbd183223a6'}, {'content': '遇CIR注册车次号不成功时,司机应使用手机报告车站值班员(列车调度员),使用手机进行通话。/*《行细》第17条*/A. 正确 B. 错误 答案:B', 'date': '2025-08-24 01:25:33', 'score': 0.8639191594548821, 'title': '遇CIR注册车次号不成功时,司机应使用手机报告车站值班员(列车调度员),使用手机进行通话。/*《行细》第17条*/', 'url': 'https://aistudy.baidu.com/site/wjzsorv8/8cd47d9a-7797-42f3-9306-b902ded71161?botSourceType=124&eduFrom=196&examQuestionId=jEq0x5SkNFMeXFzj8_MaHg'}, {'content': \\\"《行细》第17条() 列车在GSM-R区段运行时,司机应选定CIR通信模式为GSM-R,并在CIR设备操作显示终端正确注册车次功能号,确认车次功能号注册成功｡{ CIR在司机手动注册车次号时,或列车进入GSM-R工作模式区段后,如果出现CIR扬声器语音提示'车次号注册失败',表示CIR向GSM-R网络注册当前车次号失败｡() 车次功能号成功后,其他用户使用车次功能号呼叫到该CIR() 列车在GSM-R区段运行时,司机应选定CIR通信模式为GSM-R,并在CIR设备操作显示终端正确注册车次功能号,确认_注册成功 当CIR处于车次功能号注册成功状态时,获得TAX装置由监控状态进入非监控状态信息时,则自动进行车次功能号注销() 观察MMI上出现'车次号注册成功'字样,听到提示音'车次号注册成功',同时车次号字体变为黄色,说明车次号注册成功() 手机银行注册成功的可以使用手机号､昵称登录,不可以使用卡号登录() 遇列车折返不成功时,司机必须汇报行调,得到命令后,确认地面信号开放后方可动车｡\\\", 'date': '2025-01-19 23:59:16', 'score': 0.8528738993220495, 'title': '遇CIR注册车次号不成功时,司机应使用手机报告车站值班员(列车调度员),使用手机-e考试网', 'url': 'https://www.jutiku.cn/shiti/dg1usjityaai.html'}, {'content': \\\"如果CIR工作在GSM-R模式下,车次号和机车号注册成功,CIR各项设置无误,天馈系统正常,但无法获取本机IP,首先应定位CIR的出现故障() 多选题 CIR在司机手动注册车次号时,或列车进入GSM-R工作模式区段后,如果出现CIR扬声器语音提示'车次号注册失败',表示CIR向GSM-R网络注册当前车次号失败｡ B.如果显示的车次号正确,报告调度员'XX次列车车次号注册失败'｡ C.维持运行 \\\", 'date': '2025-03-25 16:51:24', 'score': 0.8441246176529621, 'title': 'CIR车次注册错误,将无法正常签收-e考试网', 'url': 'https://www.eepw.com/shiti/mwhlmziskufs.html'}, {'content': '多选题 A. 遇CIR注册车次号不成功时,司机应报告列车调度员(车站值班员),列车调度员(车站值班员)通知通信部门处理｡ B. 自动跳转失败时,司机应报告列车调度员(车站值班员),注销原车次号,重新注册新车次号｡ C. 发现CIR设备自动提取及显示的列车车次号与实际车次不符时,应手动输入正确的车次号｡ D. 发现CIR设备自动提取及显示的列车车次号与实际车次不符时,重新注册新车次号 查看答案 该试题由用户712****84提供 查看答案人数:42725 如遇到问题请 联系客服 ', 'date': '2024-12-29 20:53:04', 'score': 0.8378357723522122, 'title': '注册车次号不成功的处理要求有。《行细》第17条()A.遇CIR注册车次号不成功时-e考试网', 'url': 'https://www.eepw.com/shiti/ddvinjitkohf.html'}, {'content': '遇CIR注册车次号不成功时,应先按压( )键3秒以上,复位CIR,重新进行注册;再次注册车次号仍不成功时,应使用GSM-R手持终端报告车站值班员(列车调度员)。 A.【主控】B.【复位】C.【设置】D.【确认/签收】', 'date': '2022-10-14 00:00:00', 'score': 0.8279682373657885, 'title': '遇CIR注册车次号不成功时,应先按压( )键3秒以上,复位CIR,重新进行注册;再次注册车次号仍不成功时,应使用GSM-R手持终端报告车站值班员(列车调度员)。', 'url': 'https://easylearn.baidu.com/edu-page/tiangong/bgkdetail?id=891f9ae89b89680203d82590&fr=search'}, {'content': 'A.遇CIR注册车次号不成功时,司机应报告列车调度员(车站值班员),列车调度员(车站值班员)通知通信部门处理。B.自动跳转失败时,司机应报告列车调度员(车站值班员),注销原车次号,重新注册新车次号。C.发现CIR设备自动提取及显示的列车车次号与实际车次不符时,应手动输入正确的车次号。D.发现CIR设备自动提取及显示的列车车次号与实际车次不符时,重新注册新车次号。', 'date': '2024-12-04 00:00:00', 'score': 0.8129753816923002, 'title': '注册车次号不成功的处理要求有()。A.遇CIR注册车次号不成功时,司机应报告列车调度员(车站值班员),列车调度员(车站值班员)通知通信部门处理。B.自动跳转失败时,司机应报告列车调度员(车站值班员),注销原车次号,重新注册新车次号。C.发现CIR设备自动提取及显示的列车车次号与实际车次不符时,应手动输入正确的车次号。D.发现CIR设备自动提取及显示的列车车次号与实际车次不符时,重新注册新车次号。-百度教育', 'url': 'https://easylearn.baidu.com/edu-page/tiangong/bgkdetail?id=7aa4bcdcaa00b52acfc7ca83&fr=search'}, {'content': \\\"</h3> <h3></h3><h3>规章依据:《动车组列控车载设备和CIR设备应急操作指南》</h3><h3>GSM—R 工作模式时车次号注册不成功</h3><h3>适用等级:GSM—R 线路｡</h3><h3>现象描述:MMI 屏幕左上方显示的车次号内容为黑色字体,并语音提示:'车次号注册失败'｡</h3><h3>操作步骤:检查确认MMI 屏幕左上角显示的车次号是否正确,如果显示的车次号不正确,按'设置'键进入设置界面,重新输入正确的车次号;如果显示的车次号正确,注册不成功,请报告调度员'XX 次列车车次号注册失败'｡</h3> <h3>规章依据:《太原铁路局集团公司高铁行细》第17条 机车综合无线通信设备注册列车车次的补充规定</h3><h3>列车在GSM-R区段运行时,开车前司机应选定CIR通信模式为GSM-R,并在CIR设备操作显示终端正确注册车次功能号,确认车次功能号注册成功｡在列车车次变化地点,车次自动跳转时,司机核对后予以确认;不能实现自动跳转时,司机应注销原车次号,重新注册新车次号｡发现CIR设备自动提取及显示的列车车次号与实际车次不符时,应手动输入正确的车次号｡</h3><h3>在动车所遇CIR注册车次号不成功时,不得出所｡\\\", 'date': '2018-12-12 01:27:43', 'score': 0.7858730758409075, 'title': '太原机务段动车微课堂---CIR注册车次不成功如何处理', 'url': 'https://www.meipian.cn/1sohszug'}]}]\"}"
    }

