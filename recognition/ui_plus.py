import os
import sys
import threading
import time
from datetime import datetime

import cv2
import qdarkstyle
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QBrush, QImage
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QTextEdit, QProgressBar, QFileDialog, QFrame,
                             QGroupBox, QMessageBox, QSlider, QSpinBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 尝试导入真实预测器（不允许静默降级为模拟预测）
try:
    from inference.predictor import HandSignPredictor, IsolatedWordPredictor

    PREDICTOR_AVAILABLE = True
    PREDICTOR_IMPORT_ERROR = ""
    print("成功导入真实预测器")
except ImportError as e:
    HandSignPredictor = None  # type: ignore[assignment]
    IsolatedWordPredictor = None  # type: ignore[assignment]
    PREDICTOR_AVAILABLE = False
    PREDICTOR_IMPORT_ERROR = str(e)
    print(f"❌ 无法导入真实预测器: {e}")


class VideoPreviewThread(QThread):
    """视频预览线程 - 增强版本"""
    preview_signal = pyqtSignal(QPixmap)
    error_signal = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            print(f"尝试打开视频: {self.video_path}")

            # 尝试不同的后端
            backends = [
                cv2.CAP_FFMPEG,
                cv2.CAP_ANY,
                cv2.CAP_MSMF,
                cv2.CAP_DSHOW
            ]

            cap = None
            for backend in backends:
                cap = cv2.VideoCapture(self.video_path, backend)
                if cap.isOpened():
                    print(f"使用后端 {backend} 成功打开视频")
                    break
                if cap:
                    cap.release()

            if not cap or not cap.isOpened():
                self.error_signal.emit("无法打开视频文件，可能格式不支持或文件损坏")
                return

            # 尝试读取多帧，因为有些视频第一帧可能是空的
            ret = False
            frame = None
            for i in range(10):  # 尝试10帧
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    break
                print(f"第 {i + 1} 帧读取失败，继续尝试...")

            if not ret or frame is None:
                self.error_signal.emit("无法读取视频帧，视频可能已损坏")
                cap.release()
                return

            print(f"成功读取视频帧，形状: {frame.shape}")

            # 调整帧大小，保持宽高比
            h, w = frame.shape[:2]
            target_width = 800
            target_height = 600

            # 计算缩放比例
            scale = min(target_width / w, target_height / h)
            new_width = int(w * scale)
            new_height = int(h * scale)

            frame = cv2.resize(frame, (new_width, new_height))

            # 处理不同的图像格式
            if len(frame.shape) == 3:
                if frame.shape[2] == 3:  # BGR格式
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif frame.shape[2] == 4:  # BGRA格式
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            elif len(frame.shape) == 2:  # 灰度图像
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

            # 确保图像数据有效
            if frame is None or frame.size == 0:
                self.error_signal.emit("视频帧数据无效")
                cap.release()
                return

            h, w, ch = frame.shape
            bytes_per_line = ch * w

            # 创建QImage
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            if qt_image.isNull():
                self.error_signal.emit("创建QImage失败")
                cap.release()
                return

            pixmap = QPixmap.fromImage(qt_image)
            if pixmap.isNull():
                self.error_signal.emit("创建QPixmap失败")
                cap.release()
                return

            # 发送预览图像
            self.preview_signal.emit(pixmap)
            print("视频预览加载成功")

            cap.release()

        except Exception as e:
            error_msg = f"预览视频失败: {str(e)}"
            print(error_msg)
            self.error_signal.emit(error_msg)


class VideoPlaybackThread(QThread):
    """视频播放线程 - 用于连续播放视频"""
    frame_signal = pyqtSignal(QPixmap)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.is_playing = False

    def run(self):
        try:
            print(f"开始播放视频: {self.video_path}")

            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error_signal.emit("无法打开视频文件")
                return

            self.is_playing = True

            # 获取视频的FPS
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                fps = 30  # 默认FPS

            frame_delay = 1.0 / fps

            while self.is_playing:
                ret, frame = cap.read()
                if not ret:
                    # 视频播放完毕，重新开始
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                # 调整帧大小，保持宽高比
                h, w = frame.shape[:2]
                target_width = 800
                target_height = 600

                scale = min(target_width / w, target_height / h)
                new_width = int(w * scale)
                new_height = int(h * scale)

                frame = cv2.resize(frame, (new_width, new_height))

                # 转换为RGB格式
                if len(frame.shape) == 3:
                    if frame.shape[2] == 3:  # BGR格式
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    elif frame.shape[2] == 4:  # BGRA格式
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                elif len(frame.shape) == 2:  # 灰度图像
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

                # 创建QImage并转换为QPixmap
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)

                # 发送帧
                self.frame_signal.emit(pixmap)

                # 根据FPS控制播放速度
                time.sleep(frame_delay)

            cap.release()
            self.finished_signal.emit()

        except Exception as e:
            error_msg = f"播放视频失败: {str(e)}"
            print(error_msg)
            self.error_signal.emit(error_msg)

    def stop(self):
        self.is_playing = False


