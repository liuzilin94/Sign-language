"""
孤立词手语识别 - 模型训练脚本

功能：
1. 扫描孤立词数据集目录
2. 按采集员划分训练/验证/测试集
3. 批量提取jpg序列的特征（使用MediaPipe）
4. 缓存特征到本地（加快后续训练）
5. 训练CNN-LSTM模型
6. 评估并保存最佳模型

使用方式：
    python train_isolated.py
    python train_isolated.py --epochs 100 --batch_size 32 --model_type cnn_lstm
"""

import argparse
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from data.isolated_dataset import (
    IsolatedWordDataset, 
    scan_isolated_dataset, 
    split_by_person,
    normalize_sequence,
    extract_person_id
)
from data.preprocessing import FeatureExtractor, preprocess_isolated_features
from models.base_model import create_model


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='孤立词手语识别模型训练')
    
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32, help='批次大小')
    parser.add_argument('--learning_rate', type=float, default=3e-4, help='学习率')
    parser.add_argument('--model_type', type=str, default='cnn_lstm', 
                        choices=['bilstm', 'cnn_lstm', 'gru', 'transformer'],
                        help='模型类型')
    parser.add_argument('--seq_length', type=int, default=30, help='序列长度')
    parser.add_argument('--hidden_size', type=int, default=128, help='隐藏层大小')
    parser.add_argument('--num_layers', type=int, default=2, help='循环层数')
    parser.add_argument('--patience', type=int, default=15, help='早停耐心值')
    parser.add_argument('--num_workers', type=int, default=4, help='数据加载线程数')
    parser.add_argument('--test_ratio', type=float, default=0.2, help='测试集比例')
    parser.add_argument('--val_ratio', type=float, default=0.1, help='验证集比例')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    parser.add_argument('--no_cache', action='store_true', help='不使用特征缓存')
    parser.add_argument('--resume', type=str, default=None, help='恢复训练的模型路径')
    
    return parser.parse_args()


def load_corpus(corpus_file):
    """加载词汇表
    
    参数:
        corpus_file (str): 词汇表文件路径
        
    返回:
        dict: {词汇ID: 词汇文本}
    """
    corpus_dict = {}
    
    if os.path.exists(corpus_file):
        df = pd.read_csv(corpus_file, sep='\t', header=None, names=['index', 'text'])
        corpus_dict = dict(zip(
            df['index'].astype(str).str.zfill(6),
            df['text']
        ))
    
    return corpus_dict


class IsolatedFeatureDataset(torch.utils.data.Dataset):
    """
    孤立词特征数据集（从缓存加载特征）
    
    与 IsolatedWordDataset 的区别：
    - 直接从预提取的缓存文件中加载特征
    - 内存占用更小，适合大数据集
    """
    
    def __init__(self, video_paths, labels, feature_cache_dir='features', transform=False):
        self.video_paths = video_paths
        self.labels = labels
        self.feature_cache_dir = feature_cache_dir
        self.transform = transform
    
    def __len__(self):
        return len(self.video_paths)
    
    def __getitem__(self, idx):
        import pickle
        
        # 加载缓存的特征
        cache_filename = os.path.join(
            self.feature_cache_dir,
            f"{os.path.basename(self.video_paths[idx])}.pkl"
        )
        
        if os.path.exists(cache_filename):
            with open(cache_filename, 'rb') as f:
                features = pickle.load(f)
        else:
            # 如果没有缓存，返回零特征（不应该发生）
            features = np.zeros((30, 84), dtype=np.float32)
        
        # 确保特征形状一致 (30, 84)
        target_len, feat_dim = 30, 84
        if features.shape[0] < target_len:
            # 填充
            pad = np.zeros((target_len - features.shape[0], feat_dim), dtype=np.float32)
            features = np.vstack([features, pad])
        elif features.shape[0] > target_len:
            # 截断
            features = features[:target_len]
        
        # 数据增强
        if self.transform:
            features = self._augment(features)
        
        features = torch.FloatTensor(features)
        label = torch.LongTensor([self.labels[idx]])[0]
        
        return features, label
    
    def _augment(self, features):
        """数据增强"""
        import random
        
        target_len, feat_dim = 30, 84
        
        # 添加噪声
        if random.random() < 0.5:
            noise = np.random.randn(*features.shape) * 0.05
            features = features + noise
        
        # 时间偏移
        if random.random() < 0.3:
            shift = random.randint(-2, 2)
            if shift > 0:
                features = np.vstack([features[shift:], np.tile(features[-1:], (shift, 1))])
            elif shift < 0:
                features = np.vstack([np.tile(features[0:], (-shift, 1)), features[:shift]])
        
        # 确保增强后形状一致
        if features.shape[0] < target_len:
            pad = np.zeros((target_len - features.shape[0], feat_dim), dtype=np.float32)
            features = np.vstack([features, pad])
        elif features.shape[0] > target_len:
            features = features[:target_len]
        
        return features


