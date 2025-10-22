import os
import json
import asyncio
from urllib.parse import unquote
from fastapi import APIRouter, Request, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from pygments.lexers import data

from endpoints.request_models import AskQuestionModel, parse_form_data, QuestionFetchImageModel, KeywordsModel
from middlewares.message_queue import global_queue
from services.dify import file_upload, dify_stream_chat

repair_qa = APIRouter()
BASE_DIR = os.getenv("STATIC_IMAGE_PATH")
BASE_IMAGE_URL = os.getenv("IMAGE_SERVER_BASE")


async def stream_generator():
    """
    异步生成器，用于SSE流式响应。
    每隔50ms轮询队列一次，直到收到'end'类型的数据才停止。
    如果队列为空，则继续轮询；如果有数据，则yield SSE格式输出。
    """
    end_received = False
    while not end_received:
        try:
            # 每50ms尝试从队列取数据（轮询机制）
            item = await asyncio.wait_for(global_queue.get(), timeout=0.05)
            type_, text = item
            # 确保text是字符串，如果为空则用空字符串
            text = text if text else ""
            if type_ == 'end':
                yield 'data: [DONE]\n\n'
                end_received = True
            elif type_ in ['think', 'plain_text', 'graph', 'table', 'images', 'echarts']:
                data = json.dumps({"type": type_, "text": text}, ensure_ascii=False)
                # 输出SSE格式，注意JSON字符串转义（简单假设text不含特殊字符，如需严格可添加json.dumps）
                yield f'data: {data}\n\n'
            else:
                # 未知类型，跳过或记录日志（这里简单跳过）
                pass
        except asyncio.TimeoutError:
            # 队列为空，继续下一轮轮询（不停止）
            pass
        except ValueError:
            # 如果item无法解包，跳过
            pass


