"""
手语识别与翻译系统 - 集成模型定义

本文件定义了集成多个基础模型的手语识别模型。主要特点：
1. 整合多个单模型的预测结果，发挥各模型优势
2. 支持加权投票机制，可自定义不同模型的权重
3. 通过模型融合提高整体准确性和鲁棒性
4. 能够同时利用不同模型架构捕获的各种特征
"""

import torch
import torch.nn as nn


class EnsembleModel(nn.Module):
    def __init__(self, models, weights=None):
        super(EnsembleModel, self).__init__()
        self.models = nn.ModuleList(models)

        if weights is None:
            self.weights = torch.ones(len(models)) / len(models)
        else:
            self.weights = torch.tensor(weights) / sum(weights)

    def forward(self, x):
        outputs = []
        for model in self.models:
            outputs.append(model(x))

        # 加权平均
        ensemble_output = torch.zeros_like(outputs[0])
        for i, output in enumerate(outputs):
            ensemble_output += output * self.weights[i]

        return ensemble_output
