"""
手语识别与翻译系统 - 训练脚本

本文件是手语识别与翻译系统的模型训练入口脚本。主要功能包括：
1. 数据集加载和预处理
2. 多种深度学习模型的训练（BiLSTM、Transformer、CNN-LSTM、GRU等）
3. 模型评估和性能指标计算
4. 模型权重的保存与管理

使用方法：
    python train.py --model_type transformer --batch_size 32 --epochs 100
"""

import os
import argparse
import warnings
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.utils.data.sampler import WeightedRandomSampler

from config.config import Config
from data.dataset import OptimizedHandSignDataset, load_data
from models.base_model import create_model, create_ensemble_model
from trainers.trainer import train_model, evaluate_model
from utils.visualization import plot_training_history

warnings.filterwarnings('ignore')


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='手语识别训练脚本')
    parser.add_argument('--model_type', type=str, default='bilstm',
                        choices=['bilstm', 'transformer', 'cnn_lstm', 'gru', 'all'],
                        help='模型类型，all表示训练所有模型')
    parser.add_argument('--batch_size', type=int, default=32, help='批量大小')
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='学习率')
    parser.add_argument('--patience', type=int, default=10, help='早停耐心值')
    parser.add_argument('--hidden_size', type=int, default=128, help='隐藏层大小')
    parser.add_argument('--num_layers', type=int, default=2, help='LSTM层数')
    parser.add_argument('--ensemble', action='store_true', help='是否创建集成模型')
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    config = Config()
    
    # 更新配置
    config.batch_size = args.batch_size
    config.num_epochs = args.epochs
    config.learning_rate = args.learning_rate
    config.patience = args.patience
    config.hidden_size = args.hidden_size
    config.num_layers = args.num_layers

    # 加载数据
    train_videos, val_videos, test_videos, train_labels, val_labels, test_labels, corpus_dict = load_data(config)

    print(f"训练集大小: {len(train_videos)}")
    print(f"验证集大小: {len(val_videos)}")
    print(f"测试集大小: {len(test_videos)}")
    print(f"类别数量: {config.num_classes}")

    # 创建数据集
    train_dataset = OptimizedHandSignDataset(train_videos, train_labels, transform=True)
    val_dataset = OptimizedHandSignDataset(val_videos, val_labels)
    test_dataset = OptimizedHandSignDataset(test_videos, test_labels)

    # 处理数据不平衡
    class_counts = np.bincount(train_labels)
    weights = 1.0 / class_counts
    sample_weights = weights[train_labels]
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        sampler=sampler,  # 使用加权采样器
        num_workers=config.num_workers,
        pin_memory=config.pin_memory,
        prefetch_factor=config.prefetch_factor
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        pin_memory=config.pin_memory
    )

    # 选择要训练的模型类型
    if args.model_type == 'all':
        model_types = ["bilstm", "transformer", "cnn_lstm", "gru"]
    else:
        model_types = [args.model_type]
    
    results = {}
    histories = {}
    
    for model_type in model_types:
        print(f"\n===== 训练 {model_type} 模型 =====")
        
        # 创建模型
        model = create_model(model_type, config)
        print(model)
        
        # 训练模型
        model, history = train_model(model, train_loader, val_loader, config, model_type)
        
        # 评估模型
        test_acc, precision, recall, f1 = evaluate_model(
            model, test_loader, config, corpus_dict, model_type
        )
        
        # 保存结果
        results[model_type] = {
            'accuracy': test_acc,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        histories[model_type] = history
    
    # 比较不同模型
    if len(model_types) > 1:
        print("\n===== 模型比较 =====")
        for model_type, metrics in results.items():
            print(f"{model_type}: 准确率={metrics['accuracy']:.2f}%, F1={metrics['f1']:.4f}")
        
        # 绘制训练历史
        plot_training_history(histories)
    
    # 创建并评估集成模型
    if args.ensemble or len(model_types) > 1:
        print("\n===== 创建集成模型 =====")
        model_paths = {
            model_type: os.path.join(config.model_save_path, f'best_{model_type}_model.pth')
            for model_type in model_types
        }
        
        # 检查所有模型文件是否存在
        all_exists = True
        for path in model_paths.values():
            if not os.path.exists(path):
                all_exists = False
                print(f"模型文件不存在: {path}")
        
        if all_exists:
            ensemble_model = create_ensemble_model(config, model_paths)
            print("集成模型创建成功！评估集成模型...")
            
            # 评估集成模型
            evaluate_model(ensemble_model, test_loader, config, corpus_dict, "ensemble")


if __name__ == "__main__":
    main()
