import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from mutagen import File
from mutagen.id3 import ID3, USLT
from mutagen.flac import FLAC
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
import chardet


class LyricsExtractorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("音频文件歌词提取工具")
        self.root.geometry("600x400")

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="音频文件歌词提取工具",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 说明文本
        desc_text = "支持格式: MP3, FLAC, Opus, WAV\n\n" \
                    "功能: 从音频文件中提取内嵌歌词并保存为同名的LRC文件"
        desc_label = tk.Label(self.root, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=10)

        # 选择文件按钮
        select_btn = tk.Button(self.root, text="选择音频文件",
                               command=self.select_files,
                               font=("Arial", 12),
                               bg="#4CAF50", fg="white",
                               width=20, height=2)
        select_btn.pack(pady=20)

        # 文件列表框架
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 文件列表标签
        list_label = tk.Label(list_frame, text="已选文件:", anchor="w")
        list_label.pack(fill=tk.X)

        # 文件列表框和滚动条
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)

        list_scrollbar.config(command=self.file_listbox.yview)

        # 按钮框架
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # 提取按钮
        extract_btn = tk.Button(btn_frame, text="提取歌词",
                                command=self.extract_lyrics,
                                font=("Arial", 10),
                                bg="#2196F3", fg="white",
                                width=15, height=1)
        extract_btn.pack(side=tk.LEFT, padx=5)

        # 清空列表按钮
        clear_btn = tk.Button(btn_frame, text="清空列表",
                              command=self.clear_list,
                              font=("Arial", 10),
                              bg="#FF9800", fg="white",
                              width=15, height=1)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 退出按钮
        exit_btn = tk.Button(btn_frame, text="退出",
                             command=self.root.quit,
                             font=("Arial", 10),
                             bg="#F44336", fg="white",
                             width=15, height=1)
        exit_btn.pack(side=tk.LEFT, padx=5)

        # 状态标签
        self.status_label = tk.Label(self.root, text="请选择音频文件",
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def select_files(self):
        """打开文件选择对话框"""
        file_types = [
            ("音频文件", "*.mp3 *.flac *.opus *.wav"),
            ("MP3文件", "*.mp3"),
            ("FLAC文件", "*.flac"),
            ("Opus文件", "*.opus"),
            ("WAV文件", "*.wav"),
            ("所有文件", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=file_types
        )

        if files:
            for file_path in files:
                if file_path not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, file_path)

            self.update_status(f"已选择 {len(files)} 个文件")

    def clear_list(self):
        """清空文件列表"""
        self.file_listbox.delete(0, tk.END)
        self.update_status("文件列表已清空")

    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def detect_encoding(self, text_bytes):
        """检测文本编码"""
        result = chardet.detect(text_bytes)
        return result.get('encoding', 'utf-8')

    def extract_lyrics_from_audio(self, file_path):
        """
        从音频文件中提取内嵌歌词
        返回歌词文本和编码信息
        """
        file_path = Path(file_path)
        lyrics_text = None
        encoding = 'utf-8'

        try:
            if file_path.suffix.lower() == '.mp3':
                audio = ID3(file_path)
                # 查找USLT帧（非同步歌词文本）
                for key in audio.keys():
                    if key.startswith('USLT'):
                        uslt_frame = audio[key]
                        lyrics_bytes = uslt_frame.text
                        if isinstance(lyrics_bytes, bytes):
                            encoding = self.detect_encoding(lyrics_bytes)
                            lyrics_text = lyrics_bytes.decode(encoding, errors='ignore')
                        else:
                            lyrics_text = str(lyrics_bytes)
                        break

            elif file_path.suffix.lower() == '.flac':
                audio = FLAC(file_path)
                if 'lyrics' in audio:
                    lyrics_bytes = audio['lyrics'][0]
                    if isinstance(lyrics_bytes, bytes):
                        encoding = self.detect_encoding(lyrics_bytes)
                        lyrics_text = lyrics_bytes.decode(encoding, errors='ignore')
                    else:
                        lyrics_text = str(lyrics_bytes)

            elif file_path.suffix.lower() == '.opus':
                audio = OggOpus(file_path)
                if 'lyrics' in audio:
                    lyrics_bytes = audio['lyrics'][0]
                    if isinstance(lyrics_bytes, bytes):
                        encoding = self.detect_encoding(lyrics_bytes)
                        lyrics_text = lyrics_bytes.decode(encoding, errors='ignore')
                    else:
                        lyrics_text = str(lyrics_bytes)

            elif file_path.suffix.lower() == '.wav':
                audio = WAVE(file_path)
                # WAV文件通常不包含标准歌词标签，尝试常见标签
                tags = audio.tags if audio.tags else []
                for tag in tags:
                    if tag[0].lower() in ['lyrics', 'lyric', 'unsyncedlyrics']:
                        lyrics_bytes = tag[1]
                        if isinstance(lyrics_bytes, bytes):
                            encoding = self.detect_encoding(lyrics_bytes)
                            lyrics_text = lyrics_bytes.decode(encoding, errors='ignore')
                        else:
                            lyrics_text = str(lyrics_bytes)
                        break

        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return None, None

        return lyrics_text, encoding

    def save_lyrics_to_lrc(self, audio_file_path, lyrics_text, encoding='utf-8'):
        """
        将歌词文本保存为LRC文件
        """
        audio_path = Path(audio_file_path)
        lrc_path = audio_path.with_suffix('.lrc')

        try:
            with open(lrc_path, 'w', encoding='utf-8') as f:
                # 如果没有时间标签，添加默认的标题信息
                if lyrics_text and not any(line.strip().startswith('[') for line in lyrics_text.split('\n')):
                    f.write(f"[ti:{audio_path.stem}]\n")
                    f.write("[ar:Unknown]\n")
                    f.write("[al:Unknown]\n")
                    f.write("[by:Extracted Lyrics]\n")
                    f.write("\n")

                if lyrics_text:
                    f.write(lyrics_text)
                else:
                    f.write("[00:00.00]暂无歌词信息\n")

            return lrc_path

        except Exception as e:
            print(f"保存LRC文件 {lrc_path} 时出错: {e}")
            return None

    def extract_lyrics(self):
        """提取选中文件的歌词"""
        file_paths = self.file_listbox.get(0, tk.END)

        if not file_paths:
            messagebox.showwarning("警告", "请先选择音频文件")
            return

        success_count = 0
        total_count = len(file_paths)

        for i, file_path in enumerate(file_paths):
            self.update_status(f"正在处理 ({i + 1}/{total_count}): {os.path.basename(file_path)}")

            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                continue

            # 检查文件格式
            valid_extensions = {'.mp3', '.flac', '.opus', '.wav'}
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in valid_extensions:
                print(f"不支持的文件格式: {file_path}")
                continue

            # 提取歌词
            lyrics_text, encoding = self.extract_lyrics_from_audio(file_path)

            if lyrics_text:
                print(f"  找到歌词，编码: {encoding}")
                # 保存为LRC文件
                lrc_path = self.save_lyrics_to_lrc(file_path, lyrics_text, encoding)
                if lrc_path:
                    print(f"  已保存: {lrc_path}")
                    success_count += 1
                else:
                    print(f"  保存失败: {file_path}")
            else:
                print(f"  未找到内嵌歌词: {file_path}")
                # 即使没有歌词也创建空的LRC文件
                lrc_path = self.save_lyrics_to_lrc(file_path, None)
                if lrc_path:
                    print(f"  创建空LRC文件: {lrc_path}")
                    success_count += 1

        # 显示结果
        self.update_status(f"处理完成! 成功处理 {success_count}/{total_count} 个文件")
        messagebox.showinfo("完成", f"处理完成!\n成功处理 {success_count}/{total_count} 个文件")

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """主函数"""
    app = LyricsExtractorGUI()
    app.run()


if __name__ == "__main__":
    main()