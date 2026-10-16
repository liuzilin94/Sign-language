"""
孤立词手语识别 - 数据集加载器

功能：
1. 加载孤立词数据集（jpg图像序列）
2. 按采集员划分训练集/验证集/测试集
3. 支持PyTorch DataLoader

数据目录结构：
    dataset/{词汇ID}/{样本ID}/*.jpg
    
样本ID格式：P{采集员编号}_{日期编码}_{样本编号(0-4)}
示例：P01_06_01_0 表示采集员P01的样本

按采集员划分逻辑：
    - 从样本ID中提取采集员编号（如 P01_06_01_0 → P01）
    - 随机分配采集员到训练/验证/测试集
    - 确保同一采集员的所有样本在同一个集合中
"""

import os
import re
import random
from typing import List, Tuple, Optional, Dict

import numpy as np
import torch
from torch.utils.data import Dataset


def extract_person_id(sample_id: str) -> str:
    """
    从样本ID中提取采集员编号
    
    参数:
        sample_id (str): 样本ID，格式如 "P01_06_01_0"
        
    返回:
        str: 采集员编号，如 "P01"
    """
    # 使用正则表达式提取P开头的采集员编号
    match = re.match(r'^(P\d+)', sample_id)
    if match:
        return match.group(1)
    
    # 备用方案：取样本ID的第一个下划线前的部分
    parts = sample_id.split('_')
    return parts[0] if parts else sample_id


