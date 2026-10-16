#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看训练好的模型信息"""

import torch
import os

model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_isolated_model.pth')

print('=' * 60)
print('CSL手语识别模型 - 训练结果')
print('=' * 60)
print()

if os.path.exists(model_path):
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
    
    val_acc = checkpoint.get('val_acc', 0)
    epoch = checkpoint.get('epoch', 0)
    config = checkpoint.get('config', {})
    
    print(f"验证准确率 (Validation Accuracy): {val_acc:.2f}%")
    print(f"训练轮数 (Training Epochs): {epoch + 1}")
    print()
    print('模型配置 (Model Configuration):')
    print(f"  - 词汇类别数 (Num Classes): {config.get('num_classes', 40)}")
    print(f"  - 隐藏层大小 (Hidden Size): {config.get('hidden_size', 128)}")
    print(f"  - 循环层数 (Num Layers): {config.get('num_layers', 2)}")
    print(f"  - 序列长度 (Seq Length): {config.get('seq_length', 30)}")
    print()
    
    # 计算参数量
    total_params = sum(p.numel() for p in checkpoint['model_state_dict'].values())
    print(f"模型参数量 (Total Parameters): {total_params:,}")
    print()
    
    print('=' * 60)
    print('性能评估')
    print('=' * 60)
    
    # 根据准确率给出评价
    if val_acc >= 90:
        grade = "优秀 (Excellent)"
    elif val_acc >= 80:
        grade = "良好 (Good)"
    elif val_acc >= 70:
        grade = "中等 (Fair)"
    elif val_acc >= 60:
        grade = "及格 (Pass)"
    else:
        grade = "需要改进 (Need Improvement)"
    
    print(f"综合评价: {grade}")
    print()
    print(f"对于40类手语词汇识别任务:")
    print(f"  - 正确预测样本数: 约 {val_acc/100 * 40:.0f}/40 个词汇")
    print(f"  - 平均置信度: {val_acc:.1f}%")
else:
    print(f"Model file not found: {model_path}")

print()
print('=' * 60)
