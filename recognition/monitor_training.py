"""
训练进度监控脚本

用于实时监控孤立词手语识别模型的训练进度。

使用方法：
    python monitor_training.py
"""

import os
import time
from datetime import datetime

# 特征缓存目录
FEATURES_DIR = r"d:\sign-language\csl-recognition\recognition\features"
MODELS_DIR = r"d:\sign-language\csl-recognition\recognition\models"

# 总样本数（根据您的数据集）
TOTAL_SAMPLES = 10000

def get_processed_count():
    """获取已处理的特征数量"""
    if os.path.exists(FEATURES_DIR):
        count = len([f for f in os.listdir(FEATURES_DIR) if f.endswith('.pkl')])
        return count
    return 0

def get_model_status():
    """检查模型训练状态"""
    model_path = os.path.join(MODELS_DIR, 'best_isolated_model.pth')
    history_path = os.path.join(MODELS_DIR, 'training_history.npz')
    
    status = {
        'model_exists': os.path.exists(model_path),
        'history_exists': os.path.exists(history_path),
        'model_size': 0,
        'last_modified': None
    }
    
    if status['model_exists']:
        status['model_size'] = os.path.getsize(model_path)
        status['last_modified'] = datetime.fromtimestamp(os.path.getmtime(model_path))
    
    return status

def get_training_stage(processed_count):
    """判断当前训练阶段"""
    if processed_count == 0:
        return "等待开始"
    elif processed_count < TOTAL_SAMPLES:
        percent = processed_count / TOTAL_SAMPLES * 100
        remaining = TOTAL_SAMPLES - processed_count
        # 假设每样本约1.2秒
        eta_seconds = remaining * 1.2
        eta_minutes = eta_seconds / 60
        
        if eta_minutes > 60:
            eta_str = f"约 {eta_minutes/60:.1f} 小时"
        else:
            eta_str = f"约 {eta_minutes:.0f} 分钟"
        
        return f"特征提取中 ({percent:.1f}%) - 预计剩余: {eta_str}"
    else:
        return "特征提取完成 - 开始训练模型..."

def main():
    """主函数"""
    print("=" * 50)
    print("孤立词手语识别 - 训练进度监控")
    print("=" * 50)
    print()
    
    last_count = 0
    
    try:
        while True:
            # 清屏效果（通过打印换行）
            print("\n" * 3)
            
            # 获取当前状态
            processed = get_processed_count()
            model_status = get_model_status()
            
            # 计算进度
            percent = processed / TOTAL_SAMPLES * 100
            filled = int(percent / 2)
            empty = 50 - filled
            progress_bar = "=" * filled + "-" * empty
            
            # 绘制进度条
            print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"特征提取: {processed:,} / {TOTAL_SAMPLES:,} ({percent:.1f}%)")
            print(f"进度条: [{progress_bar}]")
            print()
            
            # 训练阶段
            stage = get_training_stage(processed)
            print(f"当前阶段: {stage}")
            print()
            
            # 模型状态
            if model_status['model_exists']:
                size_mb = model_status['model_size'] / (1024 * 1024)
                print(f"模型状态: 已保存 ({size_mb:.1f} MB)")
                print(f"保存时间: {model_status['last_modified'].strftime('%H:%M:%S')}")
            else:
                print("模型状态: 等待保存...")
            
            print()
            print("-" * 50)
            print("按 Ctrl+C 退出监控")
            print("-" * 50)
            
            # 检测进度变化
            if processed > last_count:
                speed = (processed - last_count)  # 每轮增量
                last_count = processed
            
            # 等待5秒后刷新
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n监控已退出")
        return

if __name__ == '__main__':
    main()
