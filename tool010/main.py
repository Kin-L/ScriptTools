from opencc import OpenCC
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading


class BatchChineseConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("中文繁简转换工具")
        self.root.geometry("600x500")

        # 转换器配置
        self.converters = {
            's2t': ('简体到繁体', OpenCC('s2t')),
            't2s': ('繁体到简体', OpenCC('t2s')),
            's2tw': ('简体到台湾正体', OpenCC('s2tw')),
            'tw2s': ('台湾正体到简体', OpenCC('tw2s')),
            's2hk': ('简体到香港繁体', OpenCC('s2hk')),
            'hk2s': ('香港繁体到简体', OpenCC('hk2s'))
        }

        self.selected_files = []
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="中文繁简批量转换工具",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.file_listbox = tk.Listbox(file_frame, height=8, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 文件操作按钮
        ttk.Button(file_frame, text="选择文件",
                   command=self.select_files).grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Button(file_frame, text="清除列表",
                   command=self.clear_files).grid(row=1, column=1, sticky=tk.W)

        # 转换设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="转换设置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 转换类型选择
        ttk.Label(settings_frame, text="转换类型:").grid(row=0, column=0, sticky=tk.W)

        self.conversion_var = tk.StringVar(value='s2t')
        conversion_combo = ttk.Combobox(settings_frame, textvariable=self.conversion_var,
                                        values=list(self.converters.keys()), state="readonly")
        conversion_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        conversion_combo.bind('<<ComboboxSelected>>', self.on_conversion_change)

        # 转换类型描述
        self.conversion_desc = ttk.Label(settings_frame, text=self.converters['s2t'][0])
        self.conversion_desc.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))

        # 备份选项
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="创建备份文件 (.bak)",
                        variable=self.backup_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # 进度显示
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="开始转换",
                   command=self.start_conversion).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出",
                   command=self.root.quit).pack(side=tk.LEFT)

        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        progress_frame.columnconfigure(0, weight=1)

        # 绑定事件
        self.file_listbox.bind('<Delete>', lambda e: self.remove_selected_files())

    def select_files(self):
        """选择多个文件"""
        files = filedialog.askopenfilenames(
            title="选择要转换的文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )

        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    display_name = os.path.basename(file_path)
                    self.file_listbox.insert(tk.END, display_name)

            self.update_status(f"已选择 {len(files)} 个文件")

    def clear_files(self):
        """清除文件列表"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status("文件列表已清除")

    def remove_selected_files(self):
        """移除选中的文件"""
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.selected_files.pop(index)
            self.file_listbox.delete(index)

        self.update_status(f"剩余 {len(self.selected_files)} 个文件")

    def on_conversion_change(self, event):
        """转换类型改变时更新描述"""
        conversion_type = self.conversion_var.get()
        self.conversion_desc.config(text=self.converters[conversion_type][0])

    def update_status(self, message):
        """更新状态信息"""
        self.progress_label.config(text=message)
        self.root.update()

    def start_conversion(self):
        """开始转换（在新线程中）"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要转换的文件！")
            return

        # 在新线程中运行转换，避免界面冻结
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()

    def convert_files(self):
        """执行文件转换"""
        conversion_type = self.conversion_var.get()
        create_backup = self.backup_var.get()
        cc = self.converters[conversion_type][1]

        total_files = len(self.selected_files)
        success_count = 0

        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        for i, file_path in enumerate(self.selected_files):
            try:
                # 更新进度
                self.update_status(f"正在转换: {os.path.basename(file_path)} ({i + 1}/{total_files})")

                # 创建备份
                if create_backup:
                    backup_path = file_path + '.bak'
                    import shutil
                    shutil.copy2(file_path, backup_path)

                # 读取和转换文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                converted_content = cc.convert(content)

                # 写回原文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)

                success_count += 1

            except Exception as e:
                self.update_status(f"转换失败: {os.path.basename(file_path)} - {str(e)}")

            finally:
                self.progress['value'] = i + 1

        # 显示完成信息
        if success_count == total_files:
            self.update_status(f"转换完成！成功转换 {success_count} 个文件")
            messagebox.showinfo("完成", f"成功转换 {success_count} 个文件！")
        else:
            self.update_status(f"转换完成！成功 {success_count}/{total_files} 个文件")
            messagebox.showwarning("完成",
                                   f"转换完成！\n成功: {success_count} 个文件\n失败: {total_files - success_count} 个文件")

        # 重置进度条
        self.progress['value'] = 0

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


# 简化版本（如果不需要GUI）
class SimpleBatchConverter:
    def __init__(self):
        self.converters = {
            's2t': OpenCC('s2t'),
            't2s': OpenCC('t2s'),
            's2tw': OpenCC('s2tw'),
            'tw2s': OpenCC('tw2s')
        }

    def convert_selected_files(self):
        """简单的文件选择转换"""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        # 选择文件
        files = filedialog.askopenfilenames(
            title="选择要转换的文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )

        if not files:
            print("没有选择文件")
            return

        # 选择转换类型
        conversion_type = input("请输入转换类型 (s2t: 简到繁, t2s: 繁到简): ").strip()
        if conversion_type not in self.converters:
            print("错误的转换类型")
            return

        cc = self.converters[conversion_type]

        # 转换文件
        for file_path in files:
            try:
                print(f"转换中: {file_path}")

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                converted_content = cc.convert(content)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)

                print(f"✓ 成功: {file_path}")

            except Exception as e:
                print(f"✗ 失败: {file_path} - {e}")


# 使用示例
if __name__ == "__main__":
    # 使用GUI版本
    app = BatchChineseConverter()
    app.run()

    # 或者使用简单版本（取消注释下面的行）
    # converter = SimpleBatchConverter()
    # converter.convert_selected_files()