import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import shutil
import logging
from pathlib import Path
import subprocess
from datetime import datetime
import threading

# 音频文件处理相关
try:
    from mutagen import File
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    from mutagen.wave import WAVE

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("警告: mutagen库未安装，音乐文件元数据功能将不可用")


class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件管理工具")
        self.root.geometry("800x600")

        # 创建必要的目录
        self.cache_dir = Path("./cache")
        self.log_dir = Path("./log")
        self.cache_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # 设置日志
        self.setup_logging()

        # 存储文件路径
        self.file_paths = []

        # 音频文件后缀
        self.audio_extensions = {'.wav', '.mp3', '.flac', '.opus'}

        # 创建GUI
        self.create_gui()

        # Excel文件路径
        self.excel_path = self.cache_dir / "temp.xlsx"

        self.log("应用程序启动完成")

    def setup_logging(self):
        """设置日志系统"""
        log_file = self.log_dir / "operation.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger()

    def log(self, message, level='info'):
        """记录日志并在GUI中显示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        if level == 'info':
            self.logger.info(message)
            self.log_text.insert(tk.END, f"INFO: {log_message}\n")
        elif level == 'warning':
            self.logger.warning(message)
            self.log_text.insert(tk.END, f"WARNING: {log_message}\n")
        elif level == 'error':
            self.logger.error(message)
            self.log_text.insert(tk.END, f"ERROR: {log_message}\n")

        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def create_gui(self):
        """创建GUI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        # 按钮
        self.add_file_btn = ttk.Button(button_frame, text="添加文件", command=self.add_files)
        self.add_file_btn.grid(row=0, column=0, padx=(0, 10))

        self.add_folder_btn = ttk.Button(button_frame, text="添加文件夹", command=self.add_folder)
        self.add_folder_btn.grid(row=0, column=1, padx=(0, 10))

        self.generate_btn = ttk.Button(button_frame, text="生成表格", command=self.generate_table)
        self.generate_btn.grid(row=0, column=2, padx=(0, 10))

        self.apply_btn = ttk.Button(button_frame, text="应用更改", command=self.apply_changes)
        self.apply_btn.grid(row=0, column=3)

        # 路径显示文本框
        ttk.Label(main_frame, text="选择的文件/文件夹路径:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        self.paths_text = scrolledtext.ScrolledText(main_frame, height=8, width=80)
        self.paths_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 日志显示
        ttk.Label(main_frame, text="操作日志:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(title="选择文件")
        if files:
            self.file_paths.extend(files)
            self.update_paths_display()
            self.log(f"添加了 {len(files)} 个文件")

    def add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            self.file_paths.append(folder)
            self.update_paths_display()
            self.log(f"添加了文件夹: {folder}")

    def update_paths_display(self):
        """更新路径显示"""
        self.paths_text.delete(1.0, tk.END)
        for path in self.file_paths:
            self.paths_text.insert(tk.END, path + '\n')

    def get_audio_metadata(self, file_path):
        """获取音频文件的元数据"""
        if not MUTAGEN_AVAILABLE:
            return {"title": "", "artist": "", "album": ""}

        try:
            audio = File(file_path)
            if audio is None:
                return {"title": "", "artist": "", "album": ""}

            metadata = {
                "title": audio.get("title", [""])[0] if audio.get("title") else "",
                "artist": audio.get("artist", [""])[0] if audio.get("artist") else "",
                "album": audio.get("album", [""])[0] if audio.get("album") else ""
            }

            # 确保返回字符串
            for key in metadata:
                if not isinstance(metadata[key], str):
                    metadata[key] = str(metadata[key])

            return metadata
        except Exception as e:
            self.log(f"读取元数据失败 {file_path}: {str(e)}", 'warning')
            return {"title": "", "artist": "", "album": ""}

    def generate_table(self):
        """生成Excel表格"""
        if not self.file_paths:
            messagebox.showwarning("警告", "请先添加文件或文件夹")
            return

        self.progress.start()
        self.log("开始生成表格...")

        # 在新线程中执行以避免界面冻结
        thread = threading.Thread(target=self._generate_table_thread)
        thread.daemon = True
        thread.start()

    def _generate_table_thread(self):
        """在后台线程中生成表格"""
        try:
            data = []

            for path in self.file_paths:
                if os.path.isfile(path):
                    self.process_file_path(path, data)
                elif os.path.isdir(path):
                    self.process_directory(path, data)

            # 创建DataFrame
            columns = [
                '所在目录', '操作类型', '文件名(无后缀)', '文件后缀',
                '标题', '艺术家', '专辑', '原路径',
                '备份标题', '备份艺术家', '备份专辑'
            ]

            df = pd.DataFrame(data, columns=columns)

            # 保存Excel文件
            with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='文件管理')

                # 获取工作表并隐藏列
                worksheet = writer.sheets['文件管理']
                worksheet.column_dimensions['H'].hidden = True  # 原路径
                worksheet.column_dimensions['I'].hidden = True  # 备份标题
                worksheet.column_dimensions['J'].hidden = True  # 备份艺术家
                worksheet.column_dimensions['K'].hidden = True  # 备份专辑

            self.root.after(0, self._on_table_generated)

        except Exception as e:
            self.root.after(0, lambda: self.log(f"生成表格失败: {str(e)}", 'error'))
            self.root.after(0, lambda: self.progress.stop())

    def process_file_path(self, file_path, data):
        """处理单个文件路径"""
        try:
            path_obj = Path(file_path)
            directory = str(path_obj.parent)
            stem = path_obj.stem
            suffix = path_obj.suffix.lower()

            is_audio = suffix in self.audio_extensions
            metadata = self.get_audio_metadata(file_path) if is_audio else {"title": "", "artist": "", "album": ""}

            row = [
                directory,  # 所在目录
                '移动',  # 操作类型
                stem,  # 文件名(无后缀)
                suffix,  # 文件后缀
                metadata.get('title', ''),  # 标题
                metadata.get('artist', ''),  # 艺术家
                metadata.get('album', ''),  # 专辑
                file_path,  # 原路径
                metadata.get('title', ''),  # 备份标题
                metadata.get('artist', ''),  # 备份艺术家
                metadata.get('album', '')  # 备份专辑
            ]

            data.append(row)
            self.log(f"处理文件: {file_path}")

        except Exception as e:
            self.log(f"处理文件失败 {file_path}: {str(e)}", 'error')

    def process_directory(self, dir_path, data):
        """处理目录中的所有文件"""
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.process_file_path(file_path, data)

            self.log(f"处理目录: {dir_path}")

        except Exception as e:
            self.log(f"处理目录失败 {dir_path}: {str(e)}", 'error')

    def _on_table_generated(self):
        """表格生成完成后的回调"""
        self.progress.stop()
        self.log(f"表格生成完成: {self.excel_path}")

        # 打开Excel文件
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.excel_path)
            else:  # macOS 或 Linux
                subprocess.run(['open', self.excel_path] if os.name == 'posix' else ['xdg-open', self.excel_path])

            messagebox.showinfo("完成", f"表格已生成并保存至:\n{self.excel_path}\n\n请编辑后保存，然后点击'应用更改'")

        except Exception as e:
            messagebox.showinfo("完成",
                                f"表格已生成:\n{self.excel_path}\n\n但无法自动打开文件，请手动打开编辑后点击'应用更改'")
            self.log(f"无法打开Excel文件: {str(e)}", 'warning')

    def apply_changes(self):
        """应用更改"""
        if not self.excel_path.exists():
            messagebox.showerror("错误", f"未找到表格文件:\n{self.excel_path}\n请先生成表格")
            return

        self.progress.start()
        self.log("开始应用更改...")

        # 在新线程中执行
        thread = threading.Thread(target=self._apply_changes_thread)
        thread.daemon = True
        thread.start()

    def _apply_changes_thread(self):
        """在后台线程中应用更改"""
        try:
            # 读取Excel文件
            df = pd.read_excel(self.excel_path)
            success_count = 0
            error_count = 0

            for index, row in df.iterrows():
                try:
                    if self.process_row(row):
                        success_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    self.log(f"处理第{index + 2}行失败: {str(e)}", 'error')
                    error_count += 1

            self.root.after(0, lambda: self._on_changes_applied(success_count, error_count))

        except Exception as e:
            self.root.after(0, lambda: self.log(f"读取表格失败: {str(e)}", 'error'))
            self.root.after(0, lambda: self.progress.stop())

    def process_row(self, row):
        """处理单行数据"""
        original_path = row['原路径']
        operation = row['操作类型']
        new_directory = row['所在目录']
        new_stem = str(row['文件名(无后缀)'])
        new_suffix = row['文件后缀']

        # 检查文件是否存在
        if not os.path.exists(original_path):
            self.log(f"文件不存在: {original_path}", 'error')
            return False

        current_path = original_path

        # 1. 删除操作
        if operation == '删除':
            try:
                if os.path.isfile(current_path):
                    os.remove(current_path)
                    self.log(f"删除文件: {current_path}")
                elif os.path.isdir(current_path):
                    shutil.rmtree(current_path)
                    self.log(f"删除文件夹: {current_path}")
                return True
            except Exception as e:
                self.log(f"删除失败 {current_path}: {str(e)}", 'error')
                return False

        # 2. 移动/复制操作
        original_dir = str(Path(original_path).parent)
        if new_directory != original_dir:
            new_path_in_dir = os.path.join(new_directory, Path(current_path).name)

            try:
                if operation == '移动':
                    os.makedirs(new_directory, exist_ok=True)
                    shutil.move(current_path, new_path_in_dir)
                    current_path = new_path_in_dir
                    self.log(f"移动文件: {original_path} -> {current_path}")
                elif operation == '复制':
                    os.makedirs(new_directory, exist_ok=True)
                    if os.path.isfile(current_path):
                        shutil.copy2(current_path, new_path_in_dir)
                    else:
                        shutil.copytree(current_path, new_path_in_dir)
                    current_path = new_path_in_dir
                    self.log(f"复制文件: {original_path} -> {current_path}")
            except Exception as e:
                self.log(f"{operation}操作失败 {original_path} -> {new_path_in_dir}: {str(e)}", 'error')
                return False

        # 3. 重命名操作
        current_path_obj = Path(current_path)
        if current_path_obj.stem != new_stem or current_path_obj.suffix != new_suffix:
            new_path = os.path.join(current_path_obj.parent, new_stem + new_suffix)

            try:
                os.rename(current_path, new_path)
                current_path = new_path
                self.log(f"重命名: {current_path_obj.name} -> {Path(new_path).name}")
            except Exception as e:
                self.log(f"重命名失败 {current_path} -> {new_path}: {str(e)}", 'error')
                return False

        # 4. 元数据修改（仅对音频文件）
        if Path(current_path).suffix.lower() in self.audio_extensions:
            if not self.update_audio_metadata(current_path, row):
                return False

        # 5. 转码操作
        original_suffix = Path(original_path).suffix.lower()
        if (original_suffix in self.audio_extensions and
                Path(current_path).suffix.lower() in self.audio_extensions and
                original_suffix != Path(current_path).suffix.lower()):

            if not self.transcode_audio(current_path):
                return False

        return True

    def update_audio_metadata(self, file_path, row):
        """更新音频文件元数据"""
        if not MUTAGEN_AVAILABLE:
            self.log("mutagen库不可用，跳过元数据更新", 'warning')
            return True

        try:
            audio = File(file_path)
            if audio is None:
                self.log(f"无法读取音频文件: {file_path}", 'warning')
                return True

            # 检查元数据是否有变化
            backup_title = str(row['备份标题'])
            backup_artist = str(row['备份艺术家'])
            backup_album = str(row['备份专辑'])

            new_title = str(row['标题'])
            new_artist = str(row['艺术家'])
            new_album = str(row['专辑'])

            changes_made = False

            if pd.notna(new_title) and str(new_title) != str(backup_title):
                audio['title'] = str(new_title)
                changes_made = True
                self.log(f"更新标题: {file_path}")

            if pd.notna(new_artist) and str(new_artist) != str(backup_artist):
                audio['artist'] = str(new_artist)
                changes_made = True
                self.log(f"更新艺术家: {file_path}")

            if pd.notna(new_album) and str(new_album) != str(backup_album):
                audio['album'] = str(new_album)
                changes_made = True
                self.log(f"更新专辑: {file_path}")

            if changes_made:
                audio.save()
                self.log(f"保存元数据: {file_path}")

            return True

        except Exception as e:
            self.log(f"更新元数据失败 {file_path}: {str(e)}", 'error')
            return False

    def transcode_audio(self, file_path):
        """转码音频文件"""
        try:
            temp_path = file_path + '.temp'

            # 构建ffmpeg命令
            cmd = [
                'ffmpeg', '-i', file_path,
                '-y',  # 覆盖输出文件
                temp_path
            ]

            self.log(f"开始转码: {file_path}")

            # 执行转码
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # 删除原文件，重命名临时文件
                os.remove(file_path)
                os.rename(temp_path, file_path)
                self.log(f"转码完成: {file_path}")
                return True
            else:
                self.log(f"转码失败 {file_path}: {result.stderr}", 'error')
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

        except subprocess.TimeoutExpired:
            self.log(f"转码超时: {file_path}", 'error')
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
        except Exception as e:
            self.log(f"转码异常 {file_path}: {str(e)}", 'error')
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def _on_changes_applied(self, success_count, error_count):
        """更改应用完成后的回调"""
        self.progress.stop()

        message = f"操作完成!\n成功: {success_count} 个文件\n失败: {error_count} 个文件"

        if error_count == 0:
            messagebox.showinfo("完成", message)
        else:
            messagebox.showwarning("完成", message)

        self.log(f"应用更改完成 - 成功: {success_count}, 失败: {error_count}")


def main():
    """主函数"""
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()