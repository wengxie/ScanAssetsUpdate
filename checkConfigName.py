import os
import re
import json
import logging
import chardet
from all_config import path_config
from typing import List, Set, Dict, Tuple
from collections import defaultdict

from ScanAssetsUpdate.checkConfigurationTableUpdate import find_all_Configuration_in_InBundle


def read_file(file_path: str) -> str:
    """
    读取文件内容并返回作为字符串。
    :param file_path: 文件的路径
    :return: 文件内容的字符串, 或者是 None (读取失败)
    """
    try:
        # 检测文件编码
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # 使用检测到的编码读取文件内容
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
        return content
    except IOError as e:
        logging.error(f"Error: Unable to read file {file_path}. {e}")
        return None
    except UnicodeDecodeError as e:
        logging.error(f"Error: Cannot decode file {file_path}. {e}")
        return None


def load_filter_configuration(config_path: str) -> Dict:
    """
    读取过滤配置文件并返回过滤规则字典
    :param config_path: 过滤配置文件路径
    :return: 过滤规则字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except IOError as e:
        logging.error(f"Error: Unable to read filter configuration file {config_path}. {e}")
        return {}


def extract_field_values(content: str) -> List:
    """
    从文件内容中提取所有字段及字段值
    :param content: 文件内容字符串
    :return: 包含字段名和值的元组列表
    """
    field_pattern = re.compile(r'(\w+)\s*=\s*"([^"]+)";')
    matches = field_pattern.finditer(content)
    field_values = [(match.group(1).strip(), match.group(2).strip()) for match in matches]
    return field_values


def file_exists(file_name: str, all_files: Set[str]) -> bool:
    """
    检查文件名是否存在于 all_files 集合中
    :param file_name: 文件名
    :param all_files: 文件路径集合
    :return: 文件名是否存在的布尔值
    """
    return file_name in all_files


def initialize_all_files_in_bundle_no_extension(inbundle_directory: str) -> Set[str]:
    """
    初始化 InBundle 目录中的所有无后缀的文件列表
    :param inbundle_directory: InBundle 目录路径
    :return: 无后缀的文件名集合
    """
    all_files_in_bundle = []
    find_all_Configuration_in_InBundle(all_files_in_bundle, inbundle_directory)
    all_file_names = {os.path.splitext(os.path.basename(file))[0] for file in all_files_in_bundle}
    return all_file_names


def is_valid_value(value: str) -> bool:
    """
    检查字段值是否合法，过滤掉包含汉字、仅包含数字、负数、小数、首位不是字母以及包含空格的字段值
    :param value: 字段值
    :return: 如果字段值合法则返回 True，否则返回 False
    """
    # 检查是否包含汉字
    if re.search(r'[\u4e00-\u9fa5]', value):
        return False
    # 检查是否为纯数字、负数或小数
    if re.match(r'^-?\d+(\.\d+)?$', value):
        return False
    # 检查首位是否是字母
    if not value[0].isalpha():
        return False
    # 检查是否包含空格
    if ' ' in value:
        return False
    return True


def read_check_config_name_file(file_path: str) -> List[Tuple[str, str, str]]:
    """
    读取 checkConfigName.txt 文件并解析内容，返回元组列表 (字段值, 文件名, 配置文件路径)
    :param file_path: checkConfigName.txt 文件路径
    :return: 包含字段值、文件名和配置文件路径的元组列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        result = []
        for line in lines:
            match = re.match(r"\s*-\s+([^;]+);\s+(\S+)\s+\(in:\s+(.+)\)", line)
            if match:
                result.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))
        return result
    except IOError as e:
        logging.error(f"Error: Unable to read file {file_path}. {e}")
        return []


def merge_duplicate_filenames(entries: List[Tuple[str, str, str]]) -> List[Tuple[str, str, Set[str]]]:
    """
    合并重复的文件名，并保留所有关联的配置文件路径
    :param entries: 包含字段值、文件名和配置文件路径的元组列表
    :return: 包含字段值、文件名和配置文件路径集合的元组列表
    """
    merged_dict = defaultdict(lambda: defaultdict(set))
    for value, filename, config_file in entries:
        merged_dict[value][filename].add(config_file)

    merged_entries = []
    for value, files in merged_dict.items():
        for filename, config_files in files.items():
            merged_entries.append((value, filename, config_files))

    return merged_entries

