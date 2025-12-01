import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading
import subprocess
import platform


def create_m3u_from_list(file_names_list, directory_path, output_m3u_path=None):
    """
    根据文件名列表生成m3u播放列表

    Args:
        file_names_list: 文件名列表
        directory_path: 要搜索的目录路径
        output_m3u_path: 输出的m3u文件路径（可选）
    """

    if not directory_path:
        return "错误：请指定音频目录", False

    if not os.path.exists(directory_path):
        return f"错误：目录 '{directory_path}' 不存在", False

    if not file_names_list:
        return "错误：文件名列表为空", False

    # 如果没有指定输出文件，创建cache文件夹并使用当前时间命名
    if output_m3u_path is None:
        cache_dir = "./cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        timestamp = datetime.now().strftime("%y-%m-%d %H-%M-%S")
        output_m3u_path = os.path.join(cache_dir, f"{timestamp}.m3u")

    # 支持的音频文件扩展名
    audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}

    result_log = []
    result_log.append(f"输入了 {len(file_names_list)} 个文件名\n")

    # 构建目录中所有音频文件的映射（文件名不带后缀 -> 完整路径）
    audio_files_map = {}
    missing_files = []

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in audio_extensions:
                # 如果同一个文件名有多个版本，保留第一个找到的
                if name not in audio_files_map:
                    audio_files_map[name] = os.path.join(root, file)

    result_log.append(f"在目录中找到 {len(audio_files_map)} 个音频文件\n")

    # 生成m3u文件内容
    m3u_content = ["#EXTM3U\n"]  # m3u文件头
    found_count = 0

    for file_name in file_names_list:
        # 去除空白字符
        file_name = file_name.strip()
        if not file_name:
            continue

        if file_name in audio_files_map:
            file_path = audio_files_map[file_name]
            m3u_content.append(file_path + "\n")
            found_count += 1
            result_log.append(f"✓ 找到: {file_name}")
        else:
            missing_files.append(file_name)
            result_log.append(f"✗ 未找到: {file_name}")

    # 写入m3u文件
    try:
        with open(output_m3u_path, 'w', encoding='utf-8') as f:
            f.writelines(m3u_content)
        result_log.append(f"\n成功生成m3u文件: {output_m3u_path}")
        result_log.append(f"找到文件: {found_count}/{len(file_names_list)}")
    except Exception as e:
        return f"写入m3u文件时出错: {e}", False

    # 输出未找到的文件
    if missing_files:
        result_log.append(f"\n未找到的文件 ({len(missing_files)} 个):")
        for missing_file in missing_files:
            result_log.append(f"  - {missing_file}")

        # 可选：将未找到的文件列表保存到另一个txt文件
        missing_file_path = os.path.splitext(output_m3u_path)[0] + "_missing.txt"
        try:
            with open(missing_file_path, 'w', encoding='utf-8') as f:
                for missing_file in missing_files:
                    f.write(missing_file + "\n")
            result_log.append(f"未找到的文件列表已保存到: {missing_file_path}")
        except Exception as e:
            result_log.append(f"保存未找到文件列表时出错: {e}")

    return "\n".join(result_log), True, output_m3u_path


def open_file_in_explorer(file_path):
    """在文件资源管理器中打开文件所在目录"""
    try:
        if platform.system() == "Windows":
            # Windows系统
            subprocess.run(f'explorer /select,"{file_path}"')
        elif platform.system() == "Darwin":
            # macOS系统
            subprocess.run(["open", "-R", file_path])
        else:
            # Linux系统
            subprocess.run(["xdg-open", os.path.dirname(file_path)])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开文件所在目录: {e}")


