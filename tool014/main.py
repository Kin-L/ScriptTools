import subprocess
import os


def mkmp4(_audio_folder, pic_path, _out_dir):
    if not os.path.exists(_out_dir):
        os.makedirs(_out_dir)
    for filename in os.listdir(_audio_folder):
        if filename.lower().endswith(('.mp3', '.flac', '.wav')):
            # 构建输入和输出路径
            _audio_path = os.path.join(_audio_folder, filename)
            out = os.path.join(_out_dir, os.path.splitext(filename.lower())[0]+".mp4")
            cmd = f"ffmpeg -loop 1 -y -i {pic_path} -i {_audio_path} -shortest -threads 8 -r 24 -b:v 2400k -b:a 320k  -c:v h264_amf {out}"
            ffmpeger = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
            ffmpeger.communicate()


out_folder = r"E:\Kin-Audio\千年之旅\新建文件夹"
pic_path = r"E:\Unpack\新建文件夹2\CG1-1-1.png"
out_dir = r"E:\Kin-Audio\千年之旅\out\主线剧情"
# 使用音乐文件和单张图片，批量制作视频
mkmp4(out_folder, pic_path, out_dir)
