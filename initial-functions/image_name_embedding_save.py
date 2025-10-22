from dotenv import load_dotenv
load_dotenv("../.env")
import os
import json
import numpy as np
import jieba
from tqdm import tqdm
from openai import OpenAI


class ImageSemanticSearcher:
    """
    基于阿里云 DashScope embedding 的图片语义检索器
    支持本地缓存 embedding，提升性能
    """

    def __init__(self, image_dir, cache_path="../assets/embeddings/image_embeddings.json",
                 api_key_env="DASHSCOPE_API_KEY",
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 model="text-embedding-v4",
                 dimensions=1024):
        """
        初始化
        :param image_dir: 图片目录
        :param cache_path: 本地embedding缓存路径
        :param api_key_env: 环境变量名
        :param base_url: 阿里云兼容OpenAI接口URL
        :param model: embedding模型
        :param dimensions: 向量维度
        """
        self.image_dir = image_dir
        self.cache_path = cache_path
        self.client = OpenAI(api_key=os.getenv(api_key_env), base_url=base_url)
        self.model = model
        self.dimensions = dimensions

        self.image_texts = []
        self.image_paths = []
        self.embeddings = None

        # 1️⃣ 加载缓存或初始化
        self._load_or_generate_embeddings()

    def _generate_embedding(self, text):
        """
        调用 API 获取 embedding 向量
        """
        resp = self.client.embeddings.create(
            model=self.model,
            input=[text],
            dimensions=self.dimensions
        )
        return resp.data[0].embedding

    def _load_or_generate_embeddings(self):
        """
        加载缓存，如果有新图片则增量生成
        """
        print("📂 正在加载图片语义与embedding...")
        embeddings_dict = {}

        # 尝试加载缓存
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                embeddings_dict = json.load(f)
            print(f"✅ 已加载缓存 embedding ({len(embeddings_dict)} 条)。")

        # 逐个文件检查
        updated = False
        for file in tqdm(os.listdir(self.image_dir)):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                continue

            img_path = os.path.join(self.image_dir, file)
            img_name = os.path.splitext(file)[0]
            seg_text = " ".join(jieba.lcut(img_name))

            self.image_paths.append(img_path)
            self.image_texts.append(seg_text)

            if img_path not in embeddings_dict:
                embedding = self._generate_embedding(seg_text)
                embeddings_dict[img_path] = embedding
                updated = True

        # 如果有新数据，更新缓存
        if updated:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(embeddings_dict, f, ensure_ascii=False, indent=2)
            print("💾 已更新缓存文件。")

        # 转换为矩阵
        self.embeddings = np.array(list(embeddings_dict.values()), dtype=np.float32)
        self.image_paths = list(embeddings_dict.keys())

        # 归一化（余弦相似度更快）
        self.embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        print(f"✅ 已加载 {len(self.image_paths)} 张图片的 embedding。")

    def search(self, query_texts, top_k=3):
        """
        搜索最相似的图片
        :param query_texts: list[str] 查询句子（可以是改写的多个版本）
        :param top_k: 返回前k个结果
        """
        if isinstance(query_texts, str):
            query_texts = [query_texts]

        # 合并多个改写的embedding取平均（提升鲁棒性）
        query_embeddings = []
        for text in query_texts:
            seg_text = " ".join(jieba.lcut(text))
            emb = np.array(self._generate_embedding(seg_text), dtype=np.float32)
            emb /= np.linalg.norm(emb)
            query_embeddings.append(emb)

        query_vec = np.mean(query_embeddings, axis=0)

        # 本地计算余弦相似度
        scores = np.dot(self.embeddings, query_vec)

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(self.image_paths[i], float(scores[i])) for i in top_indices]
        return results



if __name__ == '__main__':
    searcher = ImageSemanticSearcher("../assets/static_images")
    query_rewrites = [
        "GSMR呼叫",
        "与车站联系失败"
    ]

    results = searcher.search(query_rewrites, top_k=3)
    print(results)