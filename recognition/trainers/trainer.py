"""
手语识别与翻译系统 - 训练器模块

本文件定义了模型训练和评估的函数，用于统一管理训练过程。主要功能：
1. 模型训练循环
2. 混合精度训练支持
3. 早停和学习率调度
4. 模型评估和指标计算
5. TensorBoard记录
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, classification_report

from utils.tensorboard_logger import TensorboardLogger


def train_model(model, train_loader, val_loader, config, model_name="bilstm"):
    """训练模型，使用混合精度训练和TensorBoard记录"""
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=1e-5)

    # 学习率调度器
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=1, eta_min=1e-6
    )

    # 早停
    early_stopping_counter = 0
    best_val_loss = float('inf')
    best_val_acc = 0.0

    # 混合精度训练
    scaler = torch.cuda.amp.GradScaler() if config.mixed_precision and torch.cuda.is_available() else None

    # TensorBoard记录器
    tb_logger = TensorboardLogger(f"logs/tensorboard/{model_name}")
    tb_logger.log_hyperparams(config)

    # 训练历史记录
    history = {
        'train_loss': [],
        'val_loss': [],
        'train_acc': [],
        'val_acc': []
    }

    for epoch in range(config.num_epochs):
        # 训练模式
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0

        all_train_preds = []
        all_train_labels = []
        all_train_scores = []

        progress_bar = tqdm(train_loader, desc=f'Epoch {epoch + 1}/{config.num_epochs}')
        for batch_idx, (inputs, labels) in enumerate(progress_bar):
            inputs, labels = inputs.to(config.device), labels.to(config.device)

            # 清零梯度
            optimizer.zero_grad()

            if scaler is not None:
                # 混合精度训练
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                # 反向传播
                scaler.scale(loss).backward()

                # 梯度裁剪
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

                # 优化器步进
                scaler.step(optimizer)
                scaler.update()
            else:
                # 常规训练
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                # 反向传播和优化
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

            # 更新学习率
            scheduler.step(epoch + batch_idx / len(train_loader))

            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()

            # 收集预测和标签用于计算指标
            all_train_preds.extend(predicted.cpu().numpy())
            all_train_labels.extend(labels.cpu().numpy())
            all_train_scores.extend(torch.softmax(outputs, dim=1).detach().cpu().numpy())

            # 更新进度条
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.0 * train_correct / train_total:.2f}%'
            })

        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total

        # 验证模式
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0

        all_val_preds = []
        all_val_labels = []
        all_val_scores = []

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(config.device), labels.to(config.device)

                if scaler is not None:
                    with torch.cuda.amp.autocast():
                        outputs = model(inputs)
                        loss = criterion(outputs, labels)
                else:
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

                # 收集预测和标签用于计算指标
                all_val_preds.extend(predicted.cpu().numpy())
                all_val_labels.extend(labels.cpu().numpy())
                all_val_scores.extend(torch.softmax(outputs, dim=1).detach().cpu().numpy())

        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total

        # 打印训练信息
        print(
            f'Epoch {epoch + 1}: train_loss={train_loss:.4f}, train_acc={train_acc:.2f}%, val_loss={val_loss:.4f}, val_acc={val_acc:.2f}%')

        # 记录历史
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)

        # 记录TensorBoard
        tb_logger.log_metrics(epoch, train_loss, val_loss, train_acc, val_acc)
        tb_logger.log_learning_rate(epoch, optimizer)
        
        # 记录sklearn指标
        tb_logger.log_sklearn_metrics(
            epoch, 
            np.array(all_val_labels), 
            np.array(all_val_preds),
            np.array(all_val_scores)
        )

        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            if not os.path.exists(config.model_save_path):
                os.makedirs(config.model_save_path)
            torch.save(model.state_dict(), os.path.join(config.model_save_path, f'best_{model_name}_model.pth'))
            early_stopping_counter = 0
            
            # 记录最佳验证指标
            precision, recall, f1, _ = precision_recall_fscore_support(
                all_val_labels, all_val_preds, average='weighted'
            )
            print(f"新的最佳模型！验证准确率: {val_acc:.2f}%, F1分数: {f1:.4f}")
            print(classification_report(all_val_labels, all_val_preds))
            
            # 绘制混淆矩阵
            cm = confusion_matrix(all_val_labels, all_val_preds)
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.xlabel('Predicted')
            plt.ylabel('True')
            plt.title(f'Confusion Matrix - {model_name}')
            plt.savefig(f'confusion_matrix_{model_name}.png')
            plt.close()
        else:
            early_stopping_counter += 1
            if early_stopping_counter >= config.patience:
                print(f'Early stopping at epoch {epoch + 1}')
                break

    # 关闭TensorBoard记录器
    tb_logger.close()

    return model, history


def evaluate_model(model, test_loader, config, corpus_dict, model_name="model"):
    """评估模型并显示详细指标"""
    model.eval()
    test_correct = 0
    test_total = 0

    predictions = []
    true_labels = []
    all_scores = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(config.device), labels.to(config.device)

            outputs = model(inputs)
            scores = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs.data, 1)

            test_total += labels.size(0)
            test_correct += (predicted == labels).sum().item()

            predictions.extend(predicted.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            all_scores.extend(scores.cpu().numpy())

    # 计算指标
    test_acc = 100 * test_correct / test_total
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='weighted'
    )
    
    # 打印结果
    print(f"------- {model_name} 评估结果 -------")
    print(f'测试准确率: {test_acc:.2f}%')
    print(f'精确率: {precision:.4f}')
    print(f'召回率: {recall:.4f}')
    print(f'F1分数: {f1:.4f}')
    print("\n分类报告:")
    print(classification_report(true_labels, predictions))
    
    # 绘制混淆矩阵
    cm = confusion_matrix(true_labels, predictions)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(f'Confusion Matrix - {model_name}')
    plt.savefig(f'test_confusion_matrix_{model_name}.png')
    
    # 输出一些例子
    print("\n示例预测结果:")
    for i in range(min(10, len(predictions))):
        pred_text = corpus_dict.get(str(predictions[i]).zfill(6), "未知")
        true_text = corpus_dict.get(str(true_labels[i]).zfill(6), "未知")
        confidence = np.max(all_scores[i])
        print(f"预测: {pred_text} ({confidence:.2%}) | 实际: {true_text}")
    
    return test_acc, precision, recall, f1 