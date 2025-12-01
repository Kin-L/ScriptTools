import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


def concat_audio_files_filter(input_files, output_file):
    """
    使用FFmpeg的filter_complex拼接音频文件
    适用于不同格式的音频，会自动进行格式转换
    """
    try:
        # 检查输入文件是否存在
        for file in input_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"文件不存在: {file}")

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
        return True, f"音频拼接完成: {output_file}"

    except FileNotFoundError as e:
        return False, str(e)
    except subprocess.CalledProcessError as e:
        return False, f"拼接失败: {e.stderr.decode()}"
    except Exception as e:
        return False, f"未知错误: {e}"


class AudioConcatenatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频文件拼接工具")
        self.root.geometry("600x500")

        # 设置窗口图标（可选）
        # self.root.iconbitmap('icon.ico')

        self.create_widgets()

    def create_widgets(self):
        # 输入文件区域
        input_frame = tk.LabelFrame(self.root, text="输入音频文件路径", padx=10, pady=10)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 说明标签
        tk.Label(input_frame, text="每行一个音频文件路径，将按顺序拼接:").pack(anchor="w")

        # 滚动文本框用于输入文件路径
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, width=70)
        self.input_text.pack(fill="both", expand=True, pady=5)

        # 按钮框架
        button_frame = tk.Frame(input_frame)
        button_frame.pack(fill="x", pady=5)

        # 添加文件按钮
        tk.Button(button_frame, text="添加文件", command=self.add_files).pack(side="left", padx=5)

        # 清空按钮
        tk.Button(button_frame, text="清空列表", command=self.clear_list).pack(side="left", padx=5)

        # 输出文件区域
        output_frame = tk.LabelFrame(self.root, text="输出文件路径", padx=10, pady=10)
        output_frame.pack(fill="x", padx=10, pady=5)

        # 输出路径输入框和浏览按钮
        output_inner_frame = tk.Frame(output_frame)
        output_inner_frame.pack(fill="x", pady=5)

        tk.Label(output_inner_frame, text="输出文件:").pack(side="left", padx=5)

        self.output_var = tk.StringVar()
        output_entry = tk.Entry(output_inner_frame, textvariable=self.output_var, width=50)
        output_entry.pack(side="left", fill="x", expand=True, padx=5)

        tk.Button(output_inner_frame, text="浏览", command=self.browse_output).pack(side="right", padx=5)

        # 操作按钮区域
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=10)

        # 拼接按钮
        tk.Button(action_frame, text="开始拼接", command=self.start_concat,
                  bg="lightblue", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        # 退出按钮
        tk.Button(action_frame, text="退出", command=self.root.quit).pack(side="right", padx=5)

        # 状态标签
        self.status_label = tk.Label(self.root, text="准备就绪", anchor="w", relief="sunken", bd=1)
        self.status_label.pack(fill="x", padx=10, pady=5)

    def add_files(self):
        """添加文件到输入列表"""
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.flac *.aac *.m4a"), ("所有文件", "*.*")]
        )

        if files:
            for file in files:
                self.input_text.insert("end", file + "\n")
            self.update_status(f"添加了 {len(files)} 个文件")

    def clear_list(self):
        """清空输入列表"""
        self.input_text.delete("1.0", "end")
        self.update_status("输入列表已清空")

    def browse_output(self):
        """选择输出文件路径"""
        output_file = filedialog.asksaveasfilename(
            title="保存输出文件",
            defaultextension=".flac",
            filetypes=[("FLAC文件", "*.flac"), ("MP3文件", "*.mp3"),
                       ("WAV文件", "*.wav"), ("所有文件", "*.*")]
        )

        if output_file:
            self.output_var.set(output_file)

    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def start_concat(self):
        """开始拼接音频文件"""
        # 获取输入文件列表
        input_text = self.input_text.get("1.0", "end-1c").strip()

        if not input_text:
            messagebox.showerror("错误", "请输入至少一个音频文件路径")
            return

        # 获取输出文件路径
        output_file = self.output_var.get().strip()

        if not output_file:
            messagebox.showerror("错误", "请输入输出文件路径")
            return

        # 解析输入文件列表
        input_files = [line.strip() for line in input_text.split("\n") if line.strip()]

        # 检查文件数量
        if len(input_files) < 2:
            messagebox.showwarning("警告", "需要至少2个音频文件进行拼接")
            return

        # 显示确认对话框
        confirm = messagebox.askyesno("确认",
                                      f"将拼接 {len(input_files)} 个音频文件:\n\n" +
                                      "\n".join([os.path.basename(f) for f in input_files]) +
                                      f"\n\n输出到: {output_file}\n\n是否继续?")

        if not confirm:
            return

        # 开始拼接
        self.update_status("正在拼接音频文件，请稍候...")

        success, message = concat_audio_files_filter(input_files, output_file)

        if success:
            messagebox.showinfo("成功", message)
            self.update_status("音频拼接完成")
        else:
            messagebox.showerror("失败", message)
            self.update_status("音频拼接失败")


def main():
    root = tk.Tk()
    app = AudioConcatenatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()