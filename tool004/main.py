import os
import shutil


def separate_files_by_ids(source_folder, target_folder, id_list):
    """
    将源文件夹中含有特定数字ID的文件分离到目标文件夹

    Args:
        source_folder (str): 源文件夹路径
        target_folder (str): 目标文件夹路径
        id_list (list): 数字ID列表
    """
    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 将数字ID转换为字符串，便于查找
    id_strings = [str(id_num) for id_num in id_list]

    # 统计变量
    moved_count = 0
    total_files = 0

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        # 只处理文件，不处理文件夹
        if os.path.isfile(file_path):
            total_files += 1

            # 检查文件名是否包含任一数字ID
            for id_str in id_strings:
                if id_str in filename:
                    # 构建目标文件路径
                    target_path = os.path.join(target_folder, filename)

                    # 移动文件
                    shutil.move(file_path, target_path)
                    moved_count += 1
                    print(f"已移动: {filename}")
                    break  # 找到匹配后跳出内层循环

    print(f"\n分离完成！")
    print(f"总共处理文件数: {total_files}")
    print(f"成功移动文件数: {moved_count}")


# 要查找的数字ID列表
target_ids = [
    10117227,
    57045797,
    69411733,
    83734452,
    118599416,
    123534417,
    154693135,
    175679783,
    176359323,
    188095415,
    197464413,
    225284797,
    225487733,
    304165978,
    312025219,
    344670814,
    351114616,
    376189799,
    398504901,
    406299063,
    422006722,
    451824903,
    457021451,
    533887731,
    568141208,
    582953320,
    630087737,
    651599959,
    665608075,
    673548794,
    745765777,
    783140677,
    788089835,
    791091089,
    795747288,
    816342641,
    880876879,
    931970440,
    936295416,
    948258271,
    1033945089,
    1034508063,
    1042605695,

]

# 使用示例
if __name__ == "__main__":
    # 设置源文件夹路径（请修改为实际路径）
    source_directory = "E:\Kin-Audio\星塔旅人\wem"

    # 设置目标文件夹路径（请修改为实际路径）
    target_directory = "E:\Kin-Audio\星塔旅人\System"

    # 执行文件分离
    separate_files_by_ids(source_directory, target_directory, target_ids)