def train_epoch(model, train_loader, criterion, optimizer, device):
    """训练一个epoch
    
    参数:
        model: 神经网络模型
        train_loader: 训练数据加载器
        criterion: 损失函数
        optimizer: 优化器
        device: 计算设备
        
    返回:
        float: 平均训练损失
    """
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    pbar = tqdm(train_loader, desc='训练中')
    for features, labels in pbar:
        features = features.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, labels)
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{100*correct/total:.2f}%'})
    
    return total_loss / len(train_loader)


def validate_epoch(model, val_loader, criterion, device):
    """验证一个epoch
    
    参数:
        model: 神经网络模型
        val_loader: 验证数据加载器
        criterion: 损失函数
        device: 计算设备
        
    返回:
        tuple: (平均验证损失, 验证准确率)
    """
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for features, labels in tqdm(val_loader, desc='验证中'):
            features = features.to(device)
            labels = labels.to(device)
            
            outputs = model(features)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    return total_loss / len(val_loader), 100 * correct / total


def evaluate_model(model, test_loader, device, corpus_dict=None):
    """评估模型在测试集上的性能
    
    参数:
        model: 神经网络模型
        test_loader: 测试数据加载器
        device: 计算设备
        corpus_dict: 词汇表字典
        
    返回:
        tuple: (准确率, 精确率, 召回率, F1分数)
    """
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for features, labels in tqdm(test_loader, desc='测试中'):
            features = features.to(device)
            outputs = model(features)
            _, predicted = torch.max(outputs.data, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    # 计算指标
    from sklearn.metrics import precision_recall_fscore_support
    
    accuracy = 100 * np.sum(np.array(all_preds) == np.array(all_labels)) / len(all_labels)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='weighted', zero_division=0
    )
    
    print(f"\n测试集评估结果:")
    print(f"  准确率: {accuracy:.2f}%")
    print(f"  精确率: {precision:.4f}")
    print(f"  召回率: {recall:.4f}")
    print(f"  F1分数: {f1:.4f}")
    
    # 打印分类报告
    if corpus_dict:
        target_names = [corpus_dict.get(str(i).zfill(6), str(i)) for i in range(len(corpus_dict))]
        print("\n分类报告:")
        print(classification_report(all_labels, all_preds, target_names=target_names, zero_division=0))
    
    return accuracy, precision, recall, f1


def train_model(model, train_loader, val_loader, config):
    """
    训练模型的主函数
    
    参数:
        model: 神经网络模型
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        config: 配置对象
        
    返回:
        tuple: (训练后的模型, 训练历史)
    """
    device = config.device
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=5
    )
    
    # 早停
    best_val_acc = 0
    patience_counter = 0
    
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_acc': []
    }
    
    print(f"\n开始训练，共 {config.num_epochs} 轮...")
    print(f"设备: {device}")
    print("-" * 50)
    
    for epoch in range(config.num_epochs):
        epoch_start = time.time()
        
        # 训练
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # 验证
        val_loss, val_acc = validate_epoch(model, val_loader, criterion, device)
        
        # 更新学习率
        scheduler.step(val_acc)
        
        # 记录历史
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        epoch_time = time.time() - epoch_start
        
        print(f"Epoch {epoch+1}/{config.num_epochs} ({epoch_time:.1f}s)")
        print(f"  训练损失: {train_loss:.4f}")
        print(f"  验证损失: {val_loss:.4f}, 验证准确率: {val_acc:.2f}%")
        
        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            model_path = os.path.join(config.model_save_path, f'best_isolated_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'config': {
                    'num_classes': config.num_classes,
                    'hidden_size': config.hidden_size,
                    'num_layers': config.num_layers,
                    'seq_length': config.seq_length
                }
            }, model_path)
            
            print(f"  ★ 保存最佳模型 (准确率: {val_acc:.2f}%)")
        else:
            patience_counter += 1
            print(f"  未改进 ({patience_counter}/{config.patience})")
        
        # 早停
        if patience_counter >= config.patience:
            print(f"\n早停: 验证准确率连续 {config.patience} 轮未提升")
            break
        
        print("-" * 50)
    
    print(f"\n训练完成！最佳验证准确率: {best_val_acc:.2f}%")
    
    return model, history


