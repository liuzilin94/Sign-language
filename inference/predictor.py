"""
手语识别与翻译系统 - 预测器模块

本文件定义了手语识别预测器类，用于进行手语视频的识别和翻译。主要功能：
1. 加载预训练模型
2. 视频文件的手语识别
3. 摄像头实时手语识别
4. 结果可视化和展示
"""

import os
import pandas as pd
import torch
import torch.nn as nn

# 使用绝对导入避免模块冲突
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.config import Config
from data.preprocessing import FeatureExtractor
from models.base_model import create_model


class HandSignPredictor:
    """手语预测器类"""

    def __init__(self, model_type="bilstm", model_path=None):
        self.config = Config()

        # 加载语料库
        corpus_df = pd.read_csv(
            self.config.corpus_file,
            sep=' ',
            header=None,
            names=['index', 'text']
        )
        self.corpus_dict = dict(zip(
            corpus_df['index'].astype(str).str.zfill(6),
            corpus_df['text']
        ))

        # 初始化模型
        self.model_type = model_type
        self.model = self._create_model(model_type)

        # 加载模型权重
        if model_path is None:
            model_path = os.path.join(self.config.model_save_path, f'best_{model_type}_model.pth')

        if os.path.exists(model_path):
            try:
                # 尝试加载模型
                if isinstance(model_path, dict):
                    # 处理集成模型的情况
                    for sub_model_type, sub_model_path in model_path.items():
                        print(f"加载子模型: {sub_model_type}")
                        # 处理集成模型的代码...
                else:
                    # 常规模型加载
                    print(f"正在加载模型: {model_path}")
                    checkpoint = torch.load(model_path, map_location=self.config.device)

                    # 对于CNN-LSTM模型，使用自定义的load_state_dict方法处理参数不匹配
                    if model_type == 'cnn_lstm':
                        result = self.model.load_state_dict(checkpoint, strict=False)
                        if result['missing_keys'] or result['unexpected_keys'] or result['error_msgs']:
                            print("模型加载存在以下问题，但已尝试兼容处理：")
                            if result['missing_keys']:
                                print(f"缺失键: {result['missing_keys'][:5]}...")
                            if result['unexpected_keys']:
                                print(f"未预期键: {result['unexpected_keys'][:5]}...")
                            if result['error_msgs']:
                                print(f"错误信息: {result['error_msgs']}")
                    else:
                        # 对其他模型使用常规加载，但设置strict=False以允许部分参数不匹配
                        self.model.load_state_dict(checkpoint, strict=False)

                print(f"模型已成功加载: {model_path}")
                # 设置为评估模式
                self.model.eval()
            except Exception as e:
                print(f"加载模型时出错: {str(e)}")
                raise RuntimeError(f"模型加载失败: {str(e)}")
        else:
            raise FileNotFoundError(f"模型文件未找到: {model_path}")

        self.feature_extractor = FeatureExtractor(self.config.seq_length)
        self.model.eval()

    def _create_model(self, model_type):
        """创建指定类型的模型"""
        return create_model(model_type, self.config)

    def predict(self, video_path, return_prob=False):
        """
        预测视频中的手语内容

        参数:
            video_path (str): 视频文件路径
            return_prob (bool): 是否返回预测概率

        返回:
            如果 return_prob=False:
                str: 预测的文本
            如果 return_prob=True:
                tuple: (预测的文本, 预测的概率)
        """
        # 提取特征
        features = self.feature_extractor.extract_from_video(video_path)
        features = torch.FloatTensor(features).unsqueeze(0).to(self.config.device)

        # 预测
        with torch.no_grad():
            outputs = self.model(features)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

            predicted_idx = predicted.item()
            confidence = confidence.item()
            predicted_text = self.corpus_dict.get(
                str(predicted_idx).zfill(6),
                "未知"
            )

        if return_prob:
            return predicted_text, confidence
        return predicted_text