async def fake_response():
    text = """# 🌍 智慧沙盘多模态交互系统

> 🚗🎤💡 集 **实时监控**、**智能识别**、**语音交互** 与 **多模态联动** 于一体的智慧沙盘项目

---

## 📸 项目鸟瞰图

![项目鸟瞰图](docs/image/bird%20view.jpg)

---

## 🧠 项目简介

本项目构建了一个集 **人工智能、物联网、语音识别、视觉检测与多模态交互** 于一体的智慧沙盘系统。  
系统实现了 **环境感知、语义定位、语音问询、车辆识别、联动控制** 等多种功能，  
在技术架构上兼顾了 **前沿性、稳定性与教学可用性**。

---

## 🏗️ 系统架构

![系统架构图](docs/image/structure.png)

### 🔹 架构核心思路

系统的核心目标是实现 **信息高速传递** 与 **多层数据深度融合**。  
通过 RTSP、MQTT、HTTP 等多种通信协议，实现视频、传感器、控制指令的高效交互。

---

## ⚙️ 模块说明

### 🤖 AI 模块

- **目标检测**：采用 `YOLOv8 旋转目标检测` 实现对手指与小车的实时定位。  
- **点面语义计算**：结合建筑物与道路数据，通过射线法判断点是否位于多边形内，实现语义化位置识别。  
- **车牌分类**：基于 `YOLO` 裁剪车辆区域，接入 `EfficientNet` 实现车牌识别与分类，构建智慧停车系统。  
- **语音理解与槽填充**：  
  - 使用 ASR 模型进行语音转文本  
  - LLM 进行语义理解与槽位填充  
  - 与视觉模型联动实现“手指+语音”多模态问询。

> 🗣️ 示例交互：  
> “请问一号小车在哪里？” → 系统返回「一号小车位于主干道东侧靠近教学楼入口区域」

---

### 🔌 硬件层（IoT）

基于 **ESP32 + MicroPython** 的分布式物联网系统，所有状态与控制均通过 `MQTT` 实时发布。

- 🌡️ 环境监测：温湿度、二氧化碳、PM2.5 实时上传  
- 🚦 信号灯控制：红绿灯、路灯、灯带、闸机  
- 💬 控制与反馈：状态信息与指令全双工传输  
- ⚙️ 通信协议：MQTT 提供轻量化、高可靠的数据传递机制

---

### 💻 前端可视化

采用 **Vue** 实现的大屏可视化界面，整合 YOLO、MQTT、RTSP 数据流。

- 🛰️ 实时绘制检测框，展示车辆与手指位置  
- 🛣️ 动态显示道路与红绿灯秒数  
- ☁️ 实时天气与环境信息接入  
- 📡 支持多源数据融合与状态联动显示

---

### 📱 安卓控制端

基于 **Android Studio** 开发，实现沙盘设备的便捷控制与消息交互。

- 🔔 发布与订阅 MQTT 消息  
- 💡 控制灯光与闸机  
- 🧭 接收实时设备状态与报警信息  

---

### 🚗 智能小车系统

基于 **STM32F103C8T6 + Keil5** 构建的自主巡线与交互小车：

- 🧲 磁导巡线 + 红外避障逻辑  
- 📶 外接 ESP8266 实现 MQTT 联动  
- 🪪 支持 RFID 定位与红绿灯识别  
- 🚦 可实现信号灯判定与路径规划  

---

## 🧩 系统特性

| 功能类别 | 描述 |
|-----------|------|
| 🔍 视觉识别 | YOLOv8 旋转目标检测 + 车牌识别 |
| 🗣️ 语音交互 | ASR + LLM 槽填充 + 多模态语义融合 |
| 💡 控制逻辑 | MQTT 实时指令下发与状态反馈 |
| 🌦️ 环境集成 | 温湿度、空气质量、天气信息接入 |
| 🚘 智能联动 | 红绿灯-车辆-灯光-语音全流程联动 |

---

## 🧩 技术栈总览

| 模块 | 技术 |
|------|------|
| 🎯 AI | Python, YOLOv8, OpenCV, EfficientNet |
| 🧠 NLP | ASR, Jieba, LLM, Slot Filling |
| 🌐 通信 | MQTT, RTSP, HTTP |
| 💡 硬件 | ESP32, MicroPython, DHT11, CO₂ Sensor, PM2.5 |
| 💻 前端 | Vue, ECharts, RTSP Stream, MQTT.js |
| 📱 移动端 | Android Studio, MQTT Client |
| 🚗 控制端 | STM32F103C8T6, ESP8266, RFID |

---

## 🔄 系统联动示例

```mermaid
sequenceDiagram
    participant 用户
    participant 语音模块
    participant AI视觉模块
    participant MQTT中枢
    participant 沙盘设备

    用户->>语音模块: 语音输入 “打开教学楼灯光”
    语音模块->>AI视觉模块: 槽填充 + 语义解析
    AI视觉模块->>MQTT中枢: 发布控制指令
    MQTT中枢->>沙盘设备: 执行灯光开启
    沙盘设备-->>MQTT中枢: 状态反馈
    MQTT中枢-->>前端显示: 灯光状态更新
"""
    graph = """
        {
  "title": {
    "text": "月度销售与利润分析",
    "left": "center",
    "textStyle": { "fontSize": 16, "fontWeight": "bold" }
  },
  "tooltip": {
    "trigger": "axis",
    "axisPointer": { "type": "shadow" }
  },
  "legend": {
    "data": ["销售额", "利润率"],
    "top": 30,
    "left": "center"
  },
  "grid": {
    "left": "3%",
    "right": "4%",
    "bottom": "3%",
    "containLabel": true
  },
  "xAxis": [
    {
      "type": "category",
      "data": ["1月", "2月", "3月", "4月", "5月", "6月"],
      "axisLabel": { "interval": 0 }
    }
  ],
  "yAxis": [
    {
      "type": "value",
      "name": "销售额(万元)",
      "min": 0,
      "max": 100,
      "axisLabel": { "formatter": "{value}" }
    },
    {
      "type": "value",
      "name": "利润率(%)",
      "min": 0,
      "max": 20,
      "axisLabel": { "formatter": "{value}%" },
      "splitLine": { "show": false }
    }
  ],
  "series": [
    {
      "name": "销售额",
      "type": "bar",
      "data": [65, 78, 90, 82, 95, 88],
      "itemStyle": { "color": "#5470c6" },
      "yAxisIndex": 0
    },
    {
      "name": "利润率",
      "type": "line",
      "data": [12, 15, 13, 16, 18, 17],
      "itemStyle": { "color": "#ee6666" },
      "lineStyle": { "width": 3 },
      "symbol": "circle",
      "symbolSize": 8,
      "yAxisIndex": 1
    }
  ]
}
    """

    images = ["http://gips3.baidu.com/it/u=1821127123,1149655687&fm=3028&app=3028&f=JPEG&fmt=auto?w=720&h=1280",
              "https://gips3.baidu.com/it/u=3732737575,1337431568&fm=3028&app=3028&f=JPEG&fmt=auto&q=100&size=f1440_2560"]
    await global_queue.put(('think', '正在为您生成内容'))
    await asyncio.sleep(0.1)
    await global_queue.put(("think", "内容......"))
    await asyncio.sleep(0.500)

    for i in range(0, len(text), 5):
        await global_queue.put(("plain_text", text[i:i+5]))
        await asyncio.sleep(0.05)

    await global_queue.put(("images", images))
    await asyncio.sleep(0.100)

    await global_queue.put(("echarts", graph))
    await global_queue.put(('end', ''))