class VideoThread(QThread):
    """摄像头线程"""
    frame_signal = pyqtSignal(QPixmap)
    finished_signal = pyqtSignal()
    save_video_signal = pyqtSignal(str)

    def __init__(self, duration=3):
        super().__init__()
        self.duration = duration
        self.is_running = False
        self.out = None
        self.save_path = None

    def run(self):
        self.is_running = True
        cap = cv2.VideoCapture(0)

        # 检查摄像头是否成功打开
        if not cap.isOpened():
            self.finished_signal.emit()
            return

        # 获取摄像头参数
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 创建保存视频的写入器
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_path = f"webcam_capture_{timestamp}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.save_path, fourcc, fps, (width, height))

        start_time = time.time()

        while self.is_running:
            ret, frame = cap.read()
            if ret:
                # 保存帧到视频文件
                self.out.write(frame)

                # 转换为RGB格式显示
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                self.frame_signal.emit(pixmap)

            # 检查录制时长
            if time.time() - start_time >= self.duration:
                break

            time.sleep(0.03)  # 约30fps

        # 释放资源
        cap.release()
        if self.out:
            self.out.release()
        self.save_video_signal.emit(self.save_path)
        self.finished_signal.emit()

    def stop(self):
        self.is_running = False


class PredictionThread(QThread):
    """预测线程"""
    result_signal = pyqtSignal(str, float)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, predictor, video_path, is_webcam=False, duration=3):
        super().__init__()
        self.predictor = predictor
        self.video_path = video_path
        self.is_webcam = is_webcam
        self.duration = duration

    def run(self):
        try:
            if self.is_webcam:
                # 摄像头预测
                result, prob = self.predictor.predict_webcam(duration=self.duration, return_prob=True)
            else:
                # 视频文件预测
                result, prob = self.predictor.predict(self.video_path, return_prob=True)

            self.result_signal.emit(result, prob)
        except Exception as e:
            self.error_signal.emit(f"预测失败: {str(e)}")
        finally:
            self.finished_signal.emit()


