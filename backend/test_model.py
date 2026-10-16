import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from inference.predictor import IsolatedWordPredictor

# 初始化预测器
model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_isolated_model.pth')
corpus_path = os.path.join(os.path.dirname(__file__), 'dataset', 'corpus.txt')

print(f"模型路径: {os.path.abspath(model_path)}")
print(f"词汇表路径: {os.path.abspath(corpus_path)}")
print(f"模型文件存在: {os.path.exists(model_path)}")
print(f"词汇表文件存在: {os.path.exists(corpus_path)}")

try:
    predictor = IsolatedWordPredictor(
        model_type='cnn_lstm',
        model_path=model_path,
        corpus_file=corpus_path
    )

    print(f"\n模型加载成功！")
    print(f"词汇表大小: {len(predictor.corpus_by_idx)}")
    print(f"词汇映射（前10个）:")
    for idx, text in list(predictor.corpus_by_idx.items())[:10]:
        print(f"  索引 {idx}: {text}")
except Exception as e:
    print(f"模型加载失败: {e}")
    import traceback
    traceback.print_exc()
