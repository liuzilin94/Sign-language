"""
手语识别与翻译系统 - 模型基类

本文件定义了模型创建和加载的通用函数，用于统一管理不同类型的模型。主要功能：
1. 创建不同类型的模型实例
2. 加载预训练模型权重
3. 提供模型类型和配置的统一接口
"""

import torch
from models.bilstm_model import ImprovedBiLSTMModel
from models.transformer_model import TransformerModel
from models.cnn_lstm_model import CNN_LSTM_Model
from models.gru_model import GRUModel
from models.ensemble_model import EnsembleModel


def create_model(model_type, config):
    """根据指定类型创建模型"""
    if model_type == "bilstm":
        return ImprovedBiLSTMModel(
            config
        ).to(config.device)
    elif model_type == "transformer":
        return TransformerModel(
            config.input_size,
            config.hidden_size,
            num_heads=8,
            num_layers=config.num_layers,
            num_classes=config.num_classes,
            dropout=0.3
        ).to(config.device)
    elif model_type == "cnn_lstm":
        return CNN_LSTM_Model(
            config.input_size,
            config.hidden_size,
            config.num_layers,
            config.num_classes,
            dropout=0.5
        ).to(config.device)
    elif model_type == "gru":
        return GRUModel(
            config.input_size,
            config.hidden_size,
            config.num_layers,
            config.num_classes,
            dropout=0.5
        ).to(config.device)
    else:
        raise ValueError(f"未知模型类型: {model_type}")


def load_model(model_type, model_path, config):
    """加载预训练模型"""
    model = create_model(model_type, config)
    model.load_state_dict(torch.load(model_path, map_location=config.device))
    model.eval()
    return model


def create_ensemble_model(config, model_paths):
    """创建并加载集成模型"""
    models = []
    
    # 加载每个模型
    for model_type, model_path in model_paths.items():
        model = create_model(model_type, config)
        model.load_state_dict(torch.load(model_path, map_location=config.device))
        model.eval()
        models.append(model)
    
    # 创建集成模型
    ensemble = EnsembleModel(models).to(config.device)
    
    return ensemble 