class MediaPlayerPreview:
    """使用QMediaPlayer进行视频预览"""

    def __init__(self, video_label):
        self.video_label = video_label
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()

        # 将视频输出设置到QVideoWidget
        self.media_player.setVideoOutput(self.video_widget)

        # 连接信号
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.error.connect(self.on_media_error)

    def preview_video(self, video_path):
        """预览视频"""
        try:
            media_content = QMediaContent(QUrl.fromLocalFile(video_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()
        except Exception as e:
            print(f"QMediaPlayer预览失败: {e}")

    def on_media_status_changed(self, status):
        """媒体状态改变"""
        if status == QMediaPlayer.LoadedMedia:
            print("媒体加载成功")
        elif status == QMediaPlayer.InvalidMedia:
            print("无效的媒体文件")

    def on_media_error(self, error):
        """媒体错误处理"""
        error_msg = f"媒体播放器错误: {error}"
        print(error_msg)


class HandSignUI(QMainWindow):
    """手语识别与翻译系统主界面"""

    # 定义信号
    show_error_signal = pyqtSignal(str)
    prediction_finished_signal = pyqtSignal()
    update_result_signal = pyqtSignal(str, float)  # 用于更新预测结果的信号

    def __init__(self):
        super().__init__()
        self.predictor = None
        self.video_thread = None
        self.preview_thread = None
        self.playback_thread = None
        self.prediction_thread = None
        self.is_recording = False
        self.current_video_path = None
        self.media_preview = None
        self.use_opencv_preview = True  # 默认使用OpenCV预览
        self.is_playing_video = False

        # 连接信号和槽
        self.show_error_signal.connect(self.show_error)
        self.prediction_finished_signal.connect(self.on_prediction_finished)
        self.update_result_signal.connect(self.update_prediction_result)

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("手语识别与翻译系统")
        # 增加窗口初始大小
        self.setGeometry(100, 100, 1800, 1400)
        self.setMinimumSize(1600, 1000)

        # 设置应用图标
        self.setWindowIcon(QIcon(self.create_icon()))

        # 设置样式
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)

        # 右侧显示面板
        display_panel = self.create_display_panel()
        main_layout.addWidget(display_panel, 2)

        # 初始化预测器
        self.init_predictor()

    def create_control_panel(self):
        """创建左侧控制面板"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setMaximumWidth(450)  # 增加控制面板宽度

        layout = QVBoxLayout(panel)
        layout.setSpacing(20)  # 增加组件间距
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距

        # 标题
        title = QLabel("手语识别与翻译系统")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)  # 增大字体
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("padding: 25px; color: #2ecc71; background-color: #34495e; border-radius: 8px;")
        layout.addWidget(title)

        # 模型选择组
        model_group = QGroupBox("模型设置")
        model_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        model_layout = QVBoxLayout(model_group)
        model_layout.setSpacing(12)

        model_label = QLabel("选择模型类型:")
        model_label.setStyleSheet("font-size: 13px;")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["BiLSTM", "Transformer", "CNN_LSTM", "GRU", "集成模型"])
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        self.model_combo.setStyleSheet("padding: 10px; font-size: 13px;")
        model_layout.addWidget(self.model_combo)

        # 显示预测器状态
        self.predictor_status = QLabel("预测器状态: 未初始化")
        self.predictor_status.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 5px;")
        model_layout.addWidget(self.predictor_status)

        layout.addWidget(model_group)

        # 输入源组
        input_group = QGroupBox("输入源")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(18)

        # 视频文件输入部分
        file_section = QVBoxLayout()
        file_label = QLabel("视频文件:")
        file_label.setStyleSheet("font-weight: bold; color: #ecf0f1; font-size: 13px;")
        file_section.addWidget(file_label)

        file_btn_layout = QHBoxLayout()
        self.file_btn = QPushButton("选择视频文件")
        self.file_btn.clicked.connect(self.select_video_file)
        self.file_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        file_btn_layout.addWidget(self.file_btn)

        file_btn_layout.addStretch()
        file_section.addLayout(file_btn_layout)

        self.file_label = QLabel("未选择文件")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet(
            "color: #95a5a6; font-size: 12px; padding: 8px; background-color: #2c3e50; border-radius: 4px; min-height: 40px;")
        file_section.addWidget(self.file_label)

        # 视频控制按钮
        video_control_layout = QHBoxLayout()
        self.play_btn = QPushButton("播放视频")
        self.play_btn.clicked.connect(self.toggle_video_playback)
        self.play_btn.setEnabled(False)
        self.play_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #3498db; color: white;")
        video_control_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("停止播放")
        self.stop_btn.clicked.connect(self.stop_video_playback)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #e74c3c; color: white;")
        video_control_layout.addWidget(self.stop_btn)

        file_section.addLayout(video_control_layout)
        input_layout.addLayout(file_section)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #7f8c8d; margin: 10px 0;")
        input_layout.addWidget(separator)

        # 摄像头输入部分
        camera_section = QVBoxLayout()
        camera_label = QLabel("摄像头:")
        camera_label.setStyleSheet("font-weight: bold; color: #ecf0f1; font-size: 13px;")
        camera_section.addWidget(camera_label)

        # 录制时长设置
        duration_layout = QHBoxLayout()
        duration_text = QLabel("录制时长:")
        duration_text.setStyleSheet("color: #bdc3c7; font-size: 13px;")
        duration_layout.addWidget(duration_text)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 10)
        self.duration_spin.setValue(3)
        self.duration_spin.setSuffix(" 秒")
        self.duration_spin.setStyleSheet("padding: 8px; font-size: 13px;")
        duration_layout.addWidget(self.duration_spin)

        duration_layout.addStretch()
        camera_section.addLayout(duration_layout)

        self.camera_btn = QPushButton("开始摄像头录制")
        self.camera_btn.clicked.connect(self.toggle_camera_recording)
        self.camera_btn.setStyleSheet("padding: 10px; background-color: #3498db; color: white; font-size: 13px;")
        camera_section.addWidget(self.camera_btn)

        input_layout.addLayout(camera_section)

        layout.addWidget(input_group)

        # 预测结果组
        result_group = QGroupBox("预测结果")
        result_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        result_layout = QVBoxLayout(result_group)
        result_layout.setSpacing(12)

        result_label = QLabel("识别结果:")
        result_label.setStyleSheet("font-weight: bold; color: #ecf0f1; font-size: 13px;")
        result_layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(140)  # 增加高度
        self.result_text.setStyleSheet(
            "padding: 12px; background-color: #2c3e50; border: 1px solid #34495e; border-radius: 4px; font-size: 13px;")
        result_layout.addWidget(self.result_text)

        # 置信度
        confidence_layout = QVBoxLayout()
        confidence_label = QLabel("置信度:")
        confidence_label.setStyleSheet("font-weight: bold; color: #ecf0f1; font-size: 13px;")
        confidence_layout.addWidget(confidence_label)

        confidence_bar_layout = QHBoxLayout()
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 6px;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
        """)
        confidence_bar_layout.addWidget(self.confidence_bar)

        self.confidence_label = QLabel("0%")
        self.confidence_label.setStyleSheet("font-weight: bold; color: #ecf0f1; min-width: 50px; font-size: 13px;")
        confidence_bar_layout.addWidget(self.confidence_label)

        confidence_layout.addLayout(confidence_bar_layout)
        result_layout.addLayout(confidence_layout)

        layout.addWidget(result_group)

        # 操作按钮
        self.predict_btn = QPushButton("开始预测")
        self.predict_btn.clicked.connect(self.start_prediction)
        self.predict_btn.setEnabled(False)
        self.predict_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        layout.addWidget(self.predict_btn)

        # 历史记录组
        history_group = QGroupBox("历史记录")
        history_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        history_layout = QVBoxLayout(history_group)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet(
            "background-color: #2c3e50; border: 1px solid #34495e; border-radius: 4px; font-size: 12px;")
        history_layout.addWidget(self.history_text)

        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setStyleSheet("padding: 10px; font-size: 13px;")
        history_layout.addWidget(clear_btn)

        layout.addWidget(history_group)

        # 底部信息
        info_label = QLabel("© 22信管7綦玉华 手语识别与翻译系统")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 15px;")
        layout.addWidget(info_label)

        layout.addStretch()

        return panel

    def create_display_panel(self):
        """创建右侧显示面板"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 视频显示区域
        display_group = QGroupBox("视频预览")
        display_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        display_layout = QVBoxLayout(display_group)
        display_layout.setSpacing(15)

        # 创建视频标签并设置固定大小
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 600)  # 使用最小大小确保有足够空间
        self.video_label.setStyleSheet("""
            background-color: #2c3e50; 
            border: 2px solid #34495e; 
            border-radius: 8px;
            color: #95a5a6;
            font-size: 18px;
        """)
        self.video_label.setText("视频预览区域\n\n请选择视频文件或使用摄像头录制")
        self.video_label.setScaledContents(True)  # 允许图像缩放以适应标签大小
        display_layout.addWidget(self.video_label)

        # 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #bdc3c7; padding: 8px; font-size: 13px;")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.recording_indicator = QLabel()
        self.recording_indicator.setVisible(False)
        self.recording_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 8px; font-size: 13px;")
        status_layout.addWidget(self.recording_indicator)

        self.playing_indicator = QLabel()
        self.playing_indicator.setVisible(False)
        self.playing_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; padding: 8px; font-size: 13px;")
        status_layout.addWidget(self.playing_indicator)

        display_layout.addLayout(status_layout)

        layout.addWidget(display_group)

        return panel

    def create_icon(self):
        """创建应用图标（简单实现）"""
        # 这里可以替换为实际的图标文件
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        return pixmap

    def init_predictor(self):
        """初始化预测器 - 增强版本"""
        try:
            model_type = self.model_combo.currentText().lower()
            print(f"正在初始化预测器，模型类型: {model_type}")

            # 尝试使用真实预测器
            self.predictor = HandSignPredictor(model_type=model_type)

            # 更新状态显示
            if PREDICTOR_AVAILABLE:
                self.predictor_status.setText(f"预测器状态: {model_type}模型已加载")
                self.predictor_status.setStyleSheet("color: #2ecc71; font-size: 12px; padding: 5px;")
                print(f"成功加载真实{model_type}预测器")
            else:
                self.predictor_status.setText(f"预测器状态: 使用{model_type}模拟预测器")
                self.predictor_status.setStyleSheet("color: #f39c12; font-size: 12px; padding: 5px;")
                print(f"使用{model_type}模拟预测器")

            self.status_label.setText(f"模型 '{model_type}' 加载成功")
            self.predict_btn.setEnabled(True)

        except Exception as e:
            # 如果真实预测器初始化失败，则使用模拟预测器
            error_msg = f"真实预测器加载失败: {str(e)}，将使用模拟预测器"
            print(error_msg)

            # 使用模拟预测器
            model_type = self.model_combo.currentText().lower()
            self.predictor = HandSignPredictor(model_type=model_type)  # 这里会使用模拟预测器类
            self.predictor_status.setText(f"预测器状态: 使用{model_type}模拟预测器（真实预测器加载失败）")
            self.predictor_status.setStyleSheet("color: #f39c12; font-size: 12px; padding: 5px;")
            self.status_label.setText(f"模型 '{model_type}' 模拟模式")
            self.predict_btn.setEnabled(True)

            # 显示警告信息
            self.show_warning(f"真实预测器加载失败: {str(e)}\n已切换到模拟模式，功能受限")

    def on_model_changed(self):
        """模型类型改变时的处理"""
        self.init_predictor()

    def diagnose_video_issue(self, video_path):
        """诊断视频文件问题"""
        if not os.path.exists(video_path):
            return "文件不存在"

        file_size = os.path.getsize(video_path)
        if file_size == 0:
            return "文件大小为0，可能已损坏"

        # 使用OpenCV检查
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "OpenCV无法打开文件"

        # 检查基本属性
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cap.release()

        info = f"文件大小: {file_size} bytes, 帧数: {frame_count}, 分辨率: {width}x{height}, FPS: {fps}"
        print(f"视频信息: {info}")

        if frame_count == 0:
            return "视频没有帧数据"

        return f"视频基本属性正常 - {info}"

    def select_video_file(self):
        """选择视频文件 - 增强版本"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv);;所有文件 (*.*)"
        )

        if file_path:
            # 运行诊断
            diagnosis = self.diagnose_video_issue(file_path)
            print(f"诊断结果: {diagnosis}")

            if "正常" not in diagnosis:
                self.show_warning(f"视频文件可能有问题: {diagnosis}")

            self.file_label.setText(os.path.basename(file_path))
            self.current_video_path = file_path
            self.status_label.setText(f"已选择文件: {os.path.basename(file_path)}")

            # 启用播放按钮
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

            # 立即显示视频预览
            self.preview_video(file_path)

    def preview_video(self, video_path):
        """预览视频 - 增强版本"""
        # 如果已有预览线程在运行，先停止它
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.terminate()
            self.preview_thread.wait()

        # 停止任何正在播放的视频
        self.stop_video_playback()

        if self.use_opencv_preview:
            # 使用OpenCV预览
            self.preview_thread = VideoPreviewThread(video_path)
            self.preview_thread.preview_signal.connect(self.update_video_preview)
            self.preview_thread.error_signal.connect(self.on_opencv_preview_failed)
            self.preview_thread.start()
            self.status_label.setText("正在使用OpenCV加载视频预览...")
        else:
            # 使用QMediaPlayer预览
            self.use_media_player_preview(video_path)

    def on_opencv_preview_failed(self, error_msg):
        """OpenCV预览失败时的处理"""
        print(f"OpenCV预览失败: {error_msg}")
        self.status_label.setText("OpenCV预览失败，尝试备用方案...")

        # 切换到QMediaPlayer方案
        self.use_opencv_preview = False
        if hasattr(self, 'current_video_path'):
            self.use_media_player_preview(self.current_video_path)

    def use_media_player_preview(self, video_path):
        """使用QMediaPlayer进行预览"""
        try:
            if self.media_preview is None:
                self.media_preview = MediaPlayerPreview(self.video_label)

            # 这里需要将QVideoWidget添加到界面中
            if self.video_label.layout() is None:
                layout = QVBoxLayout(self.video_label)
                layout.addWidget(self.media_preview.video_widget)
                layout.setContentsMargins(0, 0, 0, 0)

            self.media_preview.preview_video(video_path)
            self.status_label.setText("正在使用媒体播放器加载视频...")

        except Exception as e:
            error_msg = f"备用预览方案也失败了: {str(e)}"
            print(error_msg)
            self.show_error_signal.emit(error_msg)

    def update_video_preview(self, pixmap):
        """更新视频预览"""
        # 直接设置QPixmap到标签
        if not pixmap.isNull():
            self.video_label.setPixmap(pixmap)
            self.status_label.setText("视频预览已加载")
            print("视频预览更新成功")  # 调试信息
        else:
            self.show_error_signal.emit("获取的视频预览为空")

    def toggle_video_playback(self):
        """切换视频播放状态"""
        if not self.is_playing_video:
            self.start_video_playback()
        else:
            self.stop_video_playback()

    def start_video_playback(self):
        """开始视频播放"""
        if not self.current_video_path:
            self.show_warning("请先选择视频文件")
            return

        # 停止任何正在进行的预览
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.terminate()
            self.preview_thread.wait()

        # 停止摄像头录制
        if self.video_thread and self.video_thread.isRunning():
            self.stop_camera_recording()

        # 创建并启动视频播放线程
        self.playback_thread = VideoPlaybackThread(self.current_video_path)
        self.playback_thread.frame_signal.connect(self.update_video_frame)
        self.playback_thread.error_signal.connect(self.show_error_signal)
        self.playback_thread.finished_signal.connect(self.on_playback_finished)
        self.playback_thread.start()

        self.is_playing_video = True
        self.play_btn.setText("暂停播放")
        self.play_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #f39c12; color: white;")
        self.stop_btn.setEnabled(True)
        self.playing_indicator.setText("▶ 播放中")
        self.playing_indicator.setVisible(True)
        self.status_label.setText("视频播放中...")

    def stop_video_playback(self):
        """停止视频播放"""
        if self.playback_thread and self.playback_thread.isRunning():
            self.playback_thread.stop()
            self.playback_thread.wait()

        self.is_playing_video = False
        self.play_btn.setText("播放视频")
        self.play_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #3498db; color: white;")
        self.stop_btn.setEnabled(False)
        self.playing_indicator.setVisible(False)
        self.status_label.setText("视频播放已停止")

    def on_playback_finished(self):
        """播放完成后的处理"""
        self.is_playing_video = False
        self.play_btn.setText("播放视频")
        self.play_btn.setStyleSheet("padding: 8px; font-size: 12px; background-color: #3498db; color: white;")
        self.stop_btn.setEnabled(False)
        self.playing_indicator.setVisible(False)
        self.status_label.setText("视频播放完成")

    def toggle_camera_recording(self):
        """切换摄像头录制状态"""
        if not self.is_recording:
            self.start_camera_recording()
        else:
            self.stop_camera_recording()

    def start_camera_recording(self):
        """开始摄像头录制"""
        # 停止视频播放
        self.stop_video_playback()

        if self.video_thread and self.video_thread.isRunning():
            return

        self.is_recording = True
        self.camera_btn.setText("停止录制")
        self.camera_btn.setStyleSheet("padding: 10px; background-color: #e74c3c; color: white; font-size: 13px;")
        self.recording_indicator.setText("● 录制中")
        self.recording_indicator.setVisible(True)
        self.status_label.setText("摄像头录制中...")

        # 启动摄像头线程
        self.video_thread = VideoThread(duration=self.duration_spin.value())
        self.video_thread.frame_signal.connect(self.update_video_frame)
        self.video_thread.finished_signal.connect(self.on_recording_finished)
        self.video_thread.save_video_signal.connect(self.on_video_saved)
        self.video_thread.start()

    def stop_camera_recording(self):
        """停止摄像头录制"""
        if self.video_thread:
            self.video_thread.stop()

    def on_video_saved(self, save_path):
        """摄像头视频保存完成"""
        self.current_video_path = save_path
        self.file_label.setText(os.path.basename(save_path))
        self.status_label.setText(f"摄像头视频已保存: {save_path}")

    def on_recording_finished(self):
        """录制完成后的处理"""
        self.is_recording = False
        self.camera_btn.setText("开始摄像头录制")
        self.camera_btn.setStyleSheet("padding: 10px; background-color: #3498db; color: white; font-size: 13px;")
        self.recording_indicator.setVisible(False)
        self.status_label.setText("录制完成")

    def update_video_frame(self, pixmap):
        """更新视频帧显示"""
        self.video_label.setPixmap(pixmap)

    def start_prediction(self):
        """开始预测"""
        if not hasattr(self, 'current_video_path') or not self.current_video_path:
            self.show_warning("请先选择视频文件或使用摄像头录制")
            return

        # 禁用预测按钮
        self.predict_btn.setEnabled(False)
        self.status_label.setText("正在进行预测，请稍候...")

        # 判断是否是摄像头录制的视频
        is_webcam = self.current_video_path.startswith("webcam_capture")

        # 创建预测线程
        self.prediction_thread = PredictionThread(
            predictor=self.predictor,
            video_path=self.current_video_path,
            is_webcam=is_webcam,
            duration=self.duration_spin.value()
        )

        # 连接信号
        self.prediction_thread.result_signal.connect(self.update_result_signal.emit)
        self.prediction_thread.error_signal.connect(self.show_error_signal.emit)
        self.prediction_thread.finished_signal.connect(self.prediction_finished_signal.emit)

        # 启动线程
        self.prediction_thread.start()

    def update_prediction_result(self, result, confidence):
        """更新预测结果显示"""
        self.result_text.setText(result)
        confidence_percent = int(confidence * 100)
        self.confidence_bar.setValue(confidence_percent)
        self.confidence_label.setText(f"{confidence_percent}%")

        # 添加到历史记录
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"[{timestamp}] 模型: {self.model_combo.currentText()}, 结果: {result}, 置信度: {confidence_percent}%\n"
        self.history_text.append(history_entry)

    def on_prediction_finished(self):
        """预测完成后的处理"""
        self.predict_btn.setEnabled(True)
        self.status_label.setText("预测完成")

    def clear_history(self):
        """清空历史记录"""
        self.history_text.clear()
        self.status_label.setText("历史记录已清空")

    def show_error(self, message):
        """显示错误信息"""
        QMessageBox.critical(self, "错误", message)
        self.status_label.setText(f"错误: {message}")

    def show_warning(self, message):
        """显示警告信息"""
        QMessageBox.warning(self, "警告", message)
        self.status_label.setText(f"警告: {message}")


