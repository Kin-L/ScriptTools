import subprocess
import os
import json


def exportSpineJson(input_json_path, out_path=None):
    SPINE_EXE = r"D:\Program Files (Green)\spinepro_3.8.75\Spine.exe"
    _INPUT_JSON = input_json_path
    nowdir = os.getcwd()
    Export_JSON = rf"{nowdir}\template.export.json"
    OUTPUT_SPINE = rf"{nowdir}\cache.spine"

    cmd = [
        SPINE_EXE,
        "-i", _INPUT_JSON,
        "-o", OUTPUT_SPINE,
        "-r", "cache"
    ]
    try:
        print(f"正在导入 {_INPUT_JSON} 到 Spine 项目...")
        subprocess.run(cmd, check=True)
        print(f"成功创建 Spine 项目: {OUTPUT_SPINE}")
    except subprocess.CalledProcessError as e:
        print(f"导入失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

    # 读取JSON文件
    with open(_INPUT_JSON, 'r', encoding='utf-8') as file:
        ijdata = json.load(file)
    with open(Export_JSON, 'r', encoding='utf-8') as file:
        ejdata = json.load(file)
    if len(ijdata["animations"]) == 1:
        if out_path:
            _path = os.path.join(out_path, os.path.split(_INPUT_JSON)[1])
        else:
            _path = _INPUT_JSON
        ejdata["output"] = _path.replace(".json", ".mov")
    else:
        if out_path:
            ejdata["output"] = out_path
        else:
            ejdata["output"] = os.path.split(_INPUT_JSON)[0]
    ejdata["project"] = OUTPUT_SPINE
    with open(Export_JSON, 'w', encoding='utf-8') as file:
        json.dump(ejdata, file, ensure_ascii=False, indent=4)
    cmd = [
        SPINE_EXE,
        "-e", Export_JSON
    ]
    try:
        print(f"正在渲染导出 {_INPUT_JSON} ...")
        subprocess.run(cmd, check=True)
        print(f"成功导出: {_INPUT_JSON}")
    except subprocess.CalledProcessError as e:
        print(f"导入失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


# 使用示例
if __name__ == "__main__":
    INPUT_JSON = r"E:\Unpack\尘白禁区\登录界面spine\sp_login_bg019\sp_login_bg019.json"
    exportSpineJson(INPUT_JSON)
