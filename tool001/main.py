import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import shutil
from pathlib import Path


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文件批量重命名工具")
        self.root.geometry("800x700")

        # 创建样式
        self.setup_styles()

        # 创建界面
        self.create_widgets()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="文件批量重命名工具", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 目录选择部分
        dir_frame = ttk.LabelFrame(main_frame, text="目录设置", padding="10")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="目标目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        self.browse_dir_btn = ttk.Button(dir_frame, text="浏览目录", command=self.browse_directory)
        self.browse_dir_btn.grid(row=0, column=2)

        # 选项设置部分
        options_frame = ttk.LabelFrame(main_frame, text="重命名选项", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.ignore_extension_var = tk.BooleanVar(value=True)
        self.ignore_ext_check = ttk.Checkbutton(
            options_frame,
            text="忽略文件后缀（如果新文件名没有后缀，则沿用原文件后缀）",
            variable=self.ignore_extension_var
        )
        self.ignore_ext_check.grid(row=0, column=0, sticky=tk.W)

        # 重命名规则输入部分
        rule_frame = ttk.LabelFrame(main_frame, text="重命名规则", padding="10")
        rule_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        rule_frame.columnconfigure(0, weight=1)
        rule_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 输入文本框
        input_label = ttk.Label(rule_frame, text="输入重命名规则 (格式: 原文件名\\t新文件名)")
        input_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(rule_frame, width=80, height=10)
        self.input_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 示例文本
        example_text = """示例格式:
歌曲1.flac\t新歌曲1.flac
old_name.mp3\tnew_name.mp3
古典音乐.wav\t经典古典.wav

当启用'忽略文件后缀'选项时:
歌曲1\t新歌曲1        # 将保持原文件后缀
音乐文件\t新音乐文件    # 将保持原文件后缀"""

        example_label = ttk.Label(rule_frame, text=example_text, foreground="gray")
        example_label.grid(row=2, column=0, sticky=tk.W)

        # 按钮部分
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)

        self.execute_btn = ttk.Button(btn_frame, text="执行重命名", command=self.execute_renaming)
        self.execute_btn.grid(row=0, column=0, padx=(0, 10))

        self.clear_btn = ttk.Button(btn_frame, text="清空结果", command=self.clear_results)
        self.clear_btn.grid(row=0, column=1, padx=(0, 10))

        self.load_file_btn = ttk.Button(btn_frame, text="从文件加载规则", command=self.load_from_file)
        self.load_file_btn.grid(row=0, column=2, padx=(0, 10))

        # 结果显示部分
        result_frame = ttk.LabelFrame(main_frame, text="执行结果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        self.result_text = scrolledtext.ScrolledText(result_frame, width=80, height=15, state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def load_from_file(self):
        """从文件加载重命名规则"""
        file_path = filedialog.askopenfilename(
            title="选择重命名规则文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
                self.status_var.set(f"已从文件加载规则: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")

    def clear_results(self):
        """清空结果显示"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.status_var.set("已清空结果")

    def parse_rename_rules(self, text_content):
        """解析重命名规则文本"""
        rules = []
        lines = text_content.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # 跳过空行和注释
                continue

            if '\t' in line:
                parts = line.split('\t', 1)  # 只分割第一个制表符
                if len(parts) == 2:
                    old_name, new_name = parts
                    rules.append({
                        'line_num': line_num,
                        'old_name': old_name.strip(),
                        'new_name': new_name.strip(),
                        'original_line': line
                    })
                else:
                    rules.append({
                        'line_num': line_num,
                        'error': f"格式错误: 应包含一个制表符分隔符",
                        'original_line': line
                    })
            else:
                rules.append({
                    'line_num': line_num,
                    'error': f"格式错误: 未找到制表符分隔符",
                    'original_line': line
                })

        return rules

    def get_actual_new_filename(self, old_filename, new_filename, ignore_extension):
        """
        根据选项获取实际的新文件名

        Args:
            old_filename: 原文件名（带后缀）
            new_filename: 新文件名（可能不带后缀）
            ignore_extension: 是否忽略后缀

        Returns:
            实际的新文件名
        """
        if not ignore_extension:
            return new_filename

        # 获取原文件的后缀
        old_name, old_ext = os.path.splitext(old_filename)

        # 获取新文件的后缀
        new_name, new_ext = os.path.splitext(new_filename)

        # 如果新文件名没有指定后缀，则沿用原文件后缀
        if not new_ext:
            return new_filename + old_ext
        else:
            return new_filename

    def find_file_in_directory(self, directory, filename):
        """
        在目录中查找文件，支持模糊匹配（忽略后缀）

        Args:
            directory: 目录路径
            filename: 要查找的文件名

        Returns:
            找到的文件完整路径，如果没找到返回None
        """
        # 首先尝试精确匹配
        exact_path = os.path.join(directory, filename)
        if os.path.exists(exact_path):
            return exact_path

        # 如果启用了忽略后缀选项，尝试模糊匹配
        if self.ignore_extension_var.get():
            target_name, _ = os.path.splitext(filename)

            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_name, file_ext = os.path.splitext(file)
                    if file_name == target_name:
                        return file_path

        return None

    def execute_renaming(self):
        """执行重命名操作"""
        # 获取输入
        directory = self.dir_var.get().strip()
        text_content = self.input_text.get(1.0, tk.END).strip()
        ignore_extension = self.ignore_extension_var.get()

        # 验证输入
        if not directory:
            messagebox.showerror("错误", "请选择目标目录")
            return

        if not os.path.exists(directory):
            messagebox.showerror("错误", "选择的目录不存在")
            return

        if not text_content:
            messagebox.showerror("错误", "请输入重命名规则")
            return

        # 解析规则
        rules = self.parse_rename_rules(text_content)
        if not rules:
            messagebox.showwarning("警告", "未找到有效的重命名规则")
            return

        # 执行重命名
        self.perform_renaming(directory, rules, ignore_extension)

    def perform_renaming(self, directory, rules, ignore_extension):
        """执行实际的重命名操作"""
        # 初始化统计
        stats = {
            'total_rules': len(rules),
            'files_not_found': [],
            'rename_skipped': [],
            'rename_errors': [],
            'rename_success': []
        }

        # 清空结果文本框
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        # 显示开始信息
        self.result_text.insert(tk.END, f"开始执行重命名操作...\n")
        self.result_text.insert(tk.END, f"目标目录: {directory}\n")
        self.result_text.insert(tk.END, f"重命名规则数量: {stats['total_rules']}\n")
        self.result_text.insert(tk.END, f"忽略文件后缀: {'是' if ignore_extension else '否'}\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")
        self.root.update()

        # 遍历规则并执行重命名
        for rule in rules:
            if 'error' in rule:
                # 规则格式错误
                stats['rename_errors'].append({
                    'rule': rule,
                    'error': rule['error']
                })
                continue

            old_name = rule['old_name']
            new_name = rule['new_name']

            # 查找文件（支持忽略后缀的查找）
            old_path = self.find_file_in_directory(directory, old_name)

            if not old_path:
                # 文件不存在
                stats['files_not_found'].append(rule)
                continue

            # 获取实际的文件名（用于显示）
            actual_old_name = os.path.basename(old_path)

            # 获取实际的新文件名（处理后缀）
            actual_new_name = self.get_actual_new_filename(actual_old_name, new_name, ignore_extension)
            new_path = os.path.join(directory, actual_new_name)

            # 检查是否在同一目录下
            old_dir = os.path.dirname(old_path)
            if old_dir != directory:
                stats['rename_errors'].append({
                    'rule': rule,
                    'error': f"文件不在指定目录中: {old_path}"
                })
                continue

            if old_path == new_path:
                # 新旧文件名相同，跳过
                stats['rename_skipped'].append(rule)
                continue

            # 执行重命名
            try:
                # 检查目标文件是否已存在
                if os.path.exists(new_path):
                    stats['rename_errors'].append({
                        'rule': rule,
                        'error': f"目标文件已存在: {actual_new_name}"
                    })
                    continue

                # 执行重命名
                os.rename(old_path, new_path)

                # 更新规则信息以显示实际的文件名
                rule['actual_old_name'] = actual_old_name
                rule['actual_new_name'] = actual_new_name
                stats['rename_success'].append(rule)

            except Exception as e:
                stats['rename_errors'].append({
                    'rule': rule,
                    'error': f"重命名失败: {str(e)}"
                })

        # 显示结果
        self.display_results(stats, ignore_extension)

    def display_results(self, stats, ignore_extension):
        """显示执行结果"""
        self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.result_text.insert(tk.END, "执行结果统计:\n\n")

        # 显示未找到的文件
        if stats['files_not_found']:
            self.result_text.insert(tk.END, f"【未找到的文件】({len(stats['files_not_found'])}个):\n")
            for rule in stats['files_not_found']:
                self.result_text.insert(tk.END, f"  第{rule['line_num']}行: {rule['old_name']}\n")
            self.result_text.insert(tk.END, "\n")

        # 显示跳过的文件
        if stats['rename_skipped']:
            self.result_text.insert(tk.END, f"【跳过的文件】({len(stats['rename_skipped'])}个):\n")
            for rule in stats['rename_skipped']:
                if 'actual_old_name' in rule:
                    self.result_text.insert(tk.END,
                                            f"  第{rule['line_num']}行: 新旧文件名相同 ({rule['actual_old_name']})\n")
                else:
                    self.result_text.insert(tk.END, f"  第{rule['line_num']}行: 新旧文件名相同\n")
            self.result_text.insert(tk.END, "\n")

        # 显示重命名错误
        if stats['rename_errors']:
            self.result_text.insert(tk.END, f"【重命名错误】({len(stats['rename_errors'])}个):\n")
            for error_info in stats['rename_errors']:
                rule = error_info['rule']
                error_msg = error_info['error']
                if 'old_name' in rule:
                    self.result_text.insert(tk.END, f"  第{rule['line_num']}行: {rule['old_name']} -> {error_msg}\n")
                else:
                    self.result_text.insert(tk.END, f"  第{rule['line_num']}行: {error_msg}\n")
            self.result_text.insert(tk.END, "\n")

        # 显示成功的重命名
        if stats['rename_success']:
            self.result_text.insert(tk.END, f"【成功重命名】({len(stats['rename_success'])}个):\n")
            for rule in stats['rename_success']:
                old_display = rule.get('actual_old_name', rule['old_name'])
                new_display = rule.get('actual_new_name', rule['new_name'])
                self.result_text.insert(tk.END, f"  第{rule['line_num']}行: {old_display} -> {new_display}\n")
            self.result_text.insert(tk.END, "\n")

        # 显示统计摘要
        self.result_text.insert(tk.END, "【统计摘要】:\n")
        self.result_text.insert(tk.END, f"  总规则数: {stats['total_rules']}\n")
        self.result_text.insert(tk.END, f"  成功重命名: {len(stats['rename_success'])}\n")
        self.result_text.insert(tk.END, f"  未找到文件: {len(stats['files_not_found'])}\n")
        self.result_text.insert(tk.END, f"  跳过重命名: {len(stats['rename_skipped'])}\n")
        self.result_text.insert(tk.END, f"  重命名错误: {len(stats['rename_errors'])}\n")
        self.result_text.insert(tk.END, f"  忽略后缀模式: {'是' if ignore_extension else '否'}\n")

        # 更新状态栏
        success_count = len(stats['rename_success'])
        total_count = stats['total_rules']
        self.status_var.set(
            f"完成: 成功 {success_count}/{total_count} (忽略后缀: {'是' if ignore_extension else '否'})")

        # 锁定结果文本框
        self.result_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = FileRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()