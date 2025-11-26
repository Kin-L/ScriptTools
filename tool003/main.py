import os
import sys
from mutagen.flac import FLAC


def get_flac_duration(file_path):
    """获取FLAC文件的时长，返回mm:ss格式"""
    try:
        audio = FLAC(file_path)
        duration = audio.info.length  # 获取时长（秒）
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    except Exception as e:
        print(f"错误：无法读取文件 {file_path} - {e}")
        return "00:00"


def process_flac_files(folder_path, output_file):
    """处理指定文件夹中的所有FLAC文件"""
    if not os.path.exists(folder_path):
        print(f"错误：文件夹 '{folder_path}' 不存在")
        return

    flac_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.flac')]

    if not flac_files:
        print("在指定文件夹中未找到FLAC文件")
        return

    print(f"找到 {len(flac_files)} 个FLAC文件，开始处理...")

    with open(output_file, 'w', encoding='utf-8') as f:
        for filename in flac_files:
            file_path = os.path.join(folder_path, filename)

            # 获取文件名（不含后缀）
            name_without_ext = os.path.splitext(filename)[0].strip(".")

            # 获取音乐时长
            duration = get_flac_duration(file_path)

            # 写入文件：文件名 + 制表符 + 时长
            f.write(f"{name_without_ext}\t{duration}\n")

            print(f"已处理: {filename} -> {duration}")

    print(f"完成！结果已保存到: {output_file}")


if __name__ == "__main__":
    # 使用方法1：直接在代码中指定文件夹路径
    folder_path = r"E:\Kin-Audio\星塔旅人\1.1new"  # 修改为你的FLAC文件文件夹路径
    output_file = "music_duration.txt"

    # 使用方法2：通过命令行参数指定文件夹
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    process_flac_files(folder_path, output_file)