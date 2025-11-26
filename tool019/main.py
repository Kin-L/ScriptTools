
import subprocess
import os


def concat_audio_files_filter(input_files, output_file):
    """
    使用FFmpeg的filter_complex拼接音频文件
    适用于不同格式的音频，会自动进行格式转换
    """
    try:
        # 构建输入参数
        input_params = []
        filter_complex = ""

        for i, file in enumerate(input_files):
            input_params.extend(['-i', file])
            filter_complex += f"[{i}:0]"

        # 构建filter_complex参数
        filter_complex += f"concat=n={len(input_files)}:v=0:a=1[out]"

        # 构建FFmpeg命令
        cmd = [
            'ffmpeg',
            *input_params,
            '-filter_complex', filter_complex,
            '-map', '[out]',
            output_file
        ]

        # 执行命令
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"音频拼接完成: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"拼接失败: {e}")
        print(f"错误输出: {e.stderr.decode()}")

# 拼接多个音频片段
# 使用示例
if __name__ == "__main__":
    input_files = [
        r"E:\Unpack\尘白禁区\increase\BGM\1042763428.flac",
        r"E:\Unpack\尘白禁区\increase\BGM\141388604.flac",
    ]
    output_file = r"E:\Unpack\尘白禁区\increase\BGM\叩响门扉.flac"

    concat_audio_files_filter(input_files, output_file)