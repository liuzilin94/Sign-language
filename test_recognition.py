"""
手语识别功能测试脚本
使用用户提供的测试视频进行识别测试
"""
import sys
import os
import io
import time

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np

print("=" * 60)
print("手语识别功能测试")
print("=" * 60)

# 测试视频路径
TEST_VIDEO_PATH = r"C:\Users\刘耔琳\Pictures\Camera Roll\WIN_20260428_09_07_12_Pro.mp4"

print(f"\n测试视频: {TEST_VIDEO_PATH}")
print(f"视频存在: {os.path.exists(TEST_VIDEO_PATH)}")

# 1. MediaPipe手部检测测试
print("\n" + "-" * 40)
print("1. MediaPipe手部检测测试")
print("-" * 40)

try:
    from utils.mediapipe_compat import HandLandmarkDetector
    
    detector = HandLandmarkDetector(max_num_hands=2, running_mode="video")
    
    # 测试图片检测
    import cv2
    cap = cv2.VideoCapture(TEST_VIDEO_PATH)
    
    frame_count = 0
    detected_frames = 0
    start_time = time.time()
    
    while frame_count < 30:  # 测试前30帧
        ret, frame = cap.read()
        if not ret:
            break
        
        timestamp_ms = int(frame_count * 1000 / 30)
        detected = detector.detect(frame, timestamp_ms=timestamp_ms)
        
        if detected and len(detected) > 0:
            detected_frames += 1
        
        frame_count += 1
    
    cap.release()
    elapsed = time.time() - start_time
    
    print(f"  检测帧数: {frame_count}")
    print(f"  检测到手部帧数: {detected_frames}")
    print(f"  检测率: {detected_frames/frame_count*100:.1f}%")
    print(f"  检测耗时: {elapsed:.2f}秒")
    print(f"  每帧平均: {elapsed/frame_count*1000:.1f}ms")
    
    if detected_frames > 0:
        print("  [PASS] MediaPipe手部检测")
    else:
        print("  [FAIL] 未检测到手部（可能是视频角度问题）")
    
    detector.close()
    
except Exception as e:
    print(f"  [ERROR] MediaPipe测试失败: {e}")

# 2. 特征提取测试
print("\n" + "-" * 40)
print("2. 特征提取测试")
print("-" * 40)

try:
    from data.preprocessing import FeatureExtractor
    
    extractor = FeatureExtractor(seq_length=30)
    
    start_time = time.time()
    features = extractor.extract_from_video(TEST_VIDEO_PATH)
    elapsed = time.time() - start_time
    
    print(f"  特征形状: {features.shape}")
    print(f"  特征维度: {features.shape[1]}")
    print(f"  序列长度: {features.shape[0]}")
    print(f"  提取耗时: {elapsed:.2f}秒")
    
    # 检查特征是否有效
    if features is not None and features.shape == (30, 84):
        # 检查是否有非零值
        nonzero_ratio = np.count_nonzero(features) / features.size
        print(f"  非零值比例: {nonzero_ratio:.2%}")
        
        if nonzero_ratio > 0.1:
            print("  [PASS] 特征提取成功")
        else:
            print("  [WARN] 特征值过低，可能未检测到手部")
    else:
        print(f"  [FAIL] 特征形状错误，期望(30, 84)")
    
except Exception as e:
    print(f"  [ERROR] 特征提取失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 模型加载测试（如果模型存在）
print("\n" + "-" * 40)
print("3. 模型加载测试")
print("-" * 40)

model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'best_isolated_model.pth')
corpus_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'corpus.txt')

print(f"  模型文件: {model_path}")
print(f"  模型存在: {os.path.exists(model_path)}")
print(f"  词汇表: {corpus_path}")
print(f"  词汇表存在: {os.path.exists(corpus_path)}")

if os.path.exists(model_path) and os.path.exists(corpus_path):
    try:
        from inference.predictor import IsolatedWordPredictor
        
        print("\n  正在加载模型...")
        start_time = time.time()
        
        predictor = IsolatedWordPredictor(
            model_type='cnn_lstm',
            model_path=model_path,
            corpus_file=corpus_path
        )
        
        load_time = time.time() - start_time
        print(f"  模型加载耗时: {load_time:.2f}秒")
        
        print(f"  词汇数量: {len(predictor.corpus_by_idx)}")
        print(f"  设备: {predictor.config.device}")
        
        print("  [PASS] 模型加载成功")
        
        # 4. 识别测试
        print("\n" + "-" * 40)
        print("4. 手语识别测试")
        print("-" * 40)
        
        try:
            features = extractor.extract_from_video(TEST_VIDEO_PATH)
            
            start_time = time.time()
            result = predictor._predict(features, return_prob=True, top_k=5)
            infer_time = time.time() - start_time
            
            if isinstance(result, dict):
                predicted = result.get('predicted', '未知')
                confidence = result.get('confidence', 0)
                target_confidence = result.get('target_confidence', 0)
                
                print(f"  预测结果: {predicted}")
                print(f"  预测置信度: {confidence:.2%}")
                print(f"  目标置信度: {target_confidence:.2%}")
            else:
                predicted, confidence = result
                print(f"  预测结果: {predicted}")
                print(f"  置信度: {confidence:.2%}")
            
            print(f"  推理耗时: {infer_time*1000:.1f}ms")
            print("  [PASS] 识别完成")
            
        except Exception as e:
            print(f"  [ERROR] 识别失败: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"  [ERROR] 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("  [SKIP] 模型文件或词汇表不存在，跳过模型测试")

# 5. 系统信息
print("\n" + "-" * 40)
print("5. 系统信息")
print("-" * 40)
print(f"  PyTorch版本: {torch.__version__}")
print(f"  CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
print(f"  CPU: {os.environ.get('PROCESSOR_IDENTIFIER', 'Unknown')}")

print("\n" + "=" * 60)
print("手语识别测试完成")
print("=" * 60)