# ====================== Flask 后端服务 ======================
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app)  # 解决跨域问题

# 全局预测器实例
global_predictor = None


@app.route('/api/init-predictor', methods=['POST'])
def init_predictor_api():
    global global_predictor
    try:
        if not PREDICTOR_AVAILABLE or HandSignPredictor is None:
            return jsonify({
                "success": False,
                "message": "真实预测器导入失败，已禁止使用模拟预测。请安装依赖后重启服务。",
                "predictor_available": False,
                "import_error": PREDICTOR_IMPORT_ERROR,
            }), 500

        data = request.json
        model_type = data.get('model_type', 'bilstm')

        # 强制从项目的 models 目录加载权重（你要求的路径）
        project_root = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(project_root, "models")
        model_path = os.path.join(models_dir, f"best_{model_type}_model.pth")

        if not os.path.exists(model_path):
            return jsonify({
                "success": False,
                "message": f"模型文件不存在：{model_path}",
                "model_type": model_type,
                "models_dir": models_dir,
            }), 500

        # 初始化预测器（显式传入模型路径）
        global_predictor = HandSignPredictor(model_type=model_type, model_path=model_path)

        predictor_module = getattr(global_predictor.__class__, "__module__", "")
        predictor_class = getattr(global_predictor.__class__, "__name__", "HandSignPredictor")
        predictor_impl = "real" if PREDICTOR_AVAILABLE and predictor_module.startswith("inference.") else "mock"
        default_model_path = os.path.abspath(model_path)

        return jsonify({
            "success": True,
            "message": f"预测器初始化成功（{model_type}模型）",
            "model_type": model_type,
            "predictor_available": bool(PREDICTOR_AVAILABLE),
            "predictor_impl": predictor_impl,
            "predictor_class": predictor_class,
            "predictor_module": predictor_module,
            "default_model_path": default_model_path,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"初始化失败：{str(e)}"
        }), 500


