import re


def lrc_to_srt(lrc_file_path, srt_file_path):
    """
    将LRC歌词文件转换为SRT字幕文件

    Args:
        lrc_file_path (str): LRC文件路径
        srt_file_path (str): 输出的SRT文件路径
    """

    # 读取LRC文件
    with open(lrc_file_path, 'r', encoding='utf-8') as f:
        lrc_lines = f.readlines()

    # 解析LRC内容
    lyrics = []
    timelist = []

    for line in lrc_lines:
        line = line.strip()
        if not line:
            continue

        # 匹配时间标签和歌词内容
        # 格式如: [mm:ss.xx] 或 [mm:ss.xxx] 歌词内容
        matches = re.findall(r'\[(\d+):(\d+)(?:\.|:)?(\d+)\](.*)', line)
        if matches:
            for match in matches:
                minutes, seconds, milliseconds, text = match
                text = text.strip()
                if text:  # 只处理有歌词内容的行
                    # 处理毫秒位数（LRC可能是2位或3位）
                    if len(milliseconds) == 2:
                        milliseconds = int(milliseconds) * 10  # 2位百分秒转3位毫秒
                    elif len(milliseconds) == 3:
                        milliseconds = int(milliseconds)
                    else:
                        milliseconds = 0

                    # 转换为总毫秒数
                    total_milliseconds = (int(minutes) * 60 + int(seconds)) * 1000 + milliseconds
                    lyrics.append((total_milliseconds, text))
                    if total_milliseconds not in timelist:
                        timelist.append(total_milliseconds)

    # 按时间排序
    lyrics.sort(key=lambda x: x[0])
    timelen = len(timelist) - 1
    # 生成SRT内容
    srt_content = []
    for i in range(len(lyrics)):
        start_time, text = lyrics[i]
        num = timelist.index(start_time)

        # 计算结束时间：如果是最后一句，显示3秒；否则是下一句的开始时间
        if num < timelen:

            end_time = timelist[timelist.index(start_time) + 1]
        else:
            end_time = start_time + 7000  # 最后一句显示3秒

        # 转换为SRT时间格式: HH:MM:SS,mmm
        def format_time(milliseconds):
            hours = milliseconds // 3600000
            milliseconds %= 3600000
            minutes = milliseconds // 60000
            milliseconds %= 60000
            seconds = milliseconds // 1000
            milliseconds %= 1000
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

        start_str = format_time(start_time)
        end_str = format_time(end_time)

        # 构建SRT条目
        srt_content.append(str(i + 1))
        srt_content.append(f"{start_str} --> {end_str}")
        srt_content.append(text)
        srt_content.append("")  # 空行分隔

    # 写入SRT文件
    with open(srt_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))

    print(f"转换完成！共转换 {len(lyrics)} 句歌词")
    print(f"SRT文件已保存至: {srt_file_path}")

# 使用示例
if __name__ == "__main__":
    # 输入LRC文件路径和输出SRT文件路径
    lrc_file = r"D:\Kin-project\VideoClip\music_video\pur\lyrics.lrc"  # 替换为你的LRC文件路径
    srt_file = lrc_file.lower().rstrip(".lrc") + ".srt"  # 替换为你想要的输出路径

    # try:
    lrc_to_srt(lrc_file, srt_file)
    # except FileNotFoundError:
    #     print(f"错误：找不到文件 {lrc_file}")
    # except Exception as e:
    #     print(f"转换过程中出现错误: {e}")