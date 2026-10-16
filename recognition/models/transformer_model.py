"""
手语识别与翻译系统 - Transformer模型定义

本文件定义了基于Transformer架构的手语识别模型。主要特点：
1. 使用自注意力机制捕获全局依赖关系
2. 位置编码保留序列位置信息
3. 多头注意力机制增强特征表示能力
4. 适合处理复杂的手语动作序列
"""

import math

import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class TransformerModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_heads, num_layers, num_classes, dropout=0.1):
        super(TransformerModel, self).__init__()

        # 特征嵌入层
        self.embedding = nn.Linear(input_size, hidden_size)

        # 位置编码
        self.pos_encoder = PositionalEncoding(hidden_size)

        # Transformer编码器层
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)

        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_classes)
        )

    def forward(self, x):
        # x的形状: [batch_size, seq_len, input_size]

        # 特征嵌入
        x = self.embedding(x)

        # 位置编码
        x = self.pos_encoder(x)

        # Transformer编码器
        x = self.transformer_encoder(x)

        # 全局池化 (使用平均池化)
        x = torch.mean(x, dim=1)

        # 分类
        x = self.classifier(x)

        return x

    def get_attention_weights(self, x):
        """获取注意力权重用于可视化"""
        x = self.embedding(x)
        x = self.pos_encoder(x)

        # 获取注意力权重 (简化版本)
        attentions = []
        for layer in self.transformer_encoder.layers:
            x = layer(x)
            # 注：这只是一个近似方法，实际获取注意力权重需要修改PyTorch源码
            attentions.append(x)

        # 返回最后一层的激活作为注意力的近似
        return attentions[-1]
        
    def load_state_dict(self, state_dict, strict=True):
        """
        自定义加载模型参数，处理参数不匹配的情况
        
        参数:
            state_dict (dict): 预训练模型的参数字典
            strict (bool): 是否严格匹配参数
            
        返回:
            (dict): 加载结果信息
        """
        # 获取当前模型的参数字典
        own_state = self.state_dict()
        
        # 创建缺失和不匹配的参数列表
        missing_keys = []
        unexpected_keys = []
        error_msgs = []
        
        # 遍历预训练模型参数
        for name, param in state_dict.items():
            if name not in own_state:
                unexpected_keys.append(name)
                continue
                
            # 获取当前模型对应参数
            own_param = own_state[name]
            
            # 检查参数形状是否匹配
            if param.shape != own_param.shape:
                # Transformer层参数不匹配时的处理
                if "transformer_encoder" in name:
                    # 如果是层数不匹配，跳过
                    if any(f"layers.{i}" in name for i in range(10)):
                        missing_keys.append(name)
                        continue
                
                # 尝试调整参数大小
                try:
                    # 对于权重参数，取出适当的部分
                    if len(param.shape) > 1:
                        # 处理2D参数（权重矩阵）
                        min_shape0 = min(param.shape[0], own_param.shape[0])
                        min_shape1 = min(param.shape[1], own_param.shape[1])
                        
                        # 复制可匹配的部分
                        own_param[:min_shape0, :min_shape1] = param[:min_shape0, :min_shape1]
                    else:
                        # 处理1D参数（偏置向量）
                        min_shape = min(param.shape[0], own_param.shape[0])
                        own_param[:min_shape] = param[:min_shape]
                        
                    # 更新参数
                    own_state[name].copy_(own_param)
                except Exception as e:
                    error_msgs.append(f'Error copying parameter {name}: {str(e)}')
            else:
                # 形状匹配，直接复制
                own_state[name].copy_(param)
        
        # 返回加载结果
        return {
            'missing_keys': missing_keys,
            'unexpected_keys': unexpected_keys,
            'error_msgs': error_msgs
        }