@app.route('/api/predict-video', methods=['POST'])
def predict_video_api():
    global global_predictor
    if not global_predictor:
        return jsonify({
            "success": False,
            "message": "请先初始化预测器"
        }), 400

    try:
        if 'video' not in request.files:
            return jsonify({
                "success": False,
                "message": "未上传视频文件"
            }), 400

        video_file = request.files['video']

        # 保存为临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
            video_file.save(video_path)

        # 调用模型预测
        result, confidence = global_predictor.predict(video_path, return_prob=True)

        # 删除临时文件
        os.unlink(video_path)

        predictor_module = getattr(global_predictor.__class__, "__module__", "")
        predictor_impl = "real" if PREDICTOR_AVAILABLE and predictor_module.startswith("inference.") else "mock"
        if predictor_impl != "real":
            return jsonify({
                "success": False,
                "message": "检测到非真实预测器实现，已禁止返回结果。请修复依赖/模型加载问题后重试。",
                "predictor_available": bool(PREDICTOR_AVAILABLE),
                "predictor_impl": predictor_impl,
                "predictor_module": predictor_module,
            }), 500

        # 确保confidence是有效数值
        if confidence != confidence:  # NaN检查
            confidence = 0.0
        confidence = float(max(0.0, min(1.0, confidence)))

        return jsonify({
            "success": True,
            "result": str(result),
            "confidence": confidence,
            "model_type": getattr(global_predictor, "model_type", None),
            "predictor_impl": predictor_impl,
            "predictor_module": predictor_module,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"预测失败：{str(e)}"
        }), 500


