import os
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


def extract_lyrics_from_audio(audio_file_path):
    if not os.path.exists(audio_file_path):
        print(f"文件不存在: {audio_file_path}")
        return

    lyrics = None

    # 根据文件类型处理
    if audio_file_path.lower().endswith(".mp3"):
        try:
            audio = ID3(audio_file_path)
            if "USLT::'eng'" in audio:  # 英文歌词标签
                lyrics = audio["USLT::'eng'"].text
        except Exception as e:
            print(f"解析MP3失败: {e}")

    elif audio_file_path.lower().endswith(".flac"):
        try:
            audio = FLAC(audio_file_path)
            if "lyrics" in audio:
                lyrics = "\n".join(audio["lyrics"])
        except Exception as e:
            print(f"解析FLAC失败: {e}")

    elif audio_file_path.lower().endswith(".m4a"):
        try:
            audio = MP4(audio_file_path)
            if "\xa9lyr" in audio:  # iTunes歌词标签
                lyrics = audio["\xa9lyr"][0]
        except Exception as e:
            print(f"解析M4A失败: {e}")

    else:
        print("不支持的文件格式")
        return

    # 如果有歌词，写入txt文件
    if lyrics:
        txt_file_path = os.path.splitext(audio_file_path)[0] + ".txt"
        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(lyrics)
        print(f"歌词已提取到: {txt_file_path}")
        return txt_file_path
    else:
        print(f"未找到歌词: {audio_file_path}")
        return


# 示例调用
extract_lyrics_from_audio(r"E:\Kin-Audio\新建文件夹 (3)\夏霞 - あたらよ.mp3")  # 支持MP3/FLAC/M4A等
