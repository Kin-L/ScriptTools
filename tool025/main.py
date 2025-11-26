import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import os


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理器")
        self.root.geometry("450x250")

        # 存储选择的文件路径
        self.selected_files = []

        # 创建GUI元素
        self.create_widgets()

    def create_widgets(self):
        # 选择图片按钮
        self.select_button = tk.Button(
            self.root,
            text="选择图片",
            command=self.select_images,
            font=("Arial", 12),
            height=2
        )
        self.select_button.pack(pady=10)

        # 显示已选择文件数量
        self.file_count_label = tk.Label(self.root, text="未选择文件")
        self.file_count_label.pack()

        # 勾选按钮框架
        self.checkbox_frame = tk.Frame(self.root)
        self.checkbox_frame.pack(pady=10)

        # 制作封面勾选按钮
        self.cover_var = tk.BooleanVar()
        self.cover_check = tk.Checkbutton(
            self.checkbox_frame,
            text="制作封面 (1080×1080 PNG)",
            variable=self.cover_var,
            font=("Arial", 10)
        )
        self.cover_check.pack(anchor="w")

        # 制作背景勾选按钮
        self.back_var = tk.BooleanVar()
        self.back_check = tk.Checkbutton(
            self.checkbox_frame,
            text="制作背景 (1920×1080 JPG)",
            variable=self.back_var,
            font=("Arial", 10)
        )
        self.back_check.pack(anchor="w")

        # 开始处理按钮
        self.process_button = tk.Button(
            self.root,
            text="开始处理",
            command=self.process_images,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            height=2,
            width=15
        )
        self.process_button.pack(pady=10)

    def select_images(self):
        # 弹窗选择多个图片文件
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png")]
        )

        if files:
            self.selected_files = list(files)
            self.file_count_label.config(text=f"已选择 {len(self.selected_files)} 个文件")

    def process_images(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择图片文件！")
            return

        if not (self.cover_var.get() or self.back_var.get()):
            messagebox.showwarning("警告", "请至少选择一个处理选项！")
            return

        try:
            processed_count = 0

            for file_path in self.selected_files:
                # 打开原始图片
                original_image = Image.open(file_path)

                # 获取原文件目录和文件名（不含扩展名）
                file_dir = os.path.dirname(file_path)
                file_name = os.path.splitext(os.path.basename(file_path))[0]

                if self.cover_var.get():
                    # 制作封面：居中最大化裁剪成正方形，然后调整为1080×1080
                    cover_image = self.crop_to_square(original_image)
                    cover_image = cover_image.resize((1080, 1080), Image.Resampling.LANCZOS)

                    # 如果图片是RGBA模式，保持RGBA模式用于PNG输出
                    if cover_image.mode == 'RGBA':
                        cover_image = cover_image
                    else:
                        cover_image = cover_image.convert('RGB')

                    # 保存为PNG格式
                    cover_path = os.path.join(file_dir, f"{file_name}-cover.png")
                    cover_image.save(cover_path, "PNG")
                    processed_count += 1
                    print(f"已生成封面: {cover_path}")

                if self.back_var.get():
                    # 制作背景：居中最大化裁剪成16:9，然后调整为1920×1080
                    back_image = self.crop_to_16_9(original_image)
                    back_image = back_image.resize((1920, 1080), Image.Resampling.LANCZOS)

                    # 转换为RGB模式，因为JPEG不支持透明通道
                    if back_image.mode in ('RGBA', 'LA', 'P'):
                        # 创建白色背景
                        background = Image.new('RGB', back_image.size, (255, 255, 255))
                        if back_image.mode == 'P':
                            back_image = back_image.convert('RGBA')
                        # 将透明图片合成到白色背景上
                        background.paste(back_image, mask=back_image.split()[-1] if back_image.mode == 'RGBA' else None)
                        back_image = background
                    else:
                        back_image = back_image.convert('RGB')

                    # 保存为JPG格式
                    back_path = os.path.join(file_dir, f"{file_name}-back.jpg")
                    back_image.save(back_path, "JPEG", quality=95)
                    processed_count += 1
                    print(f"已生成背景: {back_path}")

            messagebox.showinfo("完成", f"成功处理 {processed_count} 个图片！")

        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出现错误：{str(e)}")

    def crop_to_square(self, image):
        """将图片居中最大化裁剪成正方形"""
        width, height = image.size

        # 计算裁剪区域
        if width > height:
            # 横图，裁剪左右
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        else:
            # 竖图或方图，裁剪上下
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width

        return image.crop((left, top, right, bottom))

    def crop_to_16_9(self, image):
        """将图片居中最大化裁剪成16:9横纵比"""
        width, height = image.size
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            # 图片更宽，需要裁剪左右
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = height
        else:
            # 图片更高，需要裁剪上下
            new_height = int(width / target_ratio)
            left = 0
            top = (height - new_height) // 2
            right = width
            bottom = top + new_height

        return image.crop((left, top, right, bottom))


def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()