class IsolatedWordPredictor:
    """孤立词手语预测器类

    专门用于孤立词手语识别，支持：
    1. 从jpg图像序列目录预测
    2. 从视频文件预测
    3. 从摄像头实时预测
    """

    def __init__(self, model_type="cnn_lstm", model_path=None, corpus_file=None):
        """
        初始化孤立词预测器

        参数:
            model_type (str): 模型类型
            model_path (str): 模型文件路径
            corpus_file (str): 词汇表文件路径
        """
        self.config = Config()

        # 加载词汇表
        if corpus_file is None:
            corpus_file = self.config.isolated_corpus_file

        self._load_corpus(corpus_file)  # 初始化 corpus_by_idx

        # 初始化模型
        self.model_type = model_type
        self.model = self._create_model(model_type)

        # 加载模型权重
        if model_path is None:
            model_path = os.path.join(self.config.model_save_path, 'best_isolated_model.pth')

        self._load_model(model_path, model_type)

        # 初始化特征提取器
        self.feature_extractor = FeatureExtractor(self.config.isolated_seq_length)

        # 设置为评估模式
        self.model.eval()

    def _load_corpus(self, corpus_file):
        """加载词汇表"""
        corpus_dict = {}
        label_to_idx = {}

        if os.path.exists(corpus_file):
            try:
                # 检测分隔符
                with open(corpus_file, 'rb') as f:
                    first_bytes = f.read(100)
                    if b'\t' in first_bytes:
                        sep = '\t'
                    else:
                        sep = ' '

                # 加载词汇表
                df = pd.read_csv(corpus_file, sep=sep, header=None, names=['index', 'text'])
                for df_idx, row in df.iterrows():
                    # df_idx: DataFrame 排序后的行号（0, 1, 2, ...），即训练索引
                    # row['index']: 原始 corpus ID 如 "000100"
                    corpus_id = str(row['index']).zfill(6)
                    text = str(row['text']).strip()
                    corpus_dict[corpus_id] = text
                    label_to_idx[df_idx] = text
            except Exception as e:
                print(f"词汇表加载出错: {e}")

        self.corpus_by_id = corpus_dict  # 按原始ID查找
        self.corpus_by_idx = label_to_idx  # 按训练索引查找

        print(f"词汇表加载完成: {len(label_to_idx)} 个词汇")
        return label_to_idx

    def _create_model(self, model_type):
        """创建指定类型的模型"""
        # 更新配置中的类别数 - 使用corpus_by_idx
        self.config.num_classes = len(self.corpus_by_idx) if hasattr(self, 'corpus_by_idx') and self.corpus_by_idx else 40
        return create_model(model_type, self.config)

    def _load_model(self, model_path, model_type):
        """加载模型权重"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件未找到: {model_path}")

        print(f"正在加载孤立词模型: {model_path}")

        try:
            checkpoint = torch.load(model_path, map_location=self.config.device)

            # 处理检查点格式
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                # 训练脚本保存的格式
                self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
            else:
                # 直接是模型权重
                self.model.load_state_dict(checkpoint, strict=False)

            print("孤立词模型加载成功")
        except Exception as e:
            print(f"模型加载出错: {e}")
            raise

    def _predict(self, features, return_prob=False, top_k=1, target_index=None):
        """
        通用预测方法

        参数:
            features (np.ndarray): 特征数组，形状 (seq_length, feature_dim)
            return_prob (bool): 是否返回概率
            top_k (int): 返回前k个预测结果
            target_index (int, optional): 目标词汇索引，用于返回目标词汇的置信度

        返回:
            预测结果（格式取决于return_prob和top_k参数）
        """
        features = torch.FloatTensor(features).unsqueeze(0).to(self.config.device)

        with torch.no_grad():
            outputs = self.model(features)
            probabilities = torch.softmax(outputs, dim=1)

            # 获取目标词汇的置信度（如果指定了）
            target_confidence = None
            if target_index is not None:
                target_confidence = probabilities[0][target_index].item()
                if target_confidence != target_confidence:  # NaN检查
                    target_confidence = 0.0
                target_confidence = max(0.0, min(1.0, target_confidence))

            if top_k == 1:
                # 返回单个预测
                confidence, predicted = torch.max(probabilities, 1)
                predicted_idx = predicted.item()
                confidence = confidence.item()

                # 确保confidence不是NaN或无效值
                if confidence != confidence:  # NaN检查
                    confidence = 0.0
                confidence = max(0.0, min(1.0, confidence))  # 限制范围

                # 映射到词汇文本 - 使用索引映射（训练时索引从0开始）
                predicted_text = self.corpus_by_idx.get(predicted_idx, f"词汇_{predicted_idx}")

                if return_prob:
                    # 如果指定了目标索引，返回完整信息
                    if target_index is not None:
                        target_text = self.corpus_by_idx.get(target_index, f"词汇_{target_index}")
                        return {
                            "predicted": predicted_text,
                            "predicted_idx": predicted_idx,
                            "confidence": confidence,
                            "target": target_text,
                            "target_idx": target_index,
                            "target_confidence": target_confidence
                        }
                    return predicted_text, confidence
                return predicted_text
            else:
                # 返回多个预测
                top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
                top_probs = top_probs[0].cpu().numpy()
                top_indices = top_indices[0].cpu().numpy()

                results = []
                for prob, idx in zip(top_probs, top_indices):
                    # 确保概率不是NaN
                    prob_val = float(prob)
                    if prob_val != prob_val:  # NaN检查
                        prob_val = 0.0
                    prob_val = max(0.0, min(1.0, prob_val))

                    text = self.corpus_by_idx.get(idx, f"词汇_{idx}")
                    results.append((text, prob_val))

                return results

    def predict_from_jpg_sequence(self, frames_dir, return_prob=False, top_k=1):
        """
        从jpg图像序列目录预测

        参数:
            frames_dir (str): 包含jpg图像序列的目录路径
            return_prob (bool): 是否返回概率
            top_k (int): 返回前k个预测结果

        返回:
            预测的词汇文本或包含概率的元组列表
        """
        try:
            features = self.feature_extractor.extract_from_jpg_sequence(frames_dir)
            return self._predict(features, return_prob=return_prob, top_k=top_k)
        except Exception as e:
            print(f"预测失败: {e}")
            if return_prob:
                return "预测失败", 0.0
            return "预测失败"

    def predict_from_video(self, video_path, return_prob=False, top_k=1, target_index=None):
        """
        从视频文件预测

        参数:
            video_path (str): 视频文件路径
            return_prob (bool): 是否返回概率
            top_k (int): 返回前k个预测结果
            target_index (int, optional): 目标词汇索引

        返回:
            预测的词汇文本或包含概率的元组列表
        """
        try:
            features = self.feature_extractor.extract_from_video(video_path)
            return self._predict(features, return_prob=return_prob, top_k=top_k, target_index=target_index)
        except Exception as e:
            print(f"预测失败: {e}")
            if return_prob:
                return "预测失败", 0.0
            return "预测失败"

    def predict_webcam(self, duration=3, return_prob=False, top_k=1, target_index=None):
        """
        从摄像头实时预测

        参数:
            duration (int): 录制时长（秒）
            return_prob (bool): 是否返回概率
            top_k (int): 返回前k个预测结果
            target_index (int, optional): 目标词汇索引

        返回:
            预测的词汇文本或包含概率的元组列表
        """
        features = self.feature_extractor.extract_from_webcam(duration)

        if features is None:
            if return_prob:
                return "无法获取摄像头输入", 0.0
            return "无法获取摄像头输入"

        return self._predict(features, return_prob=return_prob, top_k=top_k, target_index=target_index)

    def predict(self, input_data, return_prob=False, top_k=1):
        """
        统一的预测接口，根据输入类型自动选择预测方法

        参数:
            input_data: 输入数据，可以是：
                       - str: 文件路径（.jpg目录、.mp4/.avi视频）
                       - list: jpg图像列表
                       - int: 摄像头录制时长（秒）
            return_prob (bool): 是否返回概率
            top_k (int): 返回前k个预测结果

        返回:
            预测结果
        """
        # 根据输入类型选择预测方法
        if isinstance(input_data, str):
            # 字符串路径
            if os.path.isdir(input_data):
                # jpg序列目录
                return self.predict_from_jpg_sequence(input_data, return_prob, top_k)
            elif os.path.isfile(input_data):
                # 视频文件
                return self.predict_from_video(input_data, return_prob, top_k)
            else:
                if return_prob:
                    return "输入路径无效", 0.0
                return "输入路径无效"
        elif isinstance(input_data, int):
            # 摄像头录制时长
            return self.predict_webcam(input_data, return_prob, top_k)
        elif isinstance(input_data, (list, tuple)):
            # 图像帧列表
            features = self.feature_extractor.extract_from_frames(input_data)
            return self._predict(features, return_prob=return_prob, top_k=top_k)
        else:
            if return_prob:
                return "不支持的输入类型", 0.0
            return "不支持的输入类型"
    def predict_webcam(self, duration=3, return_prob=False):
        """
        从摄像头预测手语内容

        参数:
            duration (int): 录制时长，单位为秒
            return_prob (bool): 是否返回预测概率

        返回:
            如果 return_prob=False:
                str: 预测的文本
            如果 return_prob=True:
                tuple: (预测的文本, 预测的概率)
        """
        features = self.feature_extractor.extract_from_webcam(duration)
        if features is None:
            if return_prob:
                return "无法获取摄像头输入", 0.0
            return "无法获取摄像头输入"

        features = torch.FloatTensor(features).unsqueeze(0).to(self.config.device)

        # 预测
        with torch.no_grad():
            outputs = self.model(features)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)

            predicted_idx = predicted.item()
            confidence = confidence.item()

            # 确保confidence是有效数值
            if confidence != confidence:  # NaN检查
                confidence = 0.0
            confidence = max(0.0, min(1.0, confidence))

            # 使用corpus_by_idx映射
            if hasattr(self, 'corpus_by_idx') and self.corpus_by_idx:
                predicted_text = self.corpus_by_idx.get(predicted_idx, f"词汇_{predicted_idx}")
            else:
                predicted_text = f"词汇_{predicted_idx}"

        if return_prob:
            return predicted_text, confidence
        return predicted_text
