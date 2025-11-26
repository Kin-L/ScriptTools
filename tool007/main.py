import re
import os
from datetime import timedelta


def parse_lrc_time(time_str):
    """解析LRC时间格式（[mm:ss.xx]）为毫秒"""
    try:
        # 移除方括号
        time_str = time_str.strip('[]')
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds_parts = parts[1].split('.')
        seconds = int(seconds_parts[0])
        hundredths = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

        # 转换为毫秒
        total_ms = (minutes * 60 + seconds) * 1000 + hundredths * 10
        return total_ms
    except:
        return 0


def ms_to_srt_time(ms):
    """将毫秒转换为SRT时间格式（HH:MM:SS,mmm）"""
    td = timedelta(milliseconds=ms)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    milliseconds = td.microseconds // 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def lrc_to_srt(lrc_content, original_filename):
    """将LRC内容转换为SRT格式"""
    # 获取原文件所在目录和文件名（不含扩展名）
    file_dir = os.path.dirname(original_filename)
    file_base = os.path.splitext(os.path.basename(original_filename))[0]

    # 正则表达式匹配LRC时间标签和歌词
    time_pattern = r'\[(\d+:\d+\.\d+)\](.*)'

    # 存储所有时间戳和对应的歌词
    lyrics_data = []

    for line in lrc_content.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 查找所有时间标签
        matches = re.findall(r'\[(\d+:\d+\.\d+)\](.*?)(?=\[|$)', line)
        for match in matches:
            time_str, text = match
            text = text.strip()
            if text:  # 只添加有文本的行
                lyrics_data.append((parse_lrc_time(time_str), text))

    # 按时间戳排序
    lyrics_data.sort(key=lambda x: x[0])

    # 分析时间戳重复情况
    timestamp_count = {}
    for timestamp, text in lyrics_data:
        timestamp_count[timestamp] = timestamp_count.get(timestamp, 0) + 1

    # 计算最高重复数
    max_duplicates = max(timestamp_count.values()) if timestamp_count else 1

    # 如果没有重复时间戳，直接转换
    if max_duplicates == 1:
        output_filename = os.path.join(file_dir, f"{file_base}_output.srt")
        generate_srt_file(lyrics_data, output_filename)
        print(f"已生成文件: {output_filename}")
        return

    # 有重复时间戳，按最高重复数拆分文件
    print(f"检测到最高重复时间戳数量: {max_duplicates}，将拆分为 {max_duplicates} 个文件")

    # 初始化输出文件数据
    output_files_data = [[] for _ in range(max_duplicates)]

    # 为每个时间戳分配位置
    timestamp_positions = {}

    for timestamp, text in lyrics_data:
        if timestamp not in timestamp_positions:
            timestamp_positions[timestamp] = 0

        position = timestamp_positions[timestamp]
        output_files_data[position].append((timestamp, text))
        timestamp_positions[timestamp] += 1

    # 为每个输出文件生成SRT内容
    for i, file_data in enumerate(output_files_data):
        # 按时间戳排序
        file_data.sort(key=lambda x: x[0])

        output_filename = os.path.join(file_dir, f"{file_base}_output_{i + 1}.srt")
        generate_srt_file(file_data, output_filename)
        print(f"已生成文件: {output_filename}")


def generate_srt_file(lyrics_data, output_filename):
    """生成SRT文件"""
    srt_content = ""
    subtitle_index = 1

    for i in range(len(lyrics_data)):
        current_time = lyrics_data[i][0]
        current_text = lyrics_data[i][1]

        # 计算结束时间（下一个字幕的开始时间或当前时间+3秒）
        if i < len(lyrics_data) - 1:
            next_time = lyrics_data[i + 1][0]
            # 确保结束时间不早于开始时间，至少显示100毫秒
            end_time = max(current_time + 100, next_time)
        else:
            end_time = current_time + 3000  # 默认显示3秒

        start_time_srt = ms_to_srt_time(current_time)
        end_time_srt = ms_to_srt_time(end_time)

        srt_content += f"{subtitle_index}\n"
        srt_content += f"{start_time_srt} --> {end_time_srt}\n"
        srt_content += f"{current_text}\n\n"

        subtitle_index += 1

    # 写入文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(srt_content)


def lrc_file_to_srt(lrc_file_path):
    """从LRC文件转换为SRT文件"""
    try:
        if not os.path.exists(lrc_file_path):
            print(f"错误：找不到文件 {lrc_file_path}")
            return

        with open(lrc_file_path, 'r', encoding='utf-8') as f:
            lrc_content = f.read()

        lrc_to_srt(lrc_content, lrc_file_path)
        print("转换完成！")

    except Exception as e:
        print(f"转换过程中发生错误: {e}")


# lrc文件转srt文件，默认对重复时间戳进行拆分
# 使用示例
if __name__ == "__main__":
    # 示例1：测试没有重复时间戳的情况
    sample_lrc_no_dup = """
[00:01.00]这是第一句歌词
[00:05.50]这是第二句歌词
[00:15.25]这是第三句歌词
[00:20.75]这是最后一句歌词
"""

    print("测试没有重复时间戳的情况...")
    # lrc_to_srt(sample_lrc_no_dup, "test_no_dup.lrc")

    # 示例2：测试有重复时间戳的情况
    sample_lrc_with_dup = """
[00:01.00]这是第一句歌词
[00:05.50]这是第二句歌词
[00:10.00]这是重复时间戳的第一句
[00:10.00]这是重复时间戳的第二句
[00:10.00]这是重复时间戳的第三句
[00:15.25]这是第三句歌词
[00:20.75]这是最后一句歌词
[00:25.00]另一个重复时间戳
[00:25.00]另一个重复时间戳的第二句
"""

    # print("\n测试有重复时间戳的情况...")
    # lrc_to_srt(sample_lrc_with_dup, "test_with_dup.lrc")

    # 示例3：从实际文件转换（取消注释使用）
    lrc_file_to_srt(r"D:\Temp\lyrics.LRC")