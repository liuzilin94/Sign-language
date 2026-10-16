import os
import shutil

src_dir = 'recognition/front/数字人页面/glb'
dst_dir = 'recognition/front/public/models/avatar'

# 确保目标目录存在
os.makedirs(dst_dir, exist_ok=True)

# 列出源目录文件
print("源目录文件列表:")
files = os.listdir(src_dir)
print(f"共 {len(files)} 个文件")

# 复制所有glb文件
for f in files:
    if f.lower().endswith('.glb'):
        src = os.path.join(src_dir, f)
        dst = os.path.join(dst_dir, f)
        try:
            shutil.copy2(src, dst)
            print(f"✓ 复制: {f}")
        except Exception as e:
            print(f"✗ 复制失败 {f}: {e}")

print("\n完成!")
