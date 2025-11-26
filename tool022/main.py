# -*- coding:gbk -*-
import os
import shutil


def get_all_files(directory):
    """
    获取指定目录下所有文件的绝对路径
    :param directory: 目录路径
    :return: 文件绝对路径列表
    """
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths


def dele_repeat_file(_files):
    num = 0
    for _file in _files:
        num += 1
        name, ext = os.path.splitext(_file)
        if ext == ".mp3":
            if os.path.exists(name + ".flac"):
                # os.remove(_file)
                print(f"delete:{_file}")
                path, naem = os.path.split(_file)
                destination_path1 = os.path.join(r"E:\Kin-Desktop\新建文件夹 (2)\sour", naem)
                shutil.move(_file, destination_path1)


# 去除重名mp3
if __name__ == "__main__":
    _path = r"F:\绘星痕数据-音频\音乐库"
    _list = get_all_files(_path)
    # _list = read_m3u(_path)
    dele_repeat_file(_list)