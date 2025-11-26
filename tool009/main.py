def split_lrc_file_simple(input_file, lines_per_file=300):
    """简化版的LRC文件拆分函数"""

    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 拆分并保存
    for i, start in enumerate(range(0, len(lines), lines_per_file)):
        output_file = f"{input_file[:-4]}_part{i + 1}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines[start:start + lines_per_file])

        print(f"已创建: {output_file}")


# 使用
split_lrc_file_simple(r"D:\Kin-project\PythonProjects\JAConverter\test1\test1-o2.TXT", 300)