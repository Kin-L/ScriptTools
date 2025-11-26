import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from datetime import timedelta
import os
import threading
import sys

class SRTtoLRCConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT to LRC 转换器")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # 设置样式
        self.setup_style()

        # 创建界面
        self.create_widgets()

        # 转换器实例
        self.converter = SRTtoLRCConverter()

    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))

    def create_widgets(self):
        """创建界面组件"""

        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="SRT 转 LRC 转换器", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # 文件选择框架
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 15))

        # SRT文件选择
        srt_frame = ttk.Frame(file_frame)
        srt_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(srt_frame, text="SRT文件:").pack(side=tk.LEFT)
        self.srt_path = tk.StringVar()
        srt_entry = ttk.Entry(srt_frame, textvariable=self.srt_path, width=50)
        srt_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)

        srt_browse_btn = ttk.Button(srt_frame, text="浏览...", command=self.browse_srt_file)
        srt_browse_btn.pack(side=tk.RIGHT)

        # LRC文件选择
        lrc_frame = ttk.Frame(file_frame)
        lrc_frame.pack(fill=tk.X)

        ttk.Label(lrc_frame, text="LRC文件:").pack(side=tk.LEFT)
        self.lrc_path = tk.StringVar()
        lrc_entry = ttk.Entry(lrc_frame, textvariable=self.lrc_path, width=50)
        lrc_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)

        lrc_browse_btn = ttk.Button(lrc_frame, text="浏览...", command=self.browse_lrc_file)
        lrc_browse_btn.pack(side=tk.RIGHT)

        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 15))

        self.add_metadata = tk.BooleanVar(value=True)
        metadata_check = ttk.Checkbutton(options_frame, text="添加元数据信息", variable=self.add_metadata)
        metadata_check.pack(anchor=tk.W)

        self.auto_open = tk.BooleanVar(value=False)
        auto_open_check = ttk.Checkbutton(options_frame, text="转换完成后打开所在文件夹", variable=self.auto_open)
        auto_open_check.pack(anchor=tk.W, pady=(5, 0))

        # 进度和日志框架
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True)

        # 日志文本框
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        self.convert_btn = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(button_frame, text="清空日志", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)

        # 进度条
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def browse_srt_file(self):
        """浏览选择SRT文件"""
        file_path = filedialog.askopenfilename(
            title="选择SRT文件",
            filetypes=[("SRT文件", "*.srt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.srt_path.set(file_path)
            # 自动生成LRC文件名
            lrc_path = os.path.splitext(file_path)[0] + '.lrc'
            self.lrc_path.set(lrc_path)

    def browse_lrc_file(self):
        """浏览选择LRC保存路径"""
        file_path = filedialog.asksaveasfilename(
            title="保存LRC文件",
            defaultextension=".lrc",
            filetypes=[("LRC文件", "*.lrc"), ("所有文件", "*.*")]
        )
        if file_path:
            self.lrc_path.set(file_path)

    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def start_conversion(self):
        """开始转换（在新线程中）"""
        srt_file = self.srt_path.get()
        lrc_file = self.lrc_path.get()

        if not srt_file:
            messagebox.showerror("错误", "请选择SRT文件！")
            return

        if not lrc_file:
            messagebox.showerror("错误", "请选择LRC文件保存路径！")
            return

        # 禁用转换按钮，开始进度条
        self.convert_btn.config(state='disabled')
        self.progress.start()

        # 在新线程中执行转换
        thread = threading.Thread(
            target=self.convert_file,
            args=(srt_file, lrc_file)
        )
        thread.daemon = True
        thread.start()

    def convert_file(self, srt_file, lrc_file):
        """执行文件转换"""
        try:
            self.log(f"开始转换: {os.path.basename(srt_file)}")
            self.log(f"输入文件: {srt_file}")
            self.log(f"输出文件: {lrc_file}")
            self.log("-" * 50)

            # 执行转换
            self.converter.convert(
                srt_file_path=srt_file,
                lrc_file_path=lrc_file,
                add_metadata=self.add_metadata.get()
            )

            self.log("转换成功完成！")
            self.log(f"生成文件: {lrc_file}")

            # 转换完成后操作
            if self.auto_open.get():
                self.open_file_location(lrc_file)

            # 在主线程中显示成功消息
            self.root.after(0, lambda: messagebox.showinfo("成功", "文件转换完成！"))

        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            self.log(error_msg)
            # 在主线程中显示错误消息
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))

        finally:
            # 恢复按钮状态，停止进度条
            self.root.after(0, self.conversion_finished)

    def conversion_finished(self):
        """转换完成后的清理工作"""
        self.convert_btn.config(state='normal')
        self.progress.stop()

    def open_file_location(self, file_path):
        """打开文件所在文件夹"""
        try:
            folder_path = os.path.dirname(file_path)
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                subprocess.run(['open', folder_path] if sys.platform == 'darwin' else ['xdg-open', folder_path])
        except Exception as e:
            self.log(f"无法打开文件夹: {e}")


class SRTtoLRCConverter:
    def __init__(self):
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16']

    def detect_encoding(self, file_path):
        """检测文件编码"""
        for encoding in self.supported_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        return 'utf-8'

    def parse_srt_time(self, time_str):
        """解析SRT时间格式"""
        # 支持多种SRT时间格式
        time_str = time_str.strip()
        patterns = [
            r'(\d+):(\d+):(\d+),(\d+)',
            r'(\d+):(\d+):(\d+)\.(\d+)',
            r'(\d+):(\d+):(\d+):(\d+)'
        ]

        for pattern in patterns:
            match = re.match(pattern, time_str)
            if match:
                h, m, s, ms = map(int, match.groups())
                # 处理毫秒（SRT可能是3位或2位）
                if ms < 100:
                    ms *= 10  # 假设是2位毫秒
                return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)

        return None

    def format_lrc_time(self, time_delta):
        """格式化LRC时间"""
        total_seconds = time_delta.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"[{minutes:02d}:{seconds:05.2f}]"

    def clean_text(self, text):
        """清理文本，移除HTML标签和多余空格"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除字幕序号（如果存在）
        text = re.sub(r'^\d+\s*', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def convert(self, srt_file_path, lrc_file_path, add_metadata=True):
        """
        转换SRT到LRC
        """
        if not os.path.exists(srt_file_path):
            raise FileNotFoundError(f"SRT文件不存在: {srt_file_path}")

        # 检测编码并读取文件
        encoding = self.detect_encoding(srt_file_path)
        with open(srt_file_path, 'r', encoding=encoding) as f:
            srt_content = f.read()

        # 分割字幕块
        blocks = re.split(r'\n\s*\n', srt_content.strip())

        lrc_lines = []

        # 添加元数据
        if add_metadata:
            base_name = os.path.splitext(os.path.basename(srt_file_path))[0]
            lrc_lines.extend([
                f"[ar:Unknown Artist]",
                f"[ti:{base_name}]",
                f"[al:Unknown Album]",
                f"[by:SRT to LRC Converter]",
                f"[re:Player]",
                f"[ve:1.0]",
                ""
            ])

        valid_blocks = 0
        for block in blocks:
            if not block.strip():
                continue

            lines = [line.strip() for line in block.split('\n') if line.strip()]

            if len(lines) < 3:
                continue

            # 解析时间轴
            time_line = lines[1]
            time_parts = time_line.split('-->')
            if len(time_parts) < 2:
                continue

            start_time_str = time_parts[0].strip()
            start_time = self.parse_srt_time(start_time_str)

            if start_time is None:
                continue

            # 格式化时间并清理文本
            lrc_time = self.format_lrc_time(start_time)
            text = self.clean_text(' '.join(lines[2:]))

            if text:  # 只添加非空文本
                lrc_lines.append(f"{lrc_time}{text}")
                valid_blocks += 1

        # 按时间排序
        lrc_lines = self.sort_lrc_lines(lrc_lines)

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(lrc_file_path)), exist_ok=True)

        # 写入LRC文件
        with open(lrc_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lrc_lines))

        return valid_blocks

    def sort_lrc_lines(self, lines):
        """按时间排序LRC行"""

        def get_time(line):
            time_match = re.search(r'\[(\d+):(\d+\.\d+)\]', line)
            if time_match:
                minutes = int(time_match.group(1))
                seconds = float(time_match.group(2))
                return minutes * 60 + seconds
            return float('inf')

        metadata = [line for line in lines if
                    not line.startswith('[') or ':' not in line or not re.search(r'\[\d+:\d+\.\d+\]', line)]
        lyric_lines = [line for line in lines if line.startswith('[') and re.search(r'\[\d+:\d+\.\d+\]', line)]

        lyric_lines.sort(key=get_time)
        return metadata + lyric_lines


def main():
    """主函数"""
    root = tk.Tk()
    app = SRTtoLRCConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()