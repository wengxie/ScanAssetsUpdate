import logging
import os
from typing import List, Tuple

import chardet
from config import path_config


def read_file_with_chardet(file_path: str) -> str:
    """
    读取文件内容，通过自动检测编码方式
    :param file_path: 文件路径
    :return: 文件内容字符串或 None 如果读取失败
    """
    try:
        # 先读取文件的二进制内容
        with open(file_path, 'rb') as file:
            raw_data = file.read()

        # 检测编码格式
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        # logging.info(f"Detected encoding {encoding} for file {file_path}")

        # 使用检测到的编码格式读取文件内容
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        logging.error(f"Failed to read file {file_path} with detected encoding: {e}")
        return None


def search_in_config(content: str, search_string: str) -> List[Tuple[str, str]]:
    """
    在文件内容中搜索字符串，并返回匹配部分的字段名和行
    :param content: 文件内容
    :param search_string: 搜索的字符串
    :return: 字段名和匹配行的列表
    """
    results = []
    lines = content.splitlines()
    section = ""

    for line in lines:
        line = line.strip()
        if line.startswith('{'):
            section = line
        elif line.startswith('}'):
            section = ""
        elif search_string in line:
            results.append((section, line))

    return results


def search_in_directory(directory: str, search_string: str):
    """
    在指定目录中搜索包含指定字符串的所有文件
    :param directory: 目录路径
    :param search_string: 搜索的字符串
    :return: 包含匹配结果的列表
    """
    result = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            content = read_file_with_chardet(file_path)
            if content is None:
                continue

            hits = search_in_config(content, search_string)
            if hits:
                result.append({
                    'filename': filename,
                    'hits': hits
                })

    return result

def select_benchmark():
    """选择国内/海外基准文件"""
    input_string = input("请选择国内或海外，国内为1，海外为2：").strip()
    if input_string == "1":
        return (path_config.DOMESTIC_UNITY_ROOT_PATH)
    elif input_string == "2":
        return (path_config.GLOBAL_UNITY_ROOT_PATH)
    else:
        print("输入有误，请输入对应数字！")
        return select_benchmark()

def main():
    """
    主函数，执行查找功能
    """
    # 设置日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 提示用户输入需要查找的资源文件名
    excel_path = "datapool\ElementData\BaseData"
    UNITY_ROOT_PATH = select_benchmark()
    directory = os.path.join(UNITY_ROOT_PATH, excel_path)
    search_string = input("请输入要搜索的字符串: ").strip()

    if not directory or not search_string:
        print("输入不有效，请再次尝试")
        return

    # 找到并打印资源文件在配置表中的位置
    matching_results = search_in_directory(directory, search_string)

    if matching_results:
        print(f"包含字符串 '{search_string}' 的文件及所在字段:\n")
        for result in matching_results:
            print(f"配置表: {result['filename']}")
            for section, line in result['hits']:
                print(f"所在字段: {line}")
            print("\n")
    else:
        print(f"在指定目录中未找到包含字符串 '{search_string}' 的文件.")


if __name__ == "__main__":
    main()