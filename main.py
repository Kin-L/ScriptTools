# # 文件批量重名脚本（通用）
# import tool001.main
#
# # 批量选取音乐文件 -> m3u
# import tool002.main
#
# # 统计音乐文件时长
# import tool003.main
#
# # 依靠文件名批量选取并移动文件
# import tool004.main
#
# # 使用spine将json文件转化为spine文件
# import tool005.main
#
# # 提取音乐文件内嵌的歌词
# import tool006.main
#
# # lrc转srt文件，并对复数相同时间戳进行拆分到多个srt文件
# import tool007.main
#
# # lrc转srt文件
# import tool008.main
#
# # LRC文件拆分为多段
# import tool009.main
#
# # 繁简转化
# import tool010.main
#
# # srt文件转化为lrc文件
# import tool011.main
#
# # 多段LRC文件合一
# import tool012.main
#
# # 批量音量标准化
# import tool013.main
#
# # 使用音乐文件和单张图片，批量制作视频
# import tool014.main
#
# # 将目录中skel文件转化为json
# import tool015.main
#
# # 灵魂潮汐, 深空之眼, 环行旅舍 包体解密
# import tool016.main
#
# # json文件修改图集识别位置
# import tool017.main
#
# # UE批量图片解包
# import tool018.main
#
# # 拼接多个音频片段
# import tool019.main
#
# # UE解包拆分为.atlas与.json文件
# import tool020.main
#
# # atlas图理文件对png文件解包
# import tool021.main
#
# # 去除重名mp3
# import tool022.main
#
# # 移动文件到自身文件名的文件夹内
# import tool023.main
#
# # Astrofox
# import tool024.main
#
# # AE批量渲染前置批量图片裁剪
# import tool025.main
#
# # 音频文件歌词提取工具
# import tool026.main
#
# # 文件批量改名移动复制，修改音乐文件元数据信息（EXCEL）
# import tool027.main
#
# # WEM音频文件音乐文件转格式
# import tool028.main

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
from pathlib import Path


class ToolLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("工具启动器")
        self.root.geometry("800x500")
        self.root.minsize(600, 400)

        # 配置样式
        self.setup_styles()

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            self.main_frame,
            text="工具列表",
            font=("Microsoft YaHei", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # 创建工具列表容器（使用Frame + Canvas实现可滚动列表）
        self.create_scrollable_frame()

        # 工具配置列表 - 这里是可拓展的部分
        self.tools = [
            {
                "name": "M3U播放列表生成器",
                "description": "用于生成M3U格式的播放列表文件，支持自定义文件名列表和输出路径设置",
                "path": "./tool002/main.py"
            },
            {
                "name": "音频时长统计工具",
                "description": "统计音乐文件时长",
                "path": "./tool003/main.py"
            },
            {
                "name": "繁简字转换工具",
                "description": "批量转换文本文件中的繁简字，支持多种转换模式",
                "path": "./tool010/main.py"
            },
            {
                "name": "音频音量标准化工具",
                "description": "将音频文件音量标准化到指定LUFS值，支持多种音频格式",
                "path": "./tool013/main.py"
            },
            {
                "name": "音频片段拼接工具",
                "description": "拼接多个音频片段文件为一个音频文件",
                "path": "./tool019/main.py"
            },
            {
                "name": "音频文件歌词提取工具",
                "description": "分离音频文件歌词文本到同目录文件名的lrc文件中",
                "path": "./tool026/main.py"
            },
            {
                "name": "文件管理工具",
                "description": "管理文件和文件夹，可生成包含文件信息的Excel表格，支持音频文件元数据提取",
                "path": "./tool027/main.py"
            },
            {
                "name": "WEM音频文件转换器",
                "description": "将WEM格式音频文件转换为FLAC或WAV格式",
                "path": "./tool028/main.py"
            }
            # 后续添加新工具只需在这里增加字典条目
        ]

        # 加载工具列表
        self.load_tools()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置按钮样式
        style.configure(
            "Tool.TButton",
            font=("Microsoft YaHei", 10),
            padding=6
        )

        # 配置描述文本样式
        style.configure(
            "Description.TLabel",
            font=("Microsoft YaHei", 10),
            wraplength=550,  # 文本换行宽度
            justify=tk.LEFT
        )

        # 配置工具名称样式
        style.configure(
            "Name.TLabel",
            font=("Microsoft YaHei", 12, "bold"),
            foreground="#2c3e50"
        )

    def create_scrollable_frame(self):
        """创建可滚动的框架用于展示工具列表"""
        # 创建画布和滚动条
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(canvas_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        # 创建用于放置工具项的框架
        self.tools_frame = ttk.Frame(self.canvas)
        canvas_window = self.canvas.create_window((0, 0), window=self.tools_frame, anchor="nw")

        # 绑定事件以更新滚动区域
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(canvas_window, width=event.width)

        self.tools_frame.bind("<Configure>", on_configure)
        self.canvas.bind("<Configure>", on_configure)

        # 关键修改：绑定鼠标滚轮事件到画布和主框架
        # 让滚轮在整个列表区域都能生效
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows系统
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)  # Linux系统
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)  # Linux系统

    def _on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # Windows系统
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Linux系统
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def load_tools(self):
        """加载工具列表到界面"""
        for i, tool in enumerate(self.tools):
            # 创建每行的框架
            row_frame = ttk.Frame(self.tools_frame)
            row_frame.pack(fill=tk.X, pady=(0, 15))

            # 工具信息区域
            info_frame = ttk.Frame(row_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # 工具名称
            name_label = ttk.Label(
                info_frame,
                text=tool["name"],
                style="Name.TLabel"
            )
            name_label.pack(anchor=tk.W, pady=(0, 5))

            # 工具描述
            desc_label = ttk.Label(
                info_frame,
                text=tool["description"],
                style="Description.TLabel"
            )
            desc_label.pack(anchor=tk.W)

            # 打开按钮
            open_btn = ttk.Button(
                row_frame,
                text="打开",
                style="Tool.TButton",
                command=lambda path=tool["path"]: self.launch_tool(path)
            )
            open_btn.pack(side=tk.RIGHT, padx=(10, 0), anchor=tk.CENTER)

            # 添加分隔线
            if i < len(self.tools) - 1:
                separator = ttk.Separator(self.tools_frame, orient="horizontal")
                separator.pack(fill=tk.X, pady=(0, 15))

    def launch_tool(self, tool_path):
        """启动指定路径的工具"""
        try:
            # 检查文件是否存在
            if not Path(tool_path).exists():
                messagebox.showerror("错误", f"工具文件不存在：\n{tool_path}")
                return

            # 启动工具（使用subprocess打开新进程）
            if os.name == 'nt':  # Windows系统
                subprocess.Popen(['python', tool_path], shell=True)
            else:  # 类Unix系统
                subprocess.Popen(['python3', tool_path])

            messagebox.showinfo("提示", f"正在启动工具...\n{tool_path}")

        except Exception as e:
            messagebox.showerror("启动失败", f"无法启动工具：\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ToolLauncherGUI(root)
    root.mainloop()