def scan_directory_for_txt_files(directory_path: str) -> List[str]:
    """
    扫描指定目录下的所有txt文件
    :param directory_path: 目录路径
    :return: txt文件路径的列表
    """
    txt_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    return txt_files

def main():
    """
    主函数，扫描配置目录中的所有配置文件，解析内容并检查资源路径是否存在
    合并 checkConfigName.txt 文件中的重复文件名，并输出最终结果到同一文件
    """
    # 设置日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 配置目录路径
    config_directory = path_config.EXCEL_PATH
    inbundle_directory = path_config.INBUNDLE_DIRECTORY
    output_file_path = 'checkFileNameLog/checkConfigName.txt'  # 输出文件路径
    filter_config_path = '../all_config/filter_config.json'  # 过滤配置文件路径

    # 读取过滤配置
    filter_config = load_filter_configuration(filter_config_path)

    # 检查配置目录是否存在
    if not os.path.isdir(config_directory):
        logging.error(f"The directory does not exist: {config_directory}")
        return

    # 获取配置目录中的所有 .txt 文件路径
    files = [os.path.join(config_directory, fname) for fname in os.listdir(config_directory) if
             fname.lower().endswith('.txt')]

    # 初始化 InBundle 目录中的所有无后缀的文件列表
    all_file_names_in_bundle = initialize_all_files_in_bundle_no_extension(inbundle_directory)

    missing_files_with_config = []  # 存储缺失的字段值、文件名以及对应的配置文件名

    # 遍历每个配置文件
    for file_path in files:
        # 检查该文件是否在需要排除的文件列表中
        exclude_files = filter_config.get('exclude_files', [])
        if os.path.basename(file_path) in exclude_files:
            logging.info(f"Skipping excluded file: {file_path}")
            continue

        logging.info(f"Processing file: {file_path}")

        # 读取文件内容
        content = read_file(file_path)
        if content is None:
            continue

        # 提取所有字段名和字段值
        field_values = extract_field_values(content)
        logging.debug(f"Field values extracted: {field_values}")

        # 获取当前文件需要排除的字段
        filename = os.path.basename(file_path)
        exclude_fields = filter_config.get('exclude_fields', {}).get(filename, []) + filter_config.get('exclude_fields',
                                                                                                       {}).get('global',
                                                                                                               [])

        # 过滤掉需要排除的字段名，以及包含汉字、仅包含数字、负数和小数的字段值，首位不是字母以及包含空格的字段值
        filtered_field_values = [(field, value.split(':')[-1] if ':' in value else value) for field, value in field_values if
                                 field not in exclude_fields and is_valid_value(value)]
        logging.debug(f"Filtered field values: {filtered_field_values}")

        # 检查每个字段值的存在性，只查看文件名
        for field, base_filename in filtered_field_values:
            # 提取路径中的最后一部分作为文件名
            base_filename = os.path.splitext(os.path.basename(base_filename))[0]
            if not file_exists(base_filename, all_file_names_in_bundle):
                logging.warning(
                    f"Missing resource name: {base_filename} with value: {field} in config file: {file_path}")
                missing_files_with_config.append((field, base_filename, file_path))

    # 如果checkConfigName.txt文件存在，读取并合并其内容
    if os.path.isfile(output_file_path):
        previous_entries = read_check_config_name_file(output_file_path)
        missing_files_with_config.extend(previous_entries)

    # 合并重复字段值和文件名
    merged_missing_files = merge_duplicate_filenames(missing_files_with_config)

    # 输出检查结果到文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        if not merged_missing_files:
            message = "All resource files are present."
            logging.info(message)
            f.write(message + '\n')
        else:
            message = f"Missing resource files: {len(merged_missing_files)}"
            logging.info(message)
            f.write(message + '\n')
            for value, filename, config_files in merged_missing_files:
                logging.info(f" - {value}; {filename} (in: {', '.join(config_files)})")
                f.write(f" - {value}; {filename} (in: {', '.join(config_files)})\n")

    print(f"Results have been saved to {output_file_path}")


if __name__ == "__main__":
    main()