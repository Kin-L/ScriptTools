import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil


class WavFileMover:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV文件整理工具")
        self.root.geometry("500x200")

        # 存储选择的文件路径
        self.selected_files = []

        # 创建GUI元素
        self.create_widgets()

    def create_widgets(self):
        # 选择WAV文件按钮
        self.select_button = tk.Button(
            self.root,
            text="选择WAV文件",
            command=self.select_wav_files,
            font=("Arial", 12),
            height=2,
            width=20
        )
        self.select_button.pack(pady=10)

        # 显示已选择文件数量
        self.file_count_label = tk.Label(self.root, text="未选择文件", font=("Arial", 10))
        self.file_count_label.pack(pady=5)

        # 显示文件列表的文本框
        self.file_list_text = tk.Text(self.root, height=4, width=60)
        self.file_list_text.pack(pady=5)
        self.file_list_text.config(state=tk.DISABLED)

        # 开始移动按钮
        self.move_button = tk.Button(
            self.root,
            text="开始移动文件",
            command=self.move_files,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            height=2,
            width=20
        )
        self.move_button.pack(pady=10)

    def select_wav_files(self):
        # 弹窗选择多个WAV文件
        files = filedialog.askopenfilenames(
            title="选择WAV文件",
            filetypes=[("WAV文件", "*.wav")]
        )

        if files:
            self.selected_files = list(files)
            self.file_count_label.config(text=f"已选择 {len(self.selected_files)} 个WAV文件")

            # 更新文件列表显示
            self.file_list_text.config(state=tk.NORMAL)
            self.file_list_text.delete(1.0, tk.END)
            for file_path in self.selected_files:
                self.file_list_text.insert(tk.END, f"{file_path}\n")
            self.file_list_text.config(state=tk.DISABLED)

    def move_files(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择WAV文件！")
            return

        try:
            moved_count = 0
            skipped_count = 0

            for file_path in self.selected_files:
                success = self.move_single_file(file_path)
                if success:
                    moved_count += 1
                else:
                    skipped_count += 1

            result_message = f"文件移动完成！\n成功移动: {moved_count} 个文件"
            if skipped_count > 0:
                result_message += f"\n跳过: {skipped_count} 个文件（可能已存在或出错）"

            messagebox.showinfo("完成", result_message)

            # 清空选择列表
            self.selected_files = []
            self.file_count_label.config(text="未选择文件")
            self.file_list_text.config(state=tk.NORMAL)
            self.file_list_text.delete(1.0, tk.END)
            self.file_list_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("错误", f"移动文件时出现错误：{str(e)}")

    def move_single_file(self, file_path):
        """移动单个WAV文件到对应的子文件夹"""
        try:
            # 获取文件所在目录和文件名（不含扩展名）
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]

            # 创建目标文件夹（以文件名命名）
            target_dir = os.path.join(file_dir, file_name_without_ext)

            # 如果目标文件夹不存在，则创建
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # 目标文件路径
            target_path = os.path.join(target_dir, file_name)

            # 如果目标文件已存在，询问是否覆盖
            if os.path.exists(target_path):
                response = messagebox.askyesno(
                    "文件已存在",
                    f"文件 {file_name} 在目标文件夹中已存在。是否覆盖？"
                )
                if not response:
                    return False

            # 移动文件
            shutil.move(file_path, target_path)
            print(f"已移动: {file_path} -> {target_path}")
            return True

        except Exception as e:
            print(f"移动文件失败 {file_path}: {str(e)}")
            return False


def main():
    root = tk.Tk()
    app = WavFileMover(root)
    root.mainloop()


if __name__ == "__main__":
    main()