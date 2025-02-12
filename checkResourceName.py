import os
import logging

import all_config
from all_config import path_config
from typing import List, Set, Tuple
from checkConfigName import load_filter_configuration, read_file, initialize_all_files_in_bundle_no_extension, \
    extract_field_values, merge_duplicate_filenames, is_valid_value

def find_resource_in_config(resource_file: str, config_directory: str, inbundle_directory: str, filter_config_path: str) -> List[Tuple[str, str, Set[str]]]:
    """
    在配置表中查找特定资源文件的位置，并返回相关的结果
    :param resource_file: 资源文件名
    :param config_directory: 配置文件的目录
    :param inbundle_directory: InBundle 目录路径
    :param filter_config_path: 过滤配置文件路径
    :return: 相关的结果
    """
    # 读取过滤配置
    filter_config = load_filter_configuration(filter_config_path)

    # 获取配置目录中的所有 .txt 文件路径
    files = [os.path.join(config_directory, fname) for fname in os.listdir(config_directory) if fname.lower().endswith('.txt')]

    # 初始化 InBundle 目录中的所有无后缀的文件列表
    all_file_names_in_bundle = initialize_all_files_in_bundle_no_extension(inbundle_directory)

    resource_file_base_name = os.path.splitext(os.path.basename(resource_file))[0]
    matching_configurations = []

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
        exclude_fields = filter_config.get('exclude_fields', {}).get(filename, []) + filter_config.get('exclude_fields', {}).get('global', [])

        # 过滤掉需要排除的字段名，以及包含汉字、仅包含数字、负数和小数的字段值，首位不是字母以及包含空格的字段值
        filtered_field_values = [(field, value.split(':')[-1] if ':' in value else value) for field, value in field_values if field not in exclude_fields and is_valid_value(value)]
        logging.debug(f"Filtered field values: {filtered_field_values}")

        # 查找资源文件路径在配置文件中的位置
        for field, base_filename in filtered_field_values:
            base_filename = os.path.splitext(os.path.basename(base_filename))[0]
            if resource_file_base_name == base_filename:
                logging.info(f"Found resource name: {base_filename} with value: {field} in config file: {file_path}")
                matching_configurations.append((field, base_filename, file_path))

    return merge_duplicate_filenames(matching_configurations)


def main():
    """
    主函数，执行查找功能
    """
    # 设置日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 提示用户输入需要查找的资源文件名
    resource_file = input("在此输入需要查找的资源文件名: ").strip()

    if not resource_file:
        print("No resource file name provided. Exiting.")
        return

    # 配置参数
    config_directory = path_config.EXCEL_PATH  # 配置目录
    inbundle_directory = 'all_config/path_config.INBUNDLE_DIRECTORY'  # InBundle 目录
    filter_config_path = '../all_config/filter_config.json'  # 过滤配置文件路径

    # 找到并打印资源文件在配置表中的位置
    matching_results = find_resource_in_config(resource_file, config_directory, inbundle_directory, filter_config_path)

    if matching_results:
        print(f"'{resource_file}' 在配置表中的位置:")
        for value, filename, config_files in matching_results:
            print(f" - {value}; {filename} (in: {', '.join(config_files)})")
    else:
        print(f"配表中未找到该资源文件 '{resource_file}'.")
        print(f"请核对名称无误或再次尝试。")


if __name__ == "__main__":
    main()