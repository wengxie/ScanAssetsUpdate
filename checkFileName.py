# -*- coding: utf-8 -*-
import os
import re
from checkFailName import config
from collections import defaultdict
from ScanAssetsUpdate.checkConfigurationTableUpdate import find_all_Configuration_in_InBundle

def get_filenames_with_uppercase_or_space_in_extension(directory):
    """
    获取指定目录中后缀包含大写字母或空格的文件名，并返回它们的路径列表。

    :param directory: 需要检查的目录路径
    :return: 包含大写字母或空格文件路径的列表
    """
    files_with_uppercase = []  # 用于存储后缀包含大写字母的文件路径
    files_with_space = []  # 用于存储后缀包含空格的文件路径
    all_files = []  # 初始化列表用于存储所有扫描到的文件路径

    # 调用 find_all_Configuration_in_InBundle 函数以填充 all_files 列表
    find_all_Configuration_in_InBundle(all_files, directory)

    # 筛选后缀包含大写字母或空格的文件
    for file in all_files:
        _, ext = os.path.splitext(file)
        if re.search(r'[A-Z]', ext):
            files_with_uppercase.append(file)
        if re.search(r' ', ext):
            files_with_space.append(file)

    return files_with_uppercase, files_with_space

def find_duplicate_files(directory):
    """
    查找指定目录及其子目录中的重名 .txt 文件。

    :param directory: 需要检查的目录路径
    :return: 包含重名文件路径的字典
    """
    # 创建一个默认字典，用于保存文件名及其对应的一组路径列表
    files_dict = defaultdict(list)

    # 遍历目录及其子目录中的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            # 将文件名作为字典的键，文件路径作为值存储到列表中
            files_dict[file].append(os.path.join(root, file))

    # 创建一个字典，筛选出有重名的文件
    duplicates = {file: paths for file, paths in files_dict.items() if len(paths) > 1}

    return duplicates

def main():
    """
    主函数，用于调用各函数并打印和保存结果。
    """
    # 指定要检查的目录路径
    # inbundle_directory = os.path.join('E:', os.sep, 'Devglobal', 'client', 'MainProject', 'Assets', 'InBundle')
    fish_directory = os.path.join(config.INBUNDLE_DIRECTORY, 'Fish')
    # 指定输出文件路径，保存到当前工程目录下
    output_file_path = 'checkFailName/checkFileName.txt'

    # 调用函数，获取过滤后的文件路径和文件名列表
    files_with_uppercase, files_with_space = get_filenames_with_uppercase_or_space_in_extension(config.INBUNDLE_DIRECTORY)
    duplicates = find_duplicate_files(fish_directory)

    # 打印统计信息
    print(f"Number of matched files with uppercase: {len(files_with_uppercase)}")
    if len(files_with_uppercase) > 0:
        print("Files with uppercase: ", files_with_uppercase)
    else:
        print("No files with uppercase matched the criteria.")

    print(f"Number of matched files with space: {len(files_with_space)}")
    if len(files_with_space) > 0:
        print("Files with space: ", files_with_space)
    else:
        print("No files with space matched the criteria.")

    if duplicates:
        print("Duplicate files found:")
        for file, paths in duplicates.items():
            print(f"\nFile name: {file}")
            print("Paths:")
            for path in paths:
                print(f"  {path}")
    else:
        print("No duplicate files found.")

    # 写入输出文件，覆盖内容
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("Files with uppercase in extension:\n")
        for file in files_with_uppercase:
            f.write(file + '\n')
            print(file)

        f.write("\nFiles with space in extension:\n")
        for file in files_with_space:
            f.write(file + '\n')
            print(file)

        f.write("\nDuplicate files found:\n")
        if duplicates:
            for file, paths in duplicates.items():
                f.write(f"\nFile name: {file}\n")
                f.write("Paths:\n")
                for path in paths:
                    f.write(f"  {path}\n")
                    print(path)
        else:
            f.write("No duplicate files found.\n")

    # 打印保存结果的信息
    print(f"Results have been saved to {output_file_path}")

# 检查这段代码是否是直接运行的（而不是通过导入的方式运行）
if __name__ == "__main__":
    # 调用主函数
    main()