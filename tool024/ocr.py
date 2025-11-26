import pyautogui
from paddleocr import PaddleOCR
import numpy as np
import time


class PaddleOCRRecognizer:
    def __init__(self, use_angle_cls=True, lang='en'):
        self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang)

    def screenshot_and_ocr_paddle(self, region=None):
        """使用PaddleOCR进行识别"""
        # 截屏
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()

        # 转换为numpy数组
        img_array = np.array(screenshot)

        # OCR识别
        result = self.ocr.ocr(img_array, cls=True)

        # 提取文字
        texts = []
        if result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                texts.append((text, confidence))

        return texts, img_array


# region=(x1, y1, x2, y2) -> (text, confidence)
def ocr_specific_region(x1, y1, x2, y2):
    """识别屏幕上特定区域的文字"""
    recognizer = PaddleOCRRecognizer()
    return recognizer.screenshot_and_ocr_paddle(region=(x1, y1, x2 - x1, y2 - y1))[0]


if __name__ == "__main__":
    print(ocr_specific_region(0, 0, 1920, 1080))
