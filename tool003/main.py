import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from mutagen.flac import FLAC


class FLACDurationExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("FLAC文件时长提取器")
        self.root.geometry("800x600")

        # 设置样式
        self.setup_styles()

        # 创建UI组件
        self.create_widgets()

    def setup_styles(self):
        """设置控件样式"""
        style = ttk.Style()
        style.theme_use('clam')

    def create_widgets(self):
        """创建所有UI控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 文件夹选择部分
        ttk.Label(main_frame, text="选择文件夹:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)

        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path_var, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(folder_frame, text="浏览...", command=self.browse_folder).grid(row=0, column=1, sticky=tk.W)

        # 输出文件名
        ttk.Label(main_frame, text="输出文件名:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        self.output_file_var = tk.StringVar(value="music_duration.txt")
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_file_var, width=30)
        self.output_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # 处理按钮
        self.process_button = ttk.Button(main_frame, text="开始处理", command=self.process_files)
        self.process_button.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # 输出文本框
        ttk.Label(main_frame, text="处理结果:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))

        # 创建滚动文本框
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 配置文本框架网格
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # 滚动文本框
        self.output_text = scrolledtext.ScrolledText(text_frame, width=70, height=20, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架行权重
        main_frame.rowconfigure(7, weight=1)

        # 保存到文件按钮
        self.save_button = ttk.Button(main_frame, text="保存到文件", command=self.save_to_file, state=tk.DISABLED)
        self.save_button.grid(row=8, column=0, sticky=tk.W, pady=(0, 5))

    def browse_folder(self):
        """打开文件夹选择对话框"""
        folder_path = filedialog.askdirectory(title="选择包含FLAC文件的文件夹")
        if folder_path:
            self.folder_path_var.set(folder_path)

    def get_flac_duration(self, file_path):
        """获取FLAC文件的时长，返回mm:ss格式"""
        try:
            audio = FLAC(file_path)
            duration = audio.info.length  # 获取时长（秒）
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes:02d}:{seconds:02d}"
        except Exception as e:
            self.log_message(f"错误：无法读取文件 {os.path.basename(file_path)} - {e}")
            return "00:00"

    def log_message(self, message):
        """在输出文本框中记录消息"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)  # 自动滚动到底部
        self.root.update()  # 更新UI

    def process_files(self):
        """处理FLAC文件"""
        folder_path = self.folder_path_var.get()
        output_file = self.output_file_var.get()

        if not folder_path:
            self.log_message("错误：请先选择文件夹")
            return

        if not os.path.exists(folder_path):
            self.log_message(f"错误：文件夹 '{folder_path}' 不存在")
            return

        # 清空输出文本框
        self.output_text.delete(1.0, tk.END)

        # 禁用处理按钮
        self.process_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)

        try:
            # 查找FLAC文件
            flac_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.flac')]

            if not flac_files:
                self.log_message("在指定文件夹中未找到FLAC文件")
                return

            self.log_message(f"找到 {len(flac_files)} 个FLAC文件，开始处理...")

            # 重置进度条
            self.progress_var.set(0)

            results = []
            total_files = len(flac_files)

            for i, filename in enumerate(flac_files):
                file_path = os.path.join(folder_path, filename)

                # 获取文件名（不含后缀）
                name_without_ext = os.path.splitext(filename)[0].strip(".")

                # 获取音乐时长
                duration = self.get_flac_duration(file_path)

                # 记录结果
                result_line = f"{name_without_ext}\t{duration}"
                results.append(result_line)
                self.log_message(f"已处理: {filename} -> {duration}")

                # 更新进度条
                progress = (i + 1) / total_files * 100
                self.progress_var.set(progress)
                self.status_label.config(text=f"处理中... ({i + 1}/{total_files})")
                self.root.update()

            # 在文本框中显示结果
            self.output_text.delete(1.0, tk.END)
            for result in results:
                self.output_text.insert(tk.END, result + "\n")

            self.log_message(f"\n完成！共处理了 {len(flac_files)} 个文件")
            self.status_label.config(text="完成")

            # 保存结果到变量，供保存文件使用
            self.results = results
            self.save_button.config(state=tk.NORMAL)

        except Exception as e:
            self.log_message(f"处理过程中发生错误: {e}")
        finally:
            # 重新启用处理按钮
            self.process_button.config(state=tk.NORMAL)

    def save_to_file(self):
        """将结果保存到文件"""
        if not hasattr(self, 'results') or not self.results:
            self.log_message("没有可保存的结果")
            return

        output_file = self.output_file_var.get()
        if not output_file:
            output_file = "music_duration.txt"

        # 如果输出文件没有扩展名，添加.txt
        if not os.path.splitext(output_file)[1]:
            output_file += ".txt"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in self.results:
                    f.write(result + "\n")

            self.log_message(f"结果已保存到: {os.path.abspath(output_file)}")
        except Exception as e:
            self.log_message(f"保存文件时出错: {e}")


if __name__ == "__main__":
    # 检查命令行参数
    folder_path = None
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]

    root = tk.Tk()
    app = FLACDurationExtractor(root)

    # 如果通过命令行指定了文件夹路径，则设置
    if folder_path:
        app.folder_path_var.set(folder_path)

    root.mainloop()