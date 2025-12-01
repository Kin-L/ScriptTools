import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class AudioNormalizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频音量标准化工具")
        self.root.geometry("600x500")

        # 默认值
        self.loudnorm_var = tk.StringVar(value="-16")
        self.audio_folder_var = tk.StringVar(value="")
        self.output_folder_var = tk.StringVar(value="")
        self.same_folder_var = tk.BooleanVar(value=False)

        # 进度跟踪变量（需要在create_widgets之前初始化）
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="准备就绪")
        self.current_file_var = tk.StringVar(value="")

        # 文件队列和计数
        self.total_files = 0
        self.processed_files = 0
        self.processing = False

        # 创建UI
        self.create_widgets()

        # 日志框
        self.log_text = None

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="音频音量标准化工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 输入文件夹选择
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(input_frame, text="输入文件夹:", width=12, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.audio_folder_var, width=50).grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="浏览...", command=self.browse_input_folder).grid(row=0, column=2)

        # 输出选项
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Checkbutton(output_frame, text="在原文件夹处理(覆盖原文件)",
                       variable=self.same_folder_var, command=self.toggle_output_folder).pack(anchor="w")

        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)

        tk.Label(output_path_frame, text="输出文件夹:", width=12, anchor="w").grid(row=0, column=0, sticky="w")
        self.output_entry = tk.Entry(output_path_frame, textvariable=self.output_folder_var, width=50, state="normal")
        self.output_entry.grid(row=0, column=1, padx=5)
        self.output_browse_btn = tk.Button(output_path_frame, text="浏览...", command=self.browse_output_folder,
                                           state="normal")
        self.output_browse_btn.grid(row=0, column=2)

        # loudnorm参数
        loudnorm_frame = tk.Frame(self.root)
        loudnorm_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(loudnorm_frame, text="标准化目标(LUFS):", width=20, anchor="w").grid(row=0, column=0, sticky="w")
        loudnorm_spinbox = tk.Spinbox(loudnorm_frame, from_=-30, to=0, increment=1,
                                      textvariable=self.loudnorm_var, width=10)
        loudnorm_spinbox.grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(loudnorm_frame, text="(推荐: -16 到 -23)").grid(row=0, column=2, sticky="w", padx=5)

        # 进度条
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        # 状态标签
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, fill=tk.X)
        tk.Label(status_frame, textvariable=self.current_file_var, anchor="w", fg="blue").pack(side=tk.LEFT, fill=tk.X,
                                                                                               padx=10)

        # 日志区域
        log_frame = tk.LabelFrame(self.root, text="处理日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.log_text = tk.Text(log_frame, height=10, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # 按钮区域
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="开始处理", command=self.start_processing,
                                      width=15, bg="green", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="停止", command=self.stop_processing,
                                     width=15, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="清空日志", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)

    def toggle_output_folder(self):
        if self.same_folder_var.get():
            self.output_entry.config(state="disabled")
            self.output_browse_btn.config(state="disabled")
            self.output_folder_var.set("")
        else:
            self.output_entry.config(state="normal")
            self.output_browse_btn.config(state="normal")

    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="选择输入文件夹")
        if folder:
            self.audio_folder_var.set(folder)
            # 如果输出文件夹为空，自动建议一个
            if not self.output_folder_var.get() and not self.same_folder_var.get():
                self.output_folder_var.set(folder + "_normalized")

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder_var.set(folder)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def update_progress(self):
        if self.total_files > 0:
            progress = (self.processed_files / self.total_files) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"处理中: {self.processed_files}/{self.total_files}")

    def process_audio(self):
        _input = self.audio_folder_var.get()
        loudnorm = self.loudnorm_var.get()

        # 检查输入文件夹
        if not _input or not os.path.exists(_input):
            messagebox.showerror("错误", "请输入有效的输入文件夹路径！")
            self.processing = False
            return

        # 确定输出文件夹
        if self.same_folder_var.get():
            _output = _input  # 在原文件夹处理
        else:
            _output = self.output_folder_var.get()
            if not _output:
                messagebox.showerror("错误", "请输入输出文件夹路径或选择'在原文件夹处理'！")
                self.processing = False
                return

            # 创建输出文件夹
            if not os.path.exists(_output):
                os.makedirs(_output)

        # 获取音频文件列表
        audio_files = []
        for filename in os.listdir(_input):
            if filename.lower().endswith(('.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg')):
                audio_files.append(filename)

        self.total_files = len(audio_files)
        self.processed_files = 0

        if self.total_files == 0:
            messagebox.showwarning("警告", "输入文件夹中没有找到支持的音频文件！")
            self.processing = False
            return

        self.log_message(f"找到 {self.total_files} 个音频文件")
        self.log_message(f"开始处理，目标LUFS值: {loudnorm}")
        if self.same_folder_var.get():
            self.log_message(f"在原文件夹处理(覆盖原文件)")
        else:
            self.log_message(f"输出到: {_output}")

        # 处理每个文件
        for i, filename in enumerate(audio_files):
            if not self.processing:
                break

            _input_path = os.path.join(_input, filename)

            # 如果在原文件夹处理，需要创建一个临时文件名
            if self.same_folder_var.get():
                name, ext = os.path.splitext(filename)
                temp_filename = f"{name}_temp{ext}"
                _output_path = os.path.join(_output, temp_filename)
                final_output_path = os.path.join(_output, filename)
            else:
                _output_path = os.path.join(_output, filename)
                final_output_path = _output_path

            self.current_file_var.set(f"正在处理: {filename}")
            self.log_message(f"处理: {filename}")

            try:
                # 构建ffmpeg命令
                cmd = f'ffmpeg -i "{_input_path}" -threads 8 -af loudnorm=i={loudnorm} "{_output_path}" -y'

                # 执行命令
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

                if process.returncode == 0:
                    # 如果是在原文件夹处理，需要替换原文件
                    if self.same_folder_var.get():
                        # 删除原文件
                        if os.path.exists(final_output_path):
                            os.remove(final_output_path)
                        # 重命名临时文件
                        os.rename(_output_path, final_output_path)

                    self.log_message(f"✓ 完成: {filename}")
                else:
                    self.log_message(f"✗ 错误: {filename} - {process.stderr[:100]}")

            except Exception as e:
                self.log_message(f"✗ 异常: {filename} - {str(e)}")

            self.processed_files += 1
            self.update_progress()

        # 处理完成
        if self.processing:
            self.status_var.set(f"处理完成: {self.processed_files}/{self.total_files} 个文件")
            self.current_file_var.set("")
            messagebox.showinfo("完成", f"音频处理完成！\n处理了 {self.processed_files}/{self.total_files} 个文件")
        else:
            self.status_var.set("处理已停止")

        # 重置按钮状态
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.processing = False

    def start_processing(self):
        # 验证参数
        if not self.audio_folder_var.get():
            messagebox.showerror("错误", "请选择输入文件夹！")
            return

        # 检查ffmpeg是否可用
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("错误", "未找到ffmpeg！请确保ffmpeg已安装并添加到系统PATH中。")
            return

        # 重置状态
        self.processing = True
        self.total_files = 0
        self.processed_files = 0
        self.progress_var.set(0)
        self.status_var.set("正在准备...")

        # 更新按钮状态
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # 在新线程中处理音频
        thread = threading.Thread(target=self.process_audio)
        thread.daemon = True
        thread.start()

    def stop_processing(self):
        self.processing = False
        self.status_var.set("正在停止...")
        self.log_message("用户请求停止处理...")


def main():
    root = tk.Tk()
    app = AudioNormalizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()