"""
孤立词手语识别 - 词汇表生成工具

功能：
1. 扫描孤立词数据集目录结构
2. 自动从目录名生成词汇表文件 corpus.txt
3. 支持批量处理和数据统计

数据目录结构：
    dataset/{词汇ID}/{样本ID}/*.jpg
    
样本ID格式：P{采集员编号}_{日期编码}_{样本编号(0-4)}
示例：P01_06_01_0 表示采集员P01的样本
"""

import os
import sys


def scan_vocabulary(dataset_dir):
    """
    扫描数据集目录，收集所有词汇ID
    
    参数:
        dataset_dir (str): 数据集根目录路径
        
    返回:
        list: 排序后的词汇ID列表
    """
    if not os.path.exists(dataset_dir):
        print(f"错误: 数据集目录不存在 - {dataset_dir}")
        return []
    
    vocabulary_ids = []
    
    # 遍历dataset目录下的所有子目录（词汇ID）
    for item in os.listdir(dataset_dir):
        item_path = os.path.join(dataset_dir, item)
        
        # 检查是否为目录（词汇目录）
        if os.path.isdir(item_path):
            # 验证是否为数字目录（词汇ID）
            if item.isdigit():
                vocabulary_ids.append(item)
            else:
                # 跳过非数字目录（如__pycache__等）
                if item != '__pycache__':
                    print(f"跳过非词汇目录: {item}")
    
    # 按数字排序
    vocabulary_ids.sort(key=lambda x: int(x))
    
    return vocabulary_ids


def load_existing_corpus(corpus_file):
    """
    加载已有的词汇表文件
    
    参数:
        corpus_file (str): 词汇表文件路径
        
    返回:
        dict: {词汇ID: 词汇文本}
    """
    existing_corpus = {}
    
    if os.path.exists(corpus_file):
        try:
            with open(corpus_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            vocab_id = parts[0].strip()
                            vocab_text = parts[1].strip()
                            existing_corpus[vocab_id] = vocab_text
                        elif len(parts) == 1:
                            # 如果只有词汇ID，没有文本
                            existing_corpus[parts[0].strip()] = ""
        except Exception as e:
            print(f"读取词汇表文件时出错: {e}")
    
    return existing_corpus


def generate_corpus(dataset_dir, corpus_file):
    """
    生成或更新词汇表文件
    
    从数据集目录扫描所有词汇ID，并与已有词汇表合并生成新的词汇表。
    如果词汇已有对应文本，保留原文本；否则使用词汇ID作为文本。
    
    参数:
        dataset_dir (str): 数据集根目录路径
        corpus_file (str): 词汇表文件路径
    """
    print("=" * 50)
    print("孤立词手语识别 - 词汇表生成工具")
    print("=" * 50)
    
    # 扫描词汇
    vocabulary_ids = scan_vocabulary(dataset_dir)
    
    if not vocabulary_ids:
        print(f"未在目录 {dataset_dir} 中找到任何词汇目录")
        return False
    
    print(f"\n找到 {len(vocabulary_ids)} 个词汇类别:")
    print(f"词汇ID范围: {vocabulary_ids[0]} - {vocabulary_ids[-1]}")
    
    # 加载已有词汇表
    existing_corpus = load_existing_corpus(corpus_file)
    print(f"已有词汇表包含 {len(existing_corpus)} 个词汇")
    
    # 生成新词汇表
    new_corpus = []
    for vocab_id in vocabulary_ids:
        # 格式化为6位数字（如 100 -> 000100）
        formatted_id = vocab_id.zfill(6)
        
        # 如果已有对应文本，保留原文本；否则使用ID
        if formatted_id in existing_corpus:
            vocab_text = existing_corpus[formatted_id]
        else:
            vocab_text = vocab_id  # 使用ID作为默认文本
        
        new_corpus.append((formatted_id, vocab_text))
    
    # 保存新词汇表
    os.makedirs(os.path.dirname(corpus_file), exist_ok=True)
    
    with open(corpus_file, 'w', encoding='utf-8') as f:
        for vocab_id, vocab_text in new_corpus:
            f.write(f"{vocab_id}\t{vocab_text}\n")
    
    print(f"\n词汇表已保存到: {corpus_file}")
    print(f"共 {len(new_corpus)} 个词汇")
    
    # 统计样本数量
    total_samples = 0
    sample_counts = {}
    
    for vocab_id in vocabulary_ids:
        vocab_path = os.path.join(dataset_dir, vocab_id)
        samples = [d for d in os.listdir(vocab_path) 
                   if os.path.isdir(os.path.join(vocab_path, d))]
        sample_counts[vocab_id] = len(samples)
        total_samples += len(samples)
    
    print(f"\n数据集统计:")
    print(f"  总样本数: {total_samples}")
    print(f"  平均每词汇样本数: {total_samples / len(vocabulary_ids):.1f}")
    
    return True


def main():
    """主函数入口"""
    # 获取项目根目录
    if len(sys.argv) > 1:
        dataset_dir = sys.argv[1]
    else:
        # 默认使用项目根目录下的dataset文件夹
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dataset_dir = os.path.join(project_root, 'dataset')
    
    # 设置词汇表文件路径
    corpus_file = os.path.join(dataset_dir, 'corpus.txt')
    
    print(f"数据集目录: {dataset_dir}")
    print(f"词汇表文件: {corpus_file}")
    print()
    
    # 生成词汇表
    success = generate_corpus(dataset_dir, corpus_file)
    
    if success:
        print("\n词汇表生成成功!")
    else:
        print("\n词汇表生成失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()