@repair_qa.post("/ask", tags=["多模态图文问答"])
# async def multi_modal_ask_question(request: Request, form_data: dict = Depends(parse_form_data)):
async def multi_modal_ask_question(request: Request):
    """兼容 multipart/form-data 与 application/json"""

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        # 处理 JSON 请求
        json_data = await request.json()
        data = AskQuestionModel.model_validate(json_data)
        image_file = None
        print(json.dumps(json_data, ensure_ascii=False))
    else:
        # 处理表单请求
        form_data = await request.form()
        data, image_file = await parse_form_data(form_data)

    if image_file:
        image_file = await file_upload(image_file)
        print(image_file)

    asyncio.create_task(dify_stream_chat(data.question, data.history, image_file))
    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@repair_qa.post("/query-to-image", tags=["根据用户请求，获取最相关图片名"])
async def query_to_image(request: Request, question_model: QuestionFetchImageModel):
    image_list = await request.app.state.image_searcher.search(question_model.questions, top_k=2)
    print(image_list)
    for image_path, score in image_list:
        if score >= 0.4:
            await global_queue.put(("images", f"{BASE_IMAGE_URL}{os.path.basename(image_path)}"))
            await asyncio.sleep(0.05)
    return None


@repair_qa.post("/keywords-to-graph", tags=["根据关键字，匹配知识图谱"])
async def keywords_to_graph(request: Request, keywords_model: KeywordsModel):
    relevant_records_list = []
    llm_records_list = []
    for keyword in keywords_model.keywords:
        records = request.app.state.knowledge_graph.extract_relevant_records(keyword)
        relevant_records_list.extend(records[:20]), llm_records_list.extend(records)

    graph_str = request.app.state.knowledge_graph.build_graphs(relevant_records_list, keywords_model.title)
    await global_queue.put(("echarts", graph_str))
    unique_dicts = [dict(t) for t in {tuple(sorted(d.items())) for d in llm_records_list}]
    return {"triples": unique_dicts}



@repair_qa.get("/images/{filename:path}", tags=["图片服务器"])
async def image_path(request: Request, filename: str = Path(...)):
    file_path = os.path.join(BASE_DIR, filename)
    # 判断文件是否存在
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    # 返回文件（自动根据扩展名设置 MIME）
    return FileResponse(file_path)