@app.route('/api/predict-webcam', methods=['POST'])
def predict_webcam_api():
    global global_predictor
    if not global_predictor:
        return jsonify({
            "success": False,
            "message": "请先初始化预测器"
        }), 400

    try:
        data = request.json
        duration = int(data.get('duration', 3))

        # 调用模型预测
        result, confidence = global_predictor.predict_webcam(duration=duration, return_prob=True)

        predictor_module = getattr(global_predictor.__class__, "__module__", "")
        predictor_impl = "real" if PREDICTOR_AVAILABLE and predictor_module.startswith("inference.") else "mock"
        if predictor_impl != "real":
            return jsonify({
                "success": False,
                "message": "检测到非真实预测器实现，已禁止返回结果。请修复依赖/模型加载问题后重试。",
                "predictor_available": bool(PREDICTOR_AVAILABLE),
                "predictor_impl": predictor_impl,
                "predictor_module": predictor_module,
            }), 500

        # 确保confidence是有效数值
        if confidence != confidence:  # NaN检查
            confidence = 0.0
        confidence = float(max(0.0, min(1.0, confidence)))

        return jsonify({
            "success": True,
            "result": str(result),
            "confidence": confidence,
            "model_type": getattr(global_predictor, "model_type", None),
            "predictor_impl": predictor_impl,
            "predictor_module": predictor_module,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"摄像头预测失败：{str(e)}"
        }), 500


