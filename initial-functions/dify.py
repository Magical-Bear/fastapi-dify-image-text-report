from dotenv import load_dotenv
load_dotenv(".env")
import os
import json
import asyncio
import aiohttp
from fastapi import UploadFile
from middlewares.message_queue import global_queue

dify_user = os.getenv('DIFY_USER')
dify_url = os.getenv('DIFY_BASE_URL')
dify_token = os.getenv('DIFY_API_KEY')
dify_base_city = os.getenv('DIFY_USER_BASE_CITY')


with open(os.getenv('DIFY_MESSAGE_CONFIG'), "r", encoding="UTF8") as f:
    message_config = json.load(f)


async def file_upload(image: UploadFile):
    form_data = aiohttp.FormData()
    form_data.add_field(
        "file",
        await image.read(),  # 直接读取内存中的文件内容
        filename=image.filename,
        content_type=image.content_type
    )
    form_data.add_field("user", dify_user)

    headers = {
        "Authorization": f"Bearer {dify_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{dify_url}/files/upload", data=form_data, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(text)
            result = await resp.json()
            print(result)


async def dify_stream_chat(query: str, histories: list, image: str | None = None, response_model: str = "streaming"):
    echarts_generated = False
    workflow_url = f"{dify_url}/chat-messages"
    headers = {
        "Authorization": f"Bearer {dify_token}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "chat_histories": str(histories),
            "base_city": dify_base_city,
        },
        "query": query,
        "response_mode": response_model,
        "user": dify_user,
        "files": [] if image is None else [
            {
                "type": "image",
                "transfer_method": "local_file",
                "upload_file_id": image,
            }
        ]
    }

    if response_model == "streaming":
        async with aiohttp.ClientSession() as session:
            async with session.post(workflow_url, headers=headers, json=data) as responses:
                async for line in responses.content:
                    line = line.decode("utf-8")
                    response = None
                    if line.startswith("data: ") is False:
                        continue
                    json_data = line[6:]  # 去掉 "data: " 前缀
                    response = json.loads(json_data)
                    print(response)
                    if response["event"] == "message_end" or response["event"] == "error":
                        await global_queue.put(('end', ''))
                        return
                    if response["event"] == "message":
                        node_id = response["from_variable_selector"][0]
                        for opt, node_list in message_config["messages"].items():
                            if node_id in node_list:
                                if opt == "echarts" and echarts_generated is False:
                                    echarts_data = response["answer"][11:-4]
                                    echarts_generated = True
                                    await global_queue.put((opt, echarts_data))
                                elif opt != "echarts":
                                    await global_queue.put((opt, response["answer"]))
                                break









if __name__ == '__main__':
    import asyncio
    asyncio.run(dify_stream_chat("CIR注册失败", []))
























async def llm_classification_request(query: str, stage_type: str, other_key: dict = {}, school_flag: str = "qf60"):
    input_params = {"stage": stage_type, "school_flag": school_flag}
    input_params.update(other_key)
    data = {
        "inputs": input_params,
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "abc-123",
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('DIFY_API_KEY')}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("DIFY_URL"), json=data, headers=headers) as response:
            data = await response.json()
            print(data)
            result = data["answer"]
            try:
                result = json.loads(result)
            except:
                pass
            return result


async def dify_stream_response(query: str, retrieval: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DIFY_API_KEY')}"
    }

    payload = {
        "inputs": {"retrieval": retrieval, "stage": "summary"},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "user",
        "files": []
    }

    async with (aiohttp.ClientSession() as session):
        try:
            async with session.post(os.getenv("DIFY_URL"), headers=headers, json=payload) as responses:
                if responses.status != 200:
                    print(f"请求失败，状态码: {responses.status}")
                    print(await responses.text())
                    yield f"网络不太好，再试一次吧"
                    return
                async for line in responses.content:
                    line = line.decode("utf-8")
                    response = None
                    if line.startswith("data: "):
                        json_data = line[6:]  # 去掉 "data: " 前缀
                        response = json.loads(json_data)
                    if response is None:
                        continue
                    if response.get("event") == "message":
                        yield response.get("answer", "")
                    elif response.get("event") == "message_end":
                        return
                return
        except Exception as e:
            yield f"网络不太好，再试一次吧"
            return


