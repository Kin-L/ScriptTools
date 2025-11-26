import os.path
import re
from datetime import timedelta


def parse_lrc_file(filename):
    """
    解析LRC文件，返回时间戳和歌词的列表
    格式: [(时间戳, 歌词), ...]
    """
    lyrics = []
    time_pattern = re.compile(r'\[(\d+):(\d+\.\d+)\]')

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            # 匹配时间戳
            matches = time_pattern.findall(line)
            if matches:
                # 获取歌词文本（移除时间戳部分）
                lyric_text = time_pattern.sub('', line).strip()
                for match in matches:
                    minutes, seconds = match
                    # 转换为秒数
                    total_seconds = int(minutes) * 60 + float(seconds)
                    lyrics.append((total_seconds, lyric_text))

    # 按时间戳排序
    lyrics.sort(key=lambda x: x[0])
    return lyrics


def format_timestamp(seconds):
    """将秒数转换为LRC时间戳格式 [mm:ss.xx]"""
    minutes = int(seconds // 60)
    seconds_remaining = seconds % 60
    return f"[{minutes:02d}:{seconds_remaining:05.2f}]"


def merge_lrc_files(japanese_file, chinese_file, output_file):
    """
    合并日语和中文LRC文件
    """
    # 解析两个文件
    jp_lyrics = parse_lrc_file(japanese_file)
    cn_lyrics = parse_lrc_file(chinese_file)

    print(f"日语歌词数量: {len(jp_lyrics)}")
    print(f"中文歌词数量: {len(cn_lyrics)}")

    # 合并歌词
    merged_lyrics = []
    unmatched_jp = []
    unmatched_cn = []

    # 创建索引
    jp_index = 0
    cn_index = 0

    while jp_index < len(jp_lyrics) or cn_index < len(cn_lyrics):
        jp_timestamp = jp_lyrics[jp_index][0] if jp_index < len(jp_lyrics) else float('inf')
        cn_timestamp = cn_lyrics[cn_index][0] if cn_index < len(cn_lyrics) else float('inf')

        # 如果时间戳相近（在0.5秒内），认为是同一句
        if abs(jp_timestamp - cn_timestamp) <= 0.5:
            jp_time, jp_text = jp_lyrics[jp_index]
            cn_time, cn_text = cn_lyrics[cn_index]

            # 使用日语歌词的时间戳
            merged_line = f"{format_timestamp(jp_time)}{jp_text}\n{format_timestamp(jp_time)}{cn_text}"
            merged_lyrics.append((jp_time, merged_line))

            jp_index += 1
            cn_index += 1

        elif jp_timestamp < cn_timestamp:
            # 只有日语歌词
            jp_time, jp_text = jp_lyrics[jp_index]
            merged_line = f"{format_timestamp(jp_time)}{jp_text}"
            merged_lyrics.append((jp_time, merged_line))
            unmatched_jp.append((jp_time, jp_text))
            jp_index += 1

        else:
            # 只有中文歌词
            cn_time, cn_text = cn_lyrics[cn_index]
            merged_line = f"{format_timestamp(cn_time)}{cn_text}"
            merged_lyrics.append((cn_time, merged_line))
            unmatched_cn.append((cn_time, cn_text))
            cn_index += 1

    # 按时间戳排序合并后的歌词
    merged_lyrics.sort(key=lambda x: x[0])

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write("[merged: Japanese and Chinese lyrics]\n\n")
        for _, line in merged_lyrics:
            out_file.write(line + '\n')

    # 输出未匹配的时间戳
    print("\n=== 未匹配的时间戳 ===")
    if unmatched_jp:
        print(f"\n未匹配的日语歌词 ({len(unmatched_jp)} 个):")
        for timestamp, text in unmatched_jp:
            print(f"  {format_timestamp(timestamp)} {text}")

    if unmatched_cn:
        print(f"\n未匹配的中文歌词 ({len(unmatched_cn)} 个):")
        for timestamp, text in unmatched_cn:
            print(f"  {format_timestamp(timestamp)} {text}")

    # 统计信息
    total_matched = min(len(jp_lyrics), len(cn_lyrics)) - (len(unmatched_jp) + len(unmatched_cn)) // 2
    print(f"\n=== 合并统计 ===")
    print(f"总歌词行数: {len(merged_lyrics)}")
    print(f"匹配的歌词对: {total_matched}")
    print(f"未匹配的日语歌词: {len(unmatched_jp)}")
    print(f"未匹配的中文歌词: {len(unmatched_cn)}")
    print(f"输出文件: {output_file}")


def main():
    # 文件路径配置
    japanese_file = r"E:\Kin-Audio\ASMR\其他\綾瀬亜季子 ～再婚した清楚な妻と静かに愛を深める生活～-step1.lrc"  # 日语LRC文件路径
    chinese_file = "chlrc.lrc"  # 中文LRC文件路径
    if "step1" in japanese_file:
        output_file = japanese_file.replace("step1", "step2")
    else:
        s1, s2 = os.path.splitext(japanese_file)
        output_file = s1 + "step2" + s2

    try:
        merge_lrc_files(japanese_file, chinese_file, output_file)
        print("\n合并完成！")
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()