class M3UGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U播放列表生成器")
        self.root.geometry("900x800")

        # 设置样式
        self.setup_styles()

        # 创建界面
        self.create_widgets()

        # 变量初始化
        self.output_path = None

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置颜色
        self.bg_color = "#f0f0f0"
        self.frame_bg = "#ffffff"
        self.button_color = "#4CAF50"
        self.button_hover = "#45a049"

        self.root.configure(bg=self.bg_color)

    def create_widgets(self):
        """创建界面组件"""

        # 标题
        title_label = tk.Label(
            self.root,
            text="M3U播放列表生成器",
            font=("Microsoft YaHei", 20, "bold"),
            bg=self.bg_color,
            fg="#333333"
        )
        title_label.pack(pady=(20, 10))

        # 说明标签
        desc_label = tk.Label(
            self.root,
            text="在下方输入框中输入文件名列表（每行一个文件名，无需扩展名）",
            font=("Microsoft YaHei", 10),
            bg=self.bg_color,
            fg="#666666"
        )
        desc_label.pack(pady=(0, 20))

        # 主框架
        main_frame = tk.Frame(self.root, bg=self.frame_bg, relief=tk.RIDGE, bd=2)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # 文件名输入区域
        input_frame = tk.Frame(main_frame, bg=self.frame_bg)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 输入框标签
        input_label = tk.Label(
            input_frame,
            text="文件名列表:",
            font=("Microsoft YaHei", 11),
            bg=self.frame_bg,
            anchor="w"
        )
        input_label.pack(fill=tk.X, pady=(0, 5))

        # 文件名输入文本框
        self.filenames_text = tk.Text(
            input_frame,
            font=("Consolas", 10),
            bd=2,
            relief=tk.GROOVE,
            wrap=tk.NONE,
            height=10
        )
        self.filenames_text.pack(fill=tk.BOTH, expand=True)

        # 输入框滚动条
        input_scrollbar_y = tk.Scrollbar(self.filenames_text)
        input_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.filenames_text.config(yscrollcommand=input_scrollbar_y.set)
        input_scrollbar_y.config(command=self.filenames_text.yview)

        input_scrollbar_x = tk.Scrollbar(self.filenames_text, orient=tk.HORIZONTAL)
        input_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.filenames_text.config(xscrollcommand=input_scrollbar_x.set)
        input_scrollbar_x.config(command=self.filenames_text.xview)

        # 示例按钮
        example_frame = tk.Frame(input_frame, bg=self.frame_bg)
        example_frame.pack(fill=tk.X, pady=(5, 0))

        example_button = tk.Button(
            example_frame,
            text="插入示例文件名",
            font=("Microsoft YaHei", 9),
            bg="#9E9E9E",
            fg="white",
            activebackground="#757575",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.insert_example
        )
        example_button.pack(side=tk.LEFT)

        clear_input_button = tk.Button(
            example_frame,
            text="清空输入",
            font=("Microsoft YaHei", 9),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_filename_input
        )
        clear_input_button.pack(side=tk.LEFT, padx=(5, 0))

        # 目录输入
        dir_frame = tk.Frame(main_frame, bg=self.frame_bg)
        dir_frame.pack(fill=tk.X, padx=20, pady=10)

        dir_label = tk.Label(
            dir_frame,
            text="音频目录:",
            font=("Microsoft YaHei", 11),
            bg=self.frame_bg,
            width=15,
            anchor="w"
        )
        dir_label.pack(side=tk.LEFT)

        self.dir_entry = tk.Entry(
            dir_frame,
            font=("Microsoft YaHei", 10),
            bd=2,
            relief=tk.GROOVE,
            width=50
        )
        self.dir_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        dir_button = tk.Button(
            dir_frame,
            text="浏览",
            font=("Microsoft YaHei", 10),
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.browse_directory
        )
        dir_button.pack(side=tk.RIGHT)

        # 输出文件选项
        output_frame = tk.Frame(main_frame, bg=self.frame_bg)
        output_frame.pack(fill=tk.X, padx=20, pady=10)

        output_label = tk.Label(
            output_frame,
            text="输出设置:",
            font=("Microsoft YaHei", 11),
            bg=self.frame_bg,
            width=15,
            anchor="w"
        )
        output_label.pack(side=tk.LEFT)

        self.output_var = tk.StringVar(value="auto")
        tk.Radiobutton(
            output_frame,
            text="自动生成（./cache/时间戳.m3u）",
            variable=self.output_var,
            value="auto",
            font=("Microsoft YaHei", 10),
            bg=self.frame_bg,
            command=self.toggle_output_entry
        ).pack(anchor="w", pady=(0, 5))

        tk.Radiobutton(
            output_frame,
            text="自定义路径",
            variable=self.output_var,
            value="custom",
            font=("Microsoft YaHei", 10),
            bg=self.frame_bg,
            command=self.toggle_output_entry
        ).pack(anchor="w")

        self.output_entry_frame = tk.Frame(output_frame, bg=self.frame_bg)
        self.output_entry_frame.pack(fill=tk.X, padx=(15, 0), pady=(5, 0))

        self.output_entry = tk.Entry(
            self.output_entry_frame,
            font=("Microsoft YaHei", 10),
            bd=2,
            relief=tk.GROOVE,
            width=45,
            state="disabled"
        )
        self.output_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        self.output_button = tk.Button(
            self.output_entry_frame,
            text="浏览",
            font=("Microsoft YaHei", 10),
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.browse_output_file,
            state="disabled"
        )
        self.output_button.pack(side=tk.RIGHT)

        # 控制按钮
        button_frame = tk.Frame(main_frame, bg=self.frame_bg)
        button_frame.pack(pady=30)

        self.generate_button = tk.Button(
            button_frame,
            text="生成M3U文件",
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            height=2,
            command=self.generate_m3u
        )
        self.generate_button.pack(side=tk.LEFT, padx=10)

        self.open_button = tk.Button(
            button_frame,
            text="打开输出目录",
            font=("Microsoft YaHei", 12),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            height=2,
            command=self.open_output_directory,
            state="disabled"
        )
        self.open_button.pack(side=tk.LEFT, padx=10)

        clear_all_button = tk.Button(
            button_frame,
            text="清空所有",
            font=("Microsoft YaHei", 12),
            bg="#ff9800",
            fg="white",
            activebackground="#f57c00",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            height=2,
            command=self.clear_all
        )
        clear_all_button.pack(side=tk.LEFT, padx=10)

        # 日志输出区域
        log_frame = tk.Frame(main_frame, bg=self.frame_bg)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        log_label = tk.Label(
            log_frame,
            text="生成日志:",
            font=("Microsoft YaHei", 11),
            bg=self.frame_bg,
            anchor="w"
        )
        log_label.pack(fill=tk.X, pady=(0, 5))

        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 10),
            bd=2,
            relief=tk.GROOVE,
            wrap=tk.WORD,
            height=8
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 日志滚动条
        log_scrollbar = tk.Scrollbar(self.log_text)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)

    def insert_example(self):
        """插入示例文件名"""
        example_text = """歌曲1
歌曲2
歌曲3
音乐A
音乐B
audio_file_01
my_song_2023"""

        self.filenames_text.delete(1.0, tk.END)
        self.filenames_text.insert(1.0, example_text)

    def clear_filename_input(self):
        """清空文件名输入"""
        self.filenames_text.delete(1.0, tk.END)

    def browse_directory(self):
        """浏览目录"""
        dir_path = filedialog.askdirectory(title="选择音频目录")
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def browse_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存M3U文件",
            defaultextension=".m3u",
            filetypes=[("M3U files", "*.m3u"), ("All files", "*.*")]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def toggle_output_entry(self):
        """切换输出路径输入框状态"""
        if self.output_var.get() == "custom":
            self.output_entry.config(state="normal")
            self.output_button.config(state="normal")
        else:
            self.output_entry.config(state="disabled")
            self.output_button.config(state="disabled")

    def generate_m3u(self):
        """生成M3U文件"""
        # 从文本框获取文件名列表
        filenames_text = self.filenames_text.get(1.0, tk.END).strip()
        if not filenames_text:
            messagebox.showwarning("警告", "请输入文件名列表")
            return

        file_names_list = [line.strip() for line in filenames_text.split('\n') if line.strip()]

        directory = self.dir_entry.get().strip()

        if not directory:
            messagebox.showwarning("警告", "请指定音频目录")
            return

        # 确定输出路径
        if self.output_var.get() == "custom":
            output_file = self.output_entry.get().strip()
            if not output_file:
                messagebox.showwarning("警告", "请选择或输入输出文件路径")
                return
        else:
            output_file = None

        # 禁用按钮，防止重复点击
        self.generate_button.config(state="disabled", text="生成中...")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"正在处理 {len(file_names_list)} 个文件名...\n")
        self.log_text.insert(tk.END, "正在生成M3U文件，请稍候...\n")
        self.root.update()

        # 在新线程中执行生成操作
        def run_generation():
            try:
                result, success, output_path = create_m3u_from_list(file_names_list, directory, output_file)
                self.root.after(0, self.on_generation_complete, result, success, output_path)
            except Exception as e:
                self.root.after(0, self.on_generation_error, str(e))

        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()

    def on_generation_complete(self, result, success, output_path):
        """生成完成后的回调"""
        self.generate_button.config(state="normal", text="生成M3U文件")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, result)

        if success:
            self.output_path = output_path
            self.open_button.config(state="normal")
            messagebox.showinfo("成功", "M3U文件生成成功！")
        else:
            self.open_button.config(state="disabled")
            messagebox.showerror("错误", "生成M3U文件失败！")

    def on_generation_error(self, error_msg):
        """生成出错后的回调"""
        self.generate_button.config(state="normal", text="生成M3U文件")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"生成过程中发生错误:\n{error_msg}")
        self.open_button.config(state="disabled")
        messagebox.showerror("错误", f"生成过程中发生错误:\n{error_msg}")

    def open_output_directory(self):
        """打开输出目录"""
        if self.output_path and os.path.exists(self.output_path):
            open_file_in_explorer(self.output_path)
        else:
            messagebox.showwarning("警告", "输出文件不存在，请先生成M3U文件")

    def clear_all(self):
        """清空所有输入"""
        self.filenames_text.delete(1.0, tk.END)
        self.dir_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.output_var.set("auto")
        self.toggle_output_entry()
        self.open_button.config(state="disabled")
        self.output_path = None


def main():
    """主函数"""
    root = tk.Tk()
    app = M3UGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()