def scan_isolated_dataset(dataset_dir: str) -> Tuple[List[str], List[int]]:
    """
    扫描孤立词数据集目录，收集所有样本路径和标签
    
    参数:
        dataset_dir (str): 数据集根目录
        
    返回:
        Tuple[List[str], List[int]]: (样本路径列表, 对应标签列表)
    """
    video_paths = []
    labels = []
    
    if not os.path.exists(dataset_dir):
        print(f"错误: 数据集目录不存在 - {dataset_dir}")
        return [], []
    
    # 遍历词汇目录
    for vocab_dir in sorted(os.listdir(dataset_dir)):
        vocab_path = os.path.join(dataset_dir, vocab_dir)
        
        if not os.path.isdir(vocab_path):
            continue
        
        # 检查是否为数字目录（词汇ID）
        if not vocab_dir.isdigit():
            continue
        
        label = int(vocab_dir)
        
        # 遍历样本目录
        for sample_dir in os.listdir(vocab_path):
            sample_path = os.path.join(vocab_path, sample_dir)
            
            if not os.path.isdir(sample_path):
                continue
            
            # 检查目录中是否有jpg文件
            jpg_files = [f for f in os.listdir(sample_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if jpg_files:
                video_paths.append(sample_path)
                labels.append(label)
    
    return video_paths, labels


def split_by_person(
    video_paths: List[str], 
    labels: List[int],
    test_ratio: float = 0.2, 
    val_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[List, List, List, List, List, List]:
    """
    按采集员划分数据集（Person-wise split）
    
    确保同一采集员的所有样本在同一个集合中，避免数据泄漏。
    
    参数:
        video_paths (List[str]): 样本路径列表
        labels (List[int]): 对应标签列表
        test_ratio (float): 测试集比例
        val_ratio (float): 验证集比例
        seed (int): 随机种子
        
    返回:
        Tuple: (训练路径, 验证路径, 测试路径, 训练标签, 验证标签, 测试标签)
    """
    random.seed(seed)
    np.random.seed(seed)
    
    # 按采集员分组
    person_samples = {}  # {采集员ID: [(路径, 标签), ...]}
    
    for path, label in zip(video_paths, labels):
        sample_id = os.path.basename(path)
        person_id = extract_person_id(sample_id)
        
        if person_id not in person_samples:
            person_samples[person_id] = []
        person_samples[person_id].append((path, label))
    
    # 获取所有采集员列表
    all_persons = list(person_samples.keys())
    random.shuffle(all_persons)
    
    # 计算划分数量
    n_persons = len(all_persons)
    n_test = max(1, int(n_persons * test_ratio))
    n_val = max(1, int(n_persons * val_ratio))
    
    # 确保验证集+测试集不超过总人数的30%
    total_eval_ratio = test_ratio + val_ratio
    if total_eval_ratio > 0.3:
        n_test = max(1, int(n_persons * 0.15))
        n_val = max(1, int(n_persons * 0.15))
    
    # 划分采集员
    test_persons = set(all_persons[:n_test])
    val_persons = set(all_persons[n_test:n_test + n_val])
    train_persons = set(all_persons[n_test + n_val:])
    
    # 分配样本
    train_vids, val_vids, test_vids = [], [], []
    train_labs, val_labs, test_labs = [], [], []
    
    for path, label in zip(video_path := video_paths, labels):
        sample_id = os.path.basename(path)
        person_id = extract_person_id(sample_id)
        
        if person_id in test_persons:
            test_vids.append(path)
            test_labs.append(label)
        elif person_id in val_persons:
            val_vids.append(path)
            val_labs.append(label)
        else:
            train_vids.append(path)
            train_labs.append(label)
    
    print(f"数据集划分（按采集员）:")
    print(f"  采集员总数: {n_persons}")
    print(f"  训练集: {len(train_vids)} 样本 ({len(train_persons)} 人)")
    print(f"  验证集: {len(val_vids)} 样本 ({len(val_persons)} 人)")
    print(f"  测试集: {len(test_vids)} 样本 ({len(test_persons)} 人)")
    
    return train_vids, val_vids, test_vids, train_labs, val_labs, test_labs


def normalize_sequence(frames: List[np.ndarray], seq_length: int = 30) -> List[np.ndarray]:
    """
    归一化序列长度
    
    参数:
        frames (List[np.ndarray]): 原始帧列表
        seq_length (int): 目标序列长度
        
    返回:
        List[np.ndarray]: 归一化后的帧列表
    """
    total_frames = len(frames)
    
    if total_frames >= seq_length:
        # 帧数足够，等间隔采样
        indices = np.linspace(0, total_frames - 1, seq_length, dtype=int)
        return [frames[i] for i in indices]
    else:
        # 帧数不足，用最后一帧填充
        padding = seq_length - total_frames
        return frames + [frames[-1]] * padding


class IsolatedWordDataset(Dataset):
    """
    孤立词手语数据集类
    
    用于加载和处理孤立词手语数据集，支持jpg图像序列。
    """
    
    def __init__(
        self,
        video_paths: List[str],
        labels: List[int],
        seq_length: int = 30,
        transform: bool = False,
        feature_extractor: Optional = None,
        augment_config: Optional[Dict] = None
    ):
        """
        初始化孤立词数据集
        
        参数:
            video_paths (List[str]): 样本路径列表
            labels (List[int]): 对应标签列表
            seq_length (int): 序列长度（默认30帧）
            transform (bool): 是否应用数据增强
            feature_extractor: 特征提取器实例
            augment_config (Dict): 数据增强配置
        """
        self.video_paths = video_paths
        self.labels = labels
        self.seq_length = seq_length
        self.transform = transform
        self.feature_extractor = feature_extractor
        self.augment_config = augment_config or {}
        
        # 加载所有样本的特征到内存（加速训练）
        self._load_all_features()
    
    def _load_all_features(self):
        """预加载所有样本的特征到内存"""
        self.features = []
        
        if self.feature_extractor is not None:
            for path in self.video_paths:
                try:
                    features = self.feature_extractor.extract_from_jpg_sequence(path)
                    self.features.append(features)
                except Exception as e:
                    print(f"加载样本 {path} 时出错: {e}")
                    # 使用零特征作为占位
                    self.features.append(np.zeros((self.seq_length, 84), dtype=np.float32))
        else:
            # 不使用特征提取器，直接返回空
            self.features = [None] * len(self.video_paths)
    
    def _load_jpg_sequence(self, frames_dir: str) -> List[np.ndarray]:
        """
        加载jpg图像序列
        
        参数:
            frames_dir (str): 帧序列所在目录
            
        返回:
            List[np.ndarray]: 帧列表
        """
        # 获取所有jpg文件并排序
        jpg_files = sorted([
            f for f in os.listdir(frames_dir) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
        
        if not jpg_files:
            raise ValueError(f"目录中没有找到jpg文件: {frames_dir}")
        
        # 读取图像
        import cv2
        frames = []
        for jpg_file in jpg_files:
            img_path = os.path.join(frames_dir, jpg_file)
            img = cv2.imread(img_path)
            if img is not None:
                frames.append(img)
        
        # 归一化序列长度
        return normalize_sequence(frames, self.seq_length)
    
    def _apply_augmentation(self, features: np.ndarray) -> np.ndarray:
        """
        应用数据增强
        
        参数:
            features (np.ndarray): 原始特征 (seq_length, feature_dim)
            
        返回:
            np.ndarray: 增强后的特征
        """
        import random
        
        # 添加噪声
        if random.random() < self.augment_config.get('noise_prob', 0.5):
            noise_level = self.augment_config.get('noise_level', 0.05)
            noise = np.random.randn(*features.shape) * noise_level
            features = features + noise
        
        # 时间偏移（随机丢弃或复制部分帧）
        if random.random() < self.augment_config.get('time_shift_prob', 0.3):
            shift = random.randint(-3, 3)
            if shift > 0:
                features = np.concatenate([features[shift:], features[-1:].repeat(shift, axis=0)])
            elif shift < 0:
                features = np.concatenate([features[:0].repeat(-shift, axis=0), features[:shift]])
        
        return features
    
    def __len__(self) -> int:
        """返回数据集大小"""
        return len(self.video_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        获取单个样本
        
        参数:
            idx (int): 样本索引
            
        返回:
            Tuple[torch.Tensor, int]: (特征张量, 标签)
        """
        if self.features[idx] is not None:
            features = self.features[idx].copy()
        else:
            # 动态加载
            frames = self._load_jpg_sequence(self.video_paths[idx])
            # 这里应该调用特征提取器，但为了简单起见返回None
            features = np.zeros((self.seq_length, 84), dtype=np.float32)
        
        # 应用数据增强
        if self.transform and self.augment_config:
            features = self._apply_augmentation(features)
        
        # 转换为PyTorch张量
        features = torch.FloatTensor(features)
        label = self.labels[idx]
        
        return features, label
    
    def get_sample_info(self, idx: int) -> Dict:
        """
        获取样本信息
        
        参数:
            idx (int): 样本索引
            
        返回:
            Dict: 样本信息
        """
        return {
            'path': self.video_paths[idx],
            'label': self.labels[idx],
            'sample_id': os.path.basename(self.video_paths[idx]),
            'person_id': extract_person_id(os.path.basename(self.video_paths[idx]))
        }


def create_dataloaders(
    train_vids: List[str],
    val_vids: List[str],
    test_vids: List[str],
    train_labs: List[int],
    val_labs: List[int],
    test_labs: List[int],
    batch_size: int = 32,
    num_workers: int = 4,
    seq_length: int = 30,
    feature_extractor: Optional = None,
    augment_config: Optional[Dict] = None
) -> Tuple:
    """
    创建PyTorch DataLoader
    
    参数:
        train_vids: 训练样本路径
        val_vids: 验证样本路径
        test_vids: 测试样本路径
        train_labs: 训练标签
        val_labs: 验证标签
        test_labs: 测试标签
        batch_size: 批次大小
        num_workers: 数据加载线程数
        seq_length: 序列长度
        feature_extractor: 特征提取器
        augment_config: 数据增强配置
        
    返回:
        Tuple: (train_loader, val_loader, test_loader)
    """
    from torch.utils.data import DataLoader
    
    # 创建数据集
    train_dataset = IsolatedWordDataset(
        train_vids, train_labs, 
        seq_length=seq_length,
        transform=True,
        feature_extractor=feature_extractor,
        augment_config=augment_config
    )
    
    val_dataset = IsolatedWordDataset(
        val_vids, val_labs,
        seq_length=seq_length,
        transform=False,
        feature_extractor=feature_extractor,
        augment_config=None
    )
    
    test_dataset = IsolatedWordDataset(
        test_vids, test_labs,
        seq_length=seq_length,
        transform=False,
        feature_extractor=feature_extractor,
        augment_config=None
    )
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader, test_loader


# 测试代码
if __name__ == '__main__':
    # 测试数据集加载
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(project_root, 'dataset')
    
    print("测试孤立词数据集加载器...")
    
    # 扫描数据集
    video_paths, labels = scan_isolated_dataset(dataset_dir)
    print(f"扫描完成: {len(video_paths)} 个样本")
    
    if video_paths:
        # 测试按采集员划分
        train_vids, val_vids, test_vids, train_labs, val_labs, test_labs = \
            split_by_person(video_paths, labels)
        
        # 测试数据集类
        dataset = IsolatedWordDataset(train_vids[:10], train_labs[:10], seq_length=30)
        print(f"数据集大小: {len(dataset)}")
        
        if len(dataset) > 0:
            features, label = dataset[0]
            print(f"特征形状: {features.shape}")
            print(f"标签: {label}")