# ====================== 孤立词识别 API ======================

# 全局孤立词预测器实例
global_isolated_predictor = None


@app.route('/api/init-isolated', methods=['POST'])
def init_isolated_predictor_api():
    """初始化孤立词预测器
    
    Request: POST /api/init-isolated
    Body: {"model_type": "cnn_lstm", "model_path": "path/to/model.pth"}
    
    Response: {
        "success": true,
        "message": "孤立词预测器初始化成功",
        "num_classes": 40
    }
    """
    global global_isolated_predictor
    
    try:
        data = request.json or {}
        model_type = data.get('model_type', 'cnn_lstm')
        model_path = data.get('model_path', None)
        
        # 获取项目根目录和路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # 如果没有指定模型路径，使用默认路径
        if model_path is None:
            model_path = os.path.join(project_root, 'models', 'best_isolated_model.pth')
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            return jsonify({
                "success": False,
                "message": f"孤立词模型文件不存在: {model_path}",
                "model_type": model_type,
                "suggestion": "请先运行 python train_isolated.py 训练模型"
            }), 404
        
        # 初始化孤立词预测器
        global_isolated_predictor = IsolatedWordPredictor(
            model_type=model_type,
            model_path=model_path
        )
        
        return jsonify({
            "success": True,
            "message": "孤立词预测器初始化成功",
            "model_type": model_type,
            "model_path": model_path,
            "num_classes": global_isolated_predictor.config.num_classes
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"孤立词预测器初始化失败: {str(e)}"
        }), 500


@app.route('/api/predict-isolated', methods=['POST'])
def predict_isolated_api():
    """孤立词视频识别
    
    Request: POST /api/predict-isolated
    FormData: {"video": <file>}
    
    Response: {
        "success": true,
        "result": "你好",
        "confidence": 0.95
    }
    """
    global global_isolated_predictor
    
    if not global_isolated_predictor:
        return jsonify({
            "success": False,
            "message": "孤立词预测器未初始化，请先调用 /api/init-isolated"
        }), 400
    
    try:
        if 'video' not in request.files:
            return jsonify({
                "success": False,
                "message": "未上传视频文件"
            }), 400
        
        video_file = request.files['video']
        
        # 获取参数
        data = request.form.to_dict()
        top_k = int(data.get('top_k', 1))
        target_index = data.get('target_index')
        if target_index is not None:
            target_index = int(target_index)
        
        # 保存为临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
            video_file.save(video_path)
        
        try:
            # 调用孤立词预测器
            if top_k == 1 and target_index is not None:
                # 使用目标索引模式，返回目标词汇的置信度
                pred_result = global_isolated_predictor.predict_from_video(
                    video_path, return_prob=True, target_index=target_index
                )
                
                if isinstance(pred_result, dict):
                    return jsonify({
                        "success": True,
                        "code": 200,
                        "message": "识别成功",
                        "data": {
                            "predicted": pred_result["predicted"],
                            "confidence": pred_result["confidence"],
                            "target": pred_result["target"],
                            "target_confidence": pred_result["target_confidence"]
                        }
                    })
                else:
                    # 兼容旧格式
                    return jsonify({
                        "success": True,
                        "code": 200,
                        "message": "识别成功",
                        "data": {
                            "result": str(pred_result[0]) if isinstance(pred_result, tuple) else str(pred_result),
                            "confidence": float(pred_result[1]) if isinstance(pred_result, tuple) else 0.0
                        }
                    })
            elif top_k == 1:
                result, confidence = global_isolated_predictor.predict_from_video(
                    video_path, return_prob=True
                )
                
                # 确保confidence是有效数值
                if confidence != confidence:  # NaN检查
                    confidence = 0.0
                confidence = float(max(0.0, min(1.0, confidence)))
                
                return jsonify({
                    "success": True,
                    "code": 200,
                    "message": "识别成功",
                    "data": {
                        "result": str(result),
                        "confidence": confidence
                    }
                })
            else:
                results = global_isolated_predictor.predict_from_video(
                    video_path, return_prob=True, top_k=top_k
                )
                
                # 确保所有概率都是有效数值
                clean_results = []
                for r in results:
                    prob = float(r[1])
                    if prob != prob:  # NaN检查
                        prob = 0.0
                    prob = max(0.0, min(1.0, prob))
                    clean_results.append({"word": str(r[0]), "confidence": prob})
                
                return jsonify({
                    "success": True,
                    "results": clean_results
                })
        finally:
            # 删除临时文件
            if os.path.exists(video_path):
                os.unlink(video_path)
                
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"孤立词视频识别失败: {str(e)}"
        }), 500


