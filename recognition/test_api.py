# -*- coding: utf-8 -*-
import requests
import json

# 测试词汇API
print("=== 测试词汇API ===")
resp = requests.get("http://localhost:5001/api/vocabulary")
data = resp.json()
print(f"词汇数量: {len(data.get('vocabulary', []))}")
for v in data.get('vocabulary', [])[:5]:
    print(f"  {v}")
print()

# 测试初始化API
print("=== 测试初始化API ===")
resp = requests.post(
    "http://localhost:5001/api/init-isolated",
    json={"model_type": "cnn_lstm"}
)
data = resp.json()
print(f"初始化成功: {data.get('success')}")
print(f"词汇大小: {data.get('data', {}).get('vocab_size')}")
print()

print("=== 请使用前端录制一段视频测试预测API ===")