def main():
    """主函数入口"""
    # 解析参数
    args = parse_args()
    
    # 设置随机种子
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(args.seed)
    
    # 创建配置
    config = Config()
    
    # 更新配置
    config.num_epochs = args.epochs
    config.batch_size = args.batch_size
    config.learning_rate = args.learning_rate
    config.seq_length = args.seq_length
    config.hidden_size = args.hidden_size
    config.num_layers = args.num_layers
    config.patience = args.patience
    config.num_workers = args.num_workers
    
    print("=" * 60)
    print("孤立词手语识别 - 模型训练")
    print("=" * 60)
    print(f"训练参数:")
    print(f"  模型类型: {args.model_type}")
    print(f"  训练轮数: {args.epochs}")
    print(f"  批次大小: {args.batch_size}")
    print(f"  学习率: {args.learning_rate}")
    print(f"  序列长度: {args.seq_length}")
    print(f"  隐藏层大小: {args.hidden_size}")
    print(f"  循环层数: {args.num_layers}")
    print(f"  数据加载线程: {args.num_workers}")
    print("-" * 60)
    
    # ===== 1. 扫描数据集 =====
    print("\n[1/5] 扫描孤立词数据集...")
    video_paths, labels = scan_isolated_dataset(config.isolated_video_dir)
    
    if not video_paths:
        print("错误: 未找到任何训练样本！")
        print(f"请确保数据集位于: {config.isolated_video_dir}")
        print("目录结构应为: dataset/{词汇ID}/{样本ID}/*.jpg")
        sys.exit(1)
    
    print(f"扫描完成: 共 {len(video_paths)} 个样本")
    
    # 标签映射：将原始标签(如100-139)转换为0开始的索引
    unique_labels = sorted(set(labels))
    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
    labels = [label_to_idx[label] for label in labels]
    
    # 更新类别数
    config.num_classes = len(unique_labels)
    print(f"原始标签: {unique_labels[0]}-{unique_labels[-1]}, 映射到: 0-{config.num_classes-1}")
    print(f"类别数: {config.num_classes}")
    
    # ===== 2. 划分数据集 =====
    print("\n[2/5] 按采集员划分数据集...")
    train_vids, val_vids, test_vids, train_labs, val_labs, test_labs = \
        split_by_person(video_paths, labels, 
                       test_ratio=args.test_ratio, 
                       val_ratio=args.val_ratio,
                       seed=args.seed)
    
    # 更新类别数
    config.num_classes = len(unique_labels)
    print(f"原始标签: {unique_labels[0]}-{unique_labels[-1]}, 映射到: 0-{config.num_classes-1}")
    print(f"类别数: {config.num_classes}")
    
    # 加载词汇表
    corpus_dict = load_corpus(config.isolated_corpus_file)
    print(f"词汇表包含 {len(corpus_dict)} 个词汇")
    
    # ===== 3. 预处理特征 =====
    print("\n[3/5] 预处理并缓存特征...")
    all_videos = train_vids + val_vids + test_vids
    
    if not args.no_cache:
        preprocess_isolated_features(all_videos)
    else:
        print("跳过特征预处理（--no_cache）")
    
    # ===== 4. 创建数据加载器 =====
    print("\n[4/5] 创建数据加载器...")
    
    train_dataset = IsolatedFeatureDataset(train_vids, train_labs, transform=True)
    val_dataset = IsolatedFeatureDataset(val_vids, val_labs, transform=False)
    test_dataset = IsolatedFeatureDataset(test_vids, test_labs, transform=False)
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers
    )
    val_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers
    )
    
    print(f"训练集: {len(train_dataset)} 样本")
    print(f"验证集: {len(val_dataset)} 样本")
    print(f"测试集: {len(test_dataset)} 样本")
    
    # ===== 5. 训练模型 =====
    print("\n[5/5] 训练模型...")
    
    # 创建模型
    model = create_model(args.model_type, config)
    model = model.to(config.device)
    
    # 统计参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n模型参数量: {total_params:,} (可训练: {trainable_params:,})")
    
    # 恢复训练（如果指定）
    start_epoch = 0
    if args.resume:
        print(f"从 {args.resume} 恢复训练...")
        checkpoint = torch.load(args.resume, map_location=config.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        print(f"从第 {start_epoch} 轮继续训练")
    
    # 训练
    trained_model, history = train_model(model, train_loader, val_loader, config)
    
    # ===== 6. 评估测试集 =====
    print("\n加载最佳模型进行测试...")
    best_model_path = os.path.join(config.model_save_path, 'best_isolated_model.pth')
    checkpoint = torch.load(best_model_path, map_location=config.device)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    accuracy, precision, recall, f1 = evaluate_model(model, test_loader, config.device, corpus_dict)
    
    # ===== 7. 保存最终结果 =====
    print("\n" + "=" * 60)
    print("训练完成！")
    print("=" * 60)
    print(f"最佳模型保存于: {best_model_path}")
    print(f"验证准确率: {checkpoint['val_acc']:.2f}%")
    print(f"测试准确率: {accuracy:.2f}%")
    print(f"精确率: {precision:.4f}, 召回率: {recall:.4f}, F1: {f1:.4f}")
    
    # 保存训练历史
    history_path = os.path.join(config.model_save_path, 'training_history.npz')
    np.savez(history_path, **history)
    print(f"训练历史保存于: {history_path}")


if __name__ == '__main__':
    main()