@app.route('/api/predict-isolated-webcam', methods=['POST'])
def predict_isolated_webcam_api():
    """孤立词摄像头识别
    
    Request: POST /api/predict-isolated-webcam
    Body: {"duration": 3, "top_k": 1, "target_index": 0}
    
    Response: {
        "success": true,
        "result": "你好",
        "confidence": 0.92,
        "target": "来",
        "target_confidence": 0.85
    }
    """
    global global_isolated_predictor
    
    if not global_isolated_predictor:
        return jsonify({
            "success": False,
            "message": "孤立词预测器未初始化，请先调用 /api/init-isolated"
        }), 400
    
    try:
        data = request.json or {}
        duration = int(data.get('duration', 3))
        top_k = int(data.get('top_k', 1))
        target_index = data.get('target_index')
        if target_index is not None:
            target_index = int(target_index)
        
        # 调用孤立词预测器
        if top_k == 1 and target_index is not None:
            # 使用目标索引模式，返回目标词汇的置信度
            pred_result = global_isolated_predictor.predict_webcam(
                duration=duration, return_prob=True, target_index=target_index
            )
            
            if isinstance(pred_result, dict):
                return jsonify({
                    "success": True,
                    "result": pred_result["predicted"],
                    "confidence": pred_result["confidence"],
                    "target": pred_result["target"],
                    "target_confidence": pred_result["target_confidence"]
                })
            else:
                # 兼容旧格式
                return jsonify({
                    "success": True,
                    "result": str(pred_result[0]) if isinstance(pred_result, tuple) else str(pred_result),
                    "confidence": float(pred_result[1]) if isinstance(pred_result, tuple) else 0.0
                })
        elif top_k == 1:
            result, confidence = global_isolated_predictor.predict_webcam(
                duration=duration, return_prob=True
            )
            
            # 确保confidence是有效数值
            if confidence != confidence:  # NaN检查
                confidence = 0.0
            confidence = float(max(0.0, min(1.0, confidence)))
            
            return jsonify({
                "success": True,
                "result": str(result),
                "confidence": confidence
            })
        else:
            results = global_isolated_predictor.predict_webcam(
                duration=duration, return_prob=True, top_k=top_k
            )
            
            # 确保所有概率都是有效数值
            clean_results = []
            for r in results:
                prob = float(r[1])
                if prob != prob:  # NaN检查
                    prob = 0.0
                prob = max(0.0, min(1.0, prob))
                clean_results.append({"word": str(r[0]), "confidence": prob})
            
            return jsonify({
                "success": True,
                "results": clean_results
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"孤立词摄像头识别失败: {str(e)}"
        }), 500


@app.route('/api/predict-isolated-jpg', methods=['POST'])
def predict_isolated_jpg_api():
    """孤立词jpg序列识别
    
    Request: POST /api/predict-isolated-jpg
    FormData: {
        "frames_dir": "path/to/frames/directory",
        "top_k": 1
    }
    
    注意：此API用于本地测试，需要提供已存在的jpg序列目录路径
    在Web场景下，通常使用 predict-isolated 或 predict-isolated-webcam
    
    Response: {
        "success": true,
        "result": "你好",
        "confidence": 0.95
    }
    """
    global global_isolated_predictor
    
    if not global_isolated_predictor:
        return jsonify({
            "success": False,
            "message": "孤立词预测器未初始化，请先调用 /api/init-isolated"
        }), 400
    
    try:
        data = request.form.to_dict()
        frames_dir = data.get('frames_dir', '')
        top_k = int(data.get('top_k', 1))
        
        if not frames_dir:
            return jsonify({
                "success": False,
                "message": "未提供jpg序列目录路径"
            }), 400
        
        if not os.path.exists(frames_dir):
            return jsonify({
                "success": False,
                "message": f"目录不存在: {frames_dir}"
            }), 400
        
        # 调用孤立词预测器
        if top_k == 1:
            result, confidence = global_isolated_predictor.predict_from_jpg_sequence(
                frames_dir, return_prob=True
            )
            
            # 确保confidence是有效数值
            if confidence != confidence:  # NaN检查
                confidence = 0.0
            confidence = float(max(0.0, min(1.0, confidence)))
            
            return jsonify({
                "success": True,
                "result": str(result),
                "confidence": confidence
            })
        else:
            results = global_isolated_predictor.predict_from_jpg_sequence(
                frames_dir, return_prob=True, top_k=top_k
            )
            
            # 确保所有概率都是有效数值
            clean_results = []
            for r in results:
                prob = float(r[1])
                if prob != prob:  # NaN检查
                    prob = 0.0
                prob = max(0.0, min(1.0, prob))
                clean_results.append({"word": str(r[0]), "confidence": prob})
            
            return jsonify({
                "success": True,
                "results": clean_results
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"孤立词jpg序列识别失败: {str(e)}"
        }), 500


@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary_api():
    """获取孤立词词汇表
    
    Request: GET /api/vocabulary
    
    Response: {
        "success": true,
        "vocabulary": [
            {"id": "000100", "text": "来"},
            {"id": "000101", "text": "去（出）"}
        ]
    }
    """
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        corpus_file = os.path.join(project_root, 'dataset', 'corpus.txt')
        
        vocabulary = []
        
        if os.path.exists(corpus_file):
            with open(corpus_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            vocabulary.append({
                                "id": parts[0],
                                "text": parts[1]
                            })
        
        return jsonify({
            "success": True,
            "vocabulary": vocabulary,
            "count": len(vocabulary)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"获取词汇表失败: {str(e)}"
        }), 500


if __name__ == "__main__":
    # 启动Flask Web服务
    print("✅ Flask后端服务启动中...")
    app.run(
        host='0.0.0.0',
        port=5001,  # 改为 5001，避免冲突
        debug=True,
        use_reloader=False
    )

    # 解决高DPI显示问题
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = HandSignUI()
    window.show()
    sys.exit(app.exec_())


