import os
import sys


def create_m3u_from_txt(txt_file_path, directory_path, output_m3u_path=None):
    """
    根据txt文件中的文件名列表生成m3u播放列表

    Args:
        txt_file_path: 包含文件名的txt文件路径
        directory_path: 要搜索的目录路径
        output_m3u_path: 输出的m3u文件路径（可选）
    """

    # 检查输入文件是否存在
    if not os.path.exists(txt_file_path):
        print(f"错误：txt文件 '{txt_file_path}' 不存在")
        return

    if not os.path.exists(directory_path):
        print(f"错误：目录 '{directory_path}' 不存在")
        return

    # 如果没有指定输出文件，使用txt文件名加上.m3u后缀
    if output_m3u_path is None:
        base_name = os.path.splitext(txt_file_path)[0]
        output_m3u_path = base_name + ".m3u"

    # 支持的音频文件扩展名
    audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.wma'}

    # 读取txt文件中的文件名列表
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            # 读取所有行，去除空白字符，过滤空行
            file_names = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取txt文件时出错: {e}")
        return

    print(f"从txt文件中读取了 {len(file_names)} 个文件名")

    # 构建目录中所有音频文件的映射（文件名不带后缀 -> 完整路径）
    audio_files_map = {}
    missing_files = []

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in audio_extensions:
                # 如果同一个文件名有多个版本，保留第一个找到的
                if name not in audio_files_map:
                    audio_files_map[name] = os.path.join(root, file)

    print(f"在目录中找到 {len(audio_files_map)} 个音频文件")

    # 生成m3u文件内容
    m3u_content = ["#EXTM3U\n"]  # m3u文件头
    found_count = 0

    for file_name in file_names:
        if file_name in audio_files_map:
            file_path = audio_files_map[file_name]
            m3u_content.append(file_path + "\n")
            found_count += 1
            print(f"✓ 找到: {file_name} -> {file_path}")
        else:
            missing_files.append(file_name)
            print(f"✗ 未找到: {file_name}")

    # 写入m3u文件
    try:
        with open(output_m3u_path, 'w', encoding='utf-8') as f:
            f.writelines(m3u_content)
        print(f"\n成功生成m3u文件: {output_m3u_path}")
        print(f"找到文件: {found_count}/{len(file_names)}")
    except Exception as e:
        print(f"写入m3u文件时出错: {e}")
        return

    # 输出未找到的文件
    if missing_files:
        print(f"\n未找到的文件 ({len(missing_files)} 个):")
        for missing_file in missing_files:
            print(f"  - {missing_file}")

        # 可选：将未找到的文件列表保存到另一个txt文件
        missing_file_path = os.path.splitext(output_m3u_path)[0] + "_missing.txt"
        try:
            with open(missing_file_path, 'w', encoding='utf-8') as f:
                for missing_file in missing_files:
                    f.write(missing_file + "\n")
            print(f"未找到的文件列表已保存到: {missing_file_path}")
        except Exception as e:
            print(f"保存未找到文件列表时出错: {e}")


def main():
    """主函数，支持命令行参数和交互式输入"""
    if len(sys.argv) == 3:
        # 命令行参数方式
        txt_file = sys.argv[1]
        directory = sys.argv[2]
        output_file = None
    elif len(sys.argv) == 4:
        txt_file = sys.argv[1]
        directory = sys.argv[2]
        output_file = sys.argv[3]
    else:
        # 交互式输入方式
        txt_file = r'input.txt'
        directory = r"E:\Kin-Audio\星塔旅人\FLAC"
        output_file = r'output.m3u'
        if not output_file:
            output_file = None

    create_m3u_from_txt(txt_file, directory, output_file)


if __name__ == "__main__":
    main()