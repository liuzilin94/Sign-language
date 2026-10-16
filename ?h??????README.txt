                   CSL手语识别系统 - 素材文件说明


本文件夹包含项目的代表性素材，包括封面图、Logo、手语视频和手语图解。

一、文件夹结构

materials/
│
├── images/                    # 图片素材
│   ├── cover.jpg            # 系统封面图 (约3.6MB)
│   └── logo.png             # 系统Logo (约500KB)
│
├── videos/                   # 手语视频样本 (MP4格式)
│   └── (词汇视频...)
│
├── dict_images/              # 手语图解 (PNG格式)
│   └── (词汇图解...)
│
└── README.txt               # 本说明文件


二、素材说明


1. 封面图 (cover.jpg)
   - 尺寸：1920x1080 像素
   - 用途：系统首页背景图、登录页面背景
   - 内容：中国手语主题背景图

2. Logo (logo.png)
   - 尺寸：约500KB
   - 用途：导航栏、登录页、App图标
   - 内容：CSL手语识别系统标识

3. 手语视频 (videos/*.mp4)
   - 格式：MP4
   - 编码：H.264
   - 用途：词汇学习时的示范视频
   - 内容：演示的手语动作

4. 手语图解 (dict_images/*.png)
   - 格式：PNG透明背景
   - 用途：词典页面、词汇详情页
   - 内容：手语动作分解图解

三、素材使用说明

前端使用方式：

1. 视频播放（学习页面）
   路径：/videos/{词汇名}.mp4
   示例：/videos/中国.mp4

2. 图解展示（词典页面）
   路径：/images/dict/{词汇名}.png
   示例：/images/dict/中国.png

3. 封面和Logo
   路径：/images/cover.jpg
   路径：/images/logo.png

四、相关文件位置

在完整项目中，这些素材的原始位置：

- 封面图：front/dist/images/cover.jpg
- Logo：front/dist/images/logo.png
- 视频：video/*.mp4
- 图解：front/public/images/dict/*.png

