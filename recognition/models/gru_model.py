"""
手语识别与翻译系统 - GRU模型定义

本文件定义了基于GRU(门控循环单元)架构的手语识别模型。主要特点：
1. 使用GRU单元处理时序数据，比LSTM更轻量级
2. 包含特征提取层，优化输入特征表示
3. 双向GRU捕获前向和后向时序依赖
4. 注意力机制增强对重要帧的关注
5. 适合资源受限环境，推理速度更快
"""

import torch
import torch.nn as nn


class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes, dropout=0.5):
        super(GRUModel, self).__init__()

        # 特征提取层
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout)
        )

        # GRU层
        self.gru = nn.GRU(
            hidden_size, hidden_size, num_layers,
            batch_first=True, bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )

        # 注意力机制
        self.attention = nn.Sequential(
            nn.Linear(hidden_size * 2, 1),
            nn.Tanh()
        )

        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, num_classes)
        )

    def forward(self, x):
        # x的形状: [batch_size, seq_len, input_size]
        batch_size, seq_len, input_size = x.size()

        # 特征提取
        x = x.view(-1, input_size)
        x = self.feature_extractor(x)
        x = x.view(batch_size, seq_len, -1)

        # GRU处理
        h0 = torch.zeros(2 * self.gru.num_layers, batch_size, self.gru.hidden_size).to(x.device)
        outputs, _ = self.gru(x, h0)

        # 注意力机制
        attn_weights = self.attention(outputs)  # [batch_size, seq_len, 1]
        attn_weights = torch.softmax(attn_weights, dim=1)

        # 加权求和
        context = torch.sum(outputs * attn_weights, dim=1)  # [batch_size, hidden_size*2]

        # 分类
        output = self.classifier(context)

        return output
        
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
                # GRU层参数不匹配时的处理
                if "gru" in name:
                    # 如果是层数不匹配，跳过
                    if any(f"l{i}" in name for i in range(3, 10)):
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

    def get_attention_weights(self, x):
        """获取注意力权重用于可视化"""
        batch_size, seq_len, input_size = x.size()

        # 特征提取
        x = x.view(-1, input_size)
        x = self.feature_extractor(x)
        x = x.view(batch_size, seq_len, -1)

        # GRU处理
        h0 = torch.zeros(2 * self.gru.num_layers, batch_size, self.gru.hidden_size).to(x.device)

        outputs, _ = self.gru(x, h0)

        # 注意力机制
        attn_weights = self.attention(outputs)
        attn_weights = torch.softmax(attn_weights, dim=1)

        return attn_weights
