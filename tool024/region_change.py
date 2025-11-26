import pyautogui
import time


def detect_region_change(x1, y1, x2, y2, interval=1, threshold=0.9):
    """
    检测指定区域是否发生变化

    参数:
    - x1, y1: 区域左上角坐标
    - x2, y2: 区域右下角坐标
    - interval: 检测间隔(秒)
    - threshold: 相似度阈值，低于此值认为发生变化
    """
    # 获取初始截图
    previous_screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

    while True:
        time.sleep(interval)

        # 获取当前截图
        current_screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

        # 比较两张图片
        similarity = compare_images(previous_screenshot, current_screenshot)

        if similarity < threshold:
            print(f"区域发生变化! 相似度: {similarity:.2f}")
            return True

        # 更新前一张截图
        previous_screenshot = current_screenshot


def compare_images(img1, img2):
    """比较两张图片的相似度"""
    # 转换为RGB模式（如果不是）
    if img1.mode != 'RGB':
        img1 = img1.convert('RGB')
    if img2.mode != 'RGB':
        img2 = img2.convert('RGB')

    # 获取像素数据
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    # 计算相同像素数量
    same_pixels = sum(1 for p1, p2 in zip(pixels1, pixels2) if p1 == p2)

    # 返回相似度比例
    return same_pixels / len(pixels1)