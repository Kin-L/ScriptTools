import subprocess
import os


def vol(_input, _output):
    if not os.path.exists(_output):
        os.makedirs(_output)
    for filename in os.listdir(_input):
        if filename.lower().endswith(('.mp3', '.flac', '.wav')):
            # 构建输入和输出路径
            _input_path = os.path.join(_input, filename)
            _output_path = os.path.join(_output, filename)
            cmd1 = f"ffmpeg -i {_input_path} -threads 8 -af loudnorm=i={loudnorm} {_output_path}"
            ffmpeger = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE)
            ffmpeger.communicate()


audio_folder = r"E:\Kin-Audio\千年之旅\FLAC"
out_folder = r"E:\Kin-Audio\千年之旅\新建文件夹"
# 行业标准水平（LUFS）
loudnorm = -16
# 批量音量标准化
vol(audio_folder, out_folder)
