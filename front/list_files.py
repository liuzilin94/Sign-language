import os
import sys

print("当前工作目录:", os.getcwd())
path = 'recognition/front/数字人页面/glb'

try:
    files = os.listdir(path)
    print(f"\n目录 '{path}' 下的文件 (共{len(files)}个):")
    for f in sorted(files):
        print(f"  {repr(f)}")
        # 尝试解码
        try:
            decoded_gbk = f.encode('latin1').decode('gbk')
            print(f"    GBK解码: {decoded_gbk}")
        except Exception as e:
            print(f"    GBK解码失败: {e}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
