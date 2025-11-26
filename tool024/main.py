import pyautogui
import os
import pyperclip
from tool024.region_change import detect_region_change
click = pyautogui.click
sleep = pyautogui.sleep
send = pyautogui.write
press = pyautogui.press

def get_files_os(directory):
    """使用os.listdir获取目录下所有文件和文件夹"""
    try:
        files = os.listdir(directory)
        return files
    except FileNotFoundError:
        print(f"目录 {directory} 不存在")
        return []


# Astrofox批量渲染
if __name__ == "__main__":
    dire = r"D:\Temp"
    for name in get_files_os(dire):
        filepath = os.path.join(dire, name)
        # print(filepath,  name)
        click(306, 52)
        sleep(0.5)
        click(341, 244)
        sleep(0.5)
        click(860,450)
        sleep(0.3)
        press('backspace')
        sleep(0.3)
        press('backspace')
        sleep(0.3)
        send("25")
        sleep(0.5)
        click(958,410)
        sleep(0.5)
        click(911,433)
        sleep(0.5)
        click(1154,325)
        sleep(0.5)
        pyperclip.copy(filepath)
        sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        sleep(0.5)
        press('enter')
        sleep(0.5)
        click(1153,283)
        sleep(0.5)
        pyperclip.copy(filepath.replace(".flac", ".mp4"))
        sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        sleep(0.5)
        press('enter')
        sleep(0.5)
        click(866,647)
        sleep(2)
        detect_region_change(1062, 555, 1126, 591, 1, 0.9)
        click(1093,577)
        sleep(0.5)
