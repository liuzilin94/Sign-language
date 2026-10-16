"""Feature extraction utilities for hand-keypoint sequences."""

import os
import pickle
import tempfile
from multiprocessing import Pool

import av  # PyAV: 读取 OpenCV 不支持的 webm/vp8/vp9
import cv2
import numpy as np
from tqdm import tqdm

from utils.mediapipe_compat import HandLandmarkDetector, draw_hand_landmarks


class FeatureExtractor:
    """Extracts fixed-length hand-keypoint sequences from videos or frames."""

    def __init__(self, seq_length=30):
        self.seq_length = seq_length

    def _prepare_frames(self, frames):
        if not frames:
            raise ValueError("视频中未读取到有效帧，无法提取手部关键点。")

        total_frames = len(frames)
        if total_frames >= self.seq_length:
            indices = np.linspace(0, total_frames - 1, self.seq_length, dtype=int)
            return [frames[i] for i in indices]

        return frames + [frames[-1]] * (self.seq_length - total_frames)

    def _frames_to_features(self, frames, fps=30):
        prepared_frames = self._prepare_frames(frames)
        detector = HandLandmarkDetector(max_num_hands=2, running_mode="video")
        hand_features = []

        try:
            for frame_features in detector.detect_frames(prepared_frames):
                if len(frame_features) < 84:
                    frame_features.extend([0] * (84 - len(frame_features)))
                hand_features.append(frame_features[:84])
        finally:
            detector.close()

        return np.array(hand_features, dtype=np.float32)

    def extract_from_video(self, video_path):
        feature_cache_dir = "features"
        cache_filename = os.path.join(
            feature_cache_dir,
            f"{os.path.basename(video_path).split('.')[0]}.pkl",
        )

        if os.path.exists(cache_filename):
            with open(cache_filename, "rb") as f:
                return pickle.load(f)

        frames = []
        try:
            # 优先用 PyAV 读取（支持 webm/vp8/vp9 等 OpenCV 不支持的格式）
            container = av.open(video_path)
            vs = container.streams.video[0]
            vs.thread_type = 'AUTO'
            for frame in container.decode(vs):
                img = frame.to_ndarray(format='bgr24')
                frames.append(img)
            container.close()
        except Exception:
            # Fallback: 尝试用 OpenCV
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()

        if not frames:
            raise ValueError(f"视频中未读取到有效帧: {video_path}")

        hand_features = self._frames_to_features(frames, fps=30)

        os.makedirs(feature_cache_dir, exist_ok=True)
        with open(cache_filename, "wb") as f:
            pickle.dump(hand_features, f)

        return hand_features

    def extract_from_frames(self, frames):
        return self._frames_to_features(frames, fps=30)

    def extract_from_jpg_sequence(self, frames_dir):
        """从jpg图像序列目录提取关键点特征

        参数:
            frames_dir (str): 包含jpg图像序列的目录路径

        返回:
            np.ndarray: 关键点特征序列，形状为 (seq_length, 84)
        """
        feature_cache_dir = "features"
        cache_filename = os.path.join(
            feature_cache_dir,
            f"{os.path.basename(frames_dir)}.pkl",
        )

        # 检查缓存
        if os.path.exists(cache_filename):
            with open(cache_filename, "rb") as f:
                return pickle.load(f)

        # 获取所有jpg文件并排序
        jpg_files = sorted([
            f for f in os.listdir(frames_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])

        if not jpg_files:
            raise ValueError(f"目录中没有找到jpg文件: {frames_dir}")

        # 读取图像
        frames = []
        for jpg_file in jpg_files:
            img_path = os.path.join(frames_dir, jpg_file)
            img = cv2.imread(img_path)
            if img is not None:
                frames.append(img)

        if not frames:
            raise ValueError(f"无法读取任何图像文件: {frames_dir}")

        # 提取特征
        hand_features = self._frames_to_features(frames, fps=30)

        # 保存缓存
        os.makedirs(feature_cache_dir, exist_ok=True)
        with open(cache_filename, "wb") as f:
            pickle.dump(hand_features, f)

        return hand_features

    def extract_from_webcam(self, duration=3):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return None

        frames = []
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30
        total_frames = int(fps * duration)
        detector = HandLandmarkDetector(max_num_hands=2, running_mode="video")

        print(f"请在 {duration} 秒内做出手语动作...")

        try:
            while len(frames) < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp_ms = int(len(frames) * 1000 / fps)
                detected_hands = detector.detect(frame, timestamp_ms=timestamp_ms)
                preview_frame = draw_hand_landmarks(frame, detected_hands)

                remaining_time = max(0.0, duration - len(frames) / fps)
                cv2.putText(
                    preview_frame,
                    f"Remaining: {remaining_time:.1f}s",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                cv2.imshow("Hand Sign Input", preview_frame)
                frames.append(frame.copy())

                if cv2.waitKey(1) == 27:
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            detector.close()

        return self.extract_from_frames(frames)


def process_single_video(video_path):
    extractor = FeatureExtractor()
    return extractor.extract_from_video(video_path)


def process_single_jpg_sequence(frames_dir):
    """处理单个jpg序列目录

    参数:
        frames_dir (str): jpg序列目录路径

    返回:
        tuple: (目录路径, 特征数组)
    """
    extractor = FeatureExtractor()
    try:
        features = extractor.extract_from_jpg_sequence(frames_dir)
        return frames_dir, features
    except Exception as e:
        print(f"处理序列 {frames_dir} 时出错: {e}")
        return frames_dir, None


def preprocess_isolated_features(video_paths, n_jobs=-1):
    """批量预处理孤立词数据集的jpg序列

    参数:
        video_paths (List[str]): jpg序列目录路径列表
        n_jobs (int): 并行进程数，-1表示使用所有CPU核心
    """
    print("预处理并缓存所有jpg序列特征...")
    feature_cache_dir = "features"
    os.makedirs(feature_cache_dir, exist_ok=True)

    # 检查已处理和待处理的序列
    processed = []
    pending = []
    for path in video_paths:
        cache_filename = os.path.join(
            feature_cache_dir,
            f"{os.path.basename(path)}.pkl",
        )
        if os.path.exists(cache_filename):
            processed.append(path)
        else:
            pending.append(path)

    print(f"已处理序列: {len(processed)}/{len(video_paths)}")
    print(f"待处理序列: {len(pending)}/{len(video_paths)}")

    if not pending:
        print("所有序列已处理完毕。")
        return

    # 并行处理
    if n_jobs != 1 and len(pending) > 1:
        try:
            with Pool(processes=n_jobs) as pool:
                list(tqdm(
                    pool.imap(process_single_jpg_sequence, pending),
                    total=len(pending),
                    desc="提取特征"
                ))
        except Exception as exc:
            print(f"并行处理出错: {exc}，切换到顺序处理")
            for path in tqdm(pending, desc="提取特征"):
                process_single_jpg_sequence(path)
    else:
        for path in tqdm(pending, desc="提取特征"):
            process_single_jpg_sequence(path)

    print("预处理完成！")


def preprocess_all_videos(video_paths, n_jobs=-1):
    print("预处理并缓存所有视频特征...")
    feature_cache_dir = "features"
    os.makedirs(feature_cache_dir, exist_ok=True)

    processed_videos = []
    pending_videos = []
    for video_path in video_paths:
        cache_filename = os.path.join(
            feature_cache_dir,
            f"{os.path.basename(video_path).split('.')[0]}.pkl",
        )
        if os.path.exists(cache_filename):
            processed_videos.append(video_path)
        else:
            pending_videos.append(video_path)

    print(f"已处理视频: {len(processed_videos)}/{len(video_paths)}")
    print(f"待处理视频: {len(pending_videos)}/{len(video_paths)}")

    if not pending_videos:
        print("所有视频已处理完毕。")
        return

    if n_jobs != 1 and len(pending_videos) > 1:
        try:
            with Pool(processes=n_jobs) as pool:
                list(tqdm(pool.imap(process_single_video, pending_videos), total=len(pending_videos)))
        except Exception as exc:
            print(f"并行处理出错: {exc}，切换到顺序处理")
            for video_path in tqdm(pending_videos):
                process_single_video(video_path)
    else:
        for video_path in tqdm(pending_videos):
            process_single_video(video_path)

    print("预处理完成！")
