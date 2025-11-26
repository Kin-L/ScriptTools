import subprocess
import os
from os import path, remove, listdir
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

vgm_path = r"D:\Kin-project\PythonProjects\GamesUnpack\vgmstream-win64\vgmstream-cli.exe"
ffmpeg_path = r"D:\Program Files\ffmpeg\ffmpeg.exe"


class WEMConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WEM音频文件转换器")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        # 变量
        self.format_var = tk.StringVar(value="FLAC")
        self.keep_original_var = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="准备就绪")

        self.setup_ui()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="WEM音频文件转换器",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 格式选择
        format_frame = ttk.LabelFrame(main_frame, text="输出格式", padding="10")
        format_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        flac_radio = ttk.Radiobutton(format_frame, text="FLAC",
                                     variable=self.format_var, value="FLAC")
        flac_radio.grid(row=0, column=0, sticky=tk.W)

        wav_radio = ttk.Radiobutton(format_frame, text="WAV",
                                    variable=self.format_var, value="WAV")
        wav_radio.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        # 原文件处理选项
        file_option_frame = ttk.LabelFrame(main_frame, text="文件选项", padding="10")
        file_option_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        keep_check = ttk.Checkbutton(file_option_frame, text="保留原WEM文件",
                                     variable=self.keep_original_var)
        keep_check.grid(row=0, column=0, sticky=tk.W)

        # 选择按钮
        select_button = ttk.Button(main_frame, text="选择文件或文件夹并开始",
                                   command=self.select_and_convert)
        select_button.grid(row=3, column=0, columnspan=2, pady=20)

        # 进度条
        progress_label = ttk.Label(main_frame, text="转换进度:")
        progress_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))

        progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                       maximum=100, length=460)
        progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # 状态显示
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # 配置列权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def select_and_convert(self):
        """选择文件或文件夹并开始转换"""
        choice = messagebox.askquestion("选择方式",
                                        "选择文件还是文件夹？\n是 - 选择文件\n否 - 选择文件夹",
                                        icon='question')

        if choice == 'yes':
            files = filedialog.askopenfilenames(
                title="选择WEM文件",
                filetypes=[("WEM files", "*.wem"), ("All files", "*.*")]
            )
            if files:
                # 在新线程中执行转换
                threading.Thread(target=self.convert_files, args=(files,), daemon=True).start()
        else:
            folder = filedialog.askdirectory(title="选择包含WEM文件的文件夹")
            if folder:
                # 在新线程中执行转换
                threading.Thread(target=self.convert_folder, args=(folder,), daemon=True).start()

    def convert_folder(self, folder_path):
        """转换文件夹中的所有WEM文件"""
        try:
            # 获取所有WEM文件
            wem_files = []
            for file in listdir(folder_path):
                if file.lower().endswith('.wem'):
                    wem_files.append(path.join(folder_path, file))

            if not wem_files:
                messagebox.showwarning("警告", "选择的文件夹中没有找到WEM文件！")
                return

            self.convert_file_list(wem_files, folder_path)

        except Exception as e:
            self.show_error(f"转换过程中出现错误: {str(e)}")

    def convert_files(self, file_paths):
        """转换选择的多个文件"""
        if not file_paths:
            return

        # 获取文件所在目录（假设所有文件在同一个目录）
        output_dir = path.dirname(file_paths[0])
        self.convert_file_list(file_paths, output_dir)

    def convert_file_list(self, file_paths, output_dir):
        """转换文件列表"""
        total_files = len(file_paths)
        converted_count = 0

        for i, file_path in enumerate(file_paths):
            try:
                # 更新状态
                filename = path.basename(file_path)
                self.status_var.set(f"正在转换: {filename} ({i + 1}/{total_files})")

                # 转换单个文件
                if self.convert_single_file(file_path, output_dir):
                    converted_count += 1

                # 更新进度
                self.progress_var.set((i + 1) / total_files * 100)
                self.root.update_idletasks()

            except Exception as e:
                self.show_error(f"转换文件 {filename} 时出错: {str(e)}")
                continue

        # 完成提示
        self.status_var.set(f"转换完成！成功转换 {converted_count}/{total_files} 个文件")
        messagebox.showinfo("完成", f"转换完成！\n成功转换 {converted_count}/{total_files} 个文件")
        self.progress_var.set(0)

    def convert_single_file(self, file_path, output_dir):
        """转换单个WEM文件"""
        try:
            filename = path.basename(file_path)
            file_base = path.splitext(filename)[0]

            # 1. 用 vgmstream 解码为 WAV
            wav_path = path.join(output_dir, f"{file_base}.wav")
            subprocess.run([
                vgm_path,
                "-o", wav_path,
                file_path
            ], check=True, capture_output=True)

            # 根据选择的格式处理
            if self.format_var.get() == "FLAC":
                # 2. 用 FFmpeg 转 WAV 为 FLAC
                output_path = path.join(output_dir, f"{file_base}.flac")
                subprocess.run([
                    ffmpeg_path,
                    "-i", wav_path,
                    "-c:a", "flac",
                    output_path
                ], check=True, capture_output=True)
            else:
                # 如果是WAV格式，直接保留解码后的WAV文件
                output_path = wav_path
                # 不需要额外处理，文件已经在正确位置

            # 清理临时文件
            if path.exists(wav_path) and self.format_var.get() == "FLAC":
                remove(wav_path)

            # 如果不保留原文件，删除WEM文件
            if not self.keep_original_var.get() and path.exists(file_path):
                remove(file_path)

            return True

        except subprocess.CalledProcessError as e:
            print(f"转换失败: {e}")
            return False
        except Exception as e:
            print(f"发生错误: {e}")
            return False

    def show_error(self, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
        self.status_var.set("转换过程中出现错误")


def convert_audio_single(oldn, newn, path_out):
    """原有的转换函数（保留兼容性）"""
    try:
        # 1. 用 vgmstream 解码为 WAV
        wav_path = path.join(path_out, f"{newn}.wav")
        wem_path = path.join(path_out, f"{oldn}.wem")
        subprocess.run(
            [vgm_path,
             "-o", wav_path,
             wem_path], check=True)

        # 2. 用 FFmpeg 转 WAV 为 FLAC
        subprocess.run([
            ffmpeg_path,
            "-i", wav_path,
            "-c:a", "flac",
            path.join(path_out, f"{newn}.flac")
        ])

    finally:
        if path.exists(wav_path):
            remove(wav_path)
        if path.exists(wem_path):
            remove(wem_path)


if __name__ == "__main__":
    # 检查必要的工具是否存在
    if not path.exists(vgm_path):
        print(f"错误: 找不到 vgmstream-cli.exe 在 {vgm_path}")
        print("请确保vgmstream-cli.exe存在于指定路径")

    if not path.exists(ffmpeg_path):
        print(f"错误: 找不到 ffmpeg.exe 在 {ffmpeg_path}")
        print("请确保ffmpeg.exe存在于指定路径")

    root = tk.Tk()
    app = WEMConverterGUI(root)
    root.mainloop()