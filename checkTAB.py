import logging
import os
import chardet
from all_config import path_config


def detect_encoding(file_path):
    """
    检测文件的编码格式。
    """
    with open(file_path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def find_scripts_with_config(directory, config_table_name):
    """
    查找指定目录下包含指定配置表名称的 C# 脚本文件。

    :param directory: 要搜索的目录路径
    :param config_table_name: 配置表名称
    :return: 符合条件的脚本文件路径列表
    """
    result = []

    # 遍历目录下的所有文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".cs"):  # 只处理 C# 脚本文件
                file_path = os.path.join(root, file)
                try:
                    # 检测文件编码
                    encoding = detect_encoding(file_path)
                    with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                        content = f.read().lower()
                        # 检查是否包含配置表名称，不区分大小写
                        if config_table_name.lower() in content:
                            result.append(file_path)
                except Exception as e:
                    print(f"无法读取文件 {file_path}，错误: {e}")

    return result

def main():
    """
    主函数，执行查找功能
    """
    # 设置日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 用户输入需要查找的资源文件名
    resource_file = input("请输入需要查找的配置表名称: ").strip()

    if not resource_file:
        print("No resource file name provided. Exiting.")
        return
    print("查找中，请等待40s左右...")
    # 查找包含资源文件的C#脚本
    directory_to_search = 'all_config/path_config.ASSETS_DIRECTORY'  # C#脚本所在的目录
    scripts = find_scripts_with_config(directory_to_search, resource_file)

    # 输出C#脚本查找结果
    if scripts:
        print(f"\n以下C#脚本包含了资源文件 '{resource_file}'：")
        for script in scripts:
            print(script)
    else:
        print(f"\n未找到包含资源文件 '{resource_file}' 的C#脚本。")

if __name__ == "__main__":
    main()