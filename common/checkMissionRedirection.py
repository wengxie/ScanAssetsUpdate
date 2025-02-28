import re
import json
import os
import chardet
from datetime import datetime

def read_config(config_path):
    """
    从指定路径读取 JSON 配置文件，并返回解析后的内容。
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_encoding(filename):
    """
    检测文件的编码格式。返回检测到的编码。
    """
    with open(filename, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def read_mission_main(filename):
    """
    读取并返回指定文件的内容，先检测文件编码再进行读取。
    """
    # 检测文件编码
    encoding = detect_encoding(filename)
    print(f"Detected encoding: {encoding}")
    # 使用检测到的编码读取文件内容
    with open(filename, 'r', encoding=encoding) as f:
        return f.read()

def extract_blocks(content):
    """
    从文件内容中提取 mission_main 块。返回包含所有块的列表。
    """
    blocks = re.split(r'mission_main\s*{', content)
    return [block.strip() for block in blocks if block.strip()]

def extract_field_value(block, field):
    """
    从块中提取指定字段的值。返回包含匹配值的列表。
    """
    matches = re.findall(rf'{field}="([^"]*)";', block)
    return matches

def check_consistency(blocks, group_id_mapping, mission_mapping):
    """
    检查每个数据块的字段值是否符合映射关系，返回不一致的记录。
    """
    inconsistencies = []
    all_mappings = []

    for block in blocks:
        # 提取字段值
        group_id_values = extract_field_value(block, 'groupId')
        redirection_param_values = extract_field_value(block, 'redirectionParams')
        mission_id_values = extract_field_value(block, 'missionID')
        mission_redirection_values = extract_field_value(block, 'missionRedirection')

        # 如果 missionRedirection 为空则添加为 ["0"]
        if not mission_redirection_values:
            mission_redirection_values = ["0"]

        for mission_id in mission_id_values:
            all_mappings.append({
                "missionID": mission_id,
                "groupId": group_id_values,
                "redirectionParams": redirection_param_values,
                "missionRedirection": mission_redirection_values
            })

            if mission_id in mission_mapping:
                expected_mission = mission_mapping[mission_id]
                if group_id_values and group_id_values[0] not in expected_mission['groupId']:
                    inconsistencies.append((mission_id, 'groupId', group_id_values))
                if redirection_param_values and set(redirection_param_values).difference(expected_mission['redirectionParams']):
                    inconsistencies.append((mission_id, 'redirectionParams', redirection_param_values))
                if set(mission_redirection_values) != set(expected_mission['missionRedirection']):
                    inconsistencies.append((mission_id, 'missionRedirection', mission_redirection_values))

    return inconsistencies, all_mappings

def save_results_to_file(filename, all_mappings, inconsistencies):
    """
    将所有的字段值和一致性检测结果保存到指定的文件中。
    """
    directory = os.path.dirname(filename)
    # 如果目录不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("所有的映射关系:\n\n")
        for mapping in all_mappings:
            mission_id = mapping["missionID"]
            group_ids = mapping["groupId"]
            mission_redirections = mapping["missionRedirection"]
            redirection_params = mapping["redirectionParams"]

            # 生成字典时调整redirectionParams和missionRedirection的位置
            mission_dict = {
                "groupId": group_ids,
                "missionRedirection": mission_redirections if mission_redirections else ["0"],
                "redirectionParams": redirection_params
            }

            f.write(f'"{mission_id}": {json.dumps(mission_dict, ensure_ascii=False)},\n')

        if inconsistencies:
            f.write("\n不一致记录:\n")
            for mission_id, field, values in inconsistencies:
                f.write(f'missionID: {mission_id} 中的 {field} 不符合预期: {values}\n')

def main():
    config_path = '../all_config/redirection_config.json'  # json文件路径
    path_config = '../all_config/path_config.py'  # 路径配置文件路径

    # 读取 JSON 配置文件
    config = read_config(config_path)

    # 读取 path_config.py 文件中的路径变量
    path_config_vars = {}
    with open(path_config, 'r', encoding='utf-8') as f:
        exec(f.read(), path_config_vars)

    # 检查并提取 EXCEL_PATH 变量
    if 'EXCEL_PATH' not in path_config_vars:
        raise ValueError("EXCEL_PATH not found in path_config.py")

    mission_directory = path_config_vars['EXCEL_PATH']

    # 检查是否成功获取到了路径
    if not mission_directory:
        raise ValueError("EXCEL_PATH is None or empty")

    print(f"配置表路径: {mission_directory}")

    # 获取 mission_main 文件的完整路径
    mission_main_file = config['fileNames']['missionMain']
    mission_main_file_path = os.path.join(mission_directory, mission_main_file)

    # 打印确认路径信息
    print(f"mission_main路径: {mission_main_file_path}")

    # 检查文件是否存在
    if not os.path.exists(mission_main_file_path):
        raise FileNotFoundError(f"{mission_main_file_path} does not exist")

    # 读取并解析 mission_main 文件内容
    mission_main_content = read_mission_main(mission_main_file_path)
    blocks = extract_blocks(mission_main_content)

    # 获取 groupId 映射
    group_id_mapping = config.get('groupIdMapping', {})
    mission_mapping = config.get('missionMapping', {})

    # 检查数据块是否一致，并获取所有扫描到的映射关系
    inconsistencies, all_mappings = check_consistency(blocks, group_id_mapping, mission_mapping)

    # 生成按日期编号的输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_directory = 'checkMissionLog'
    output_file = os.path.join(output_directory, f'mapping_results_{timestamp}.txt')

    # 保存所有映射关系和一致性检查结果到文件
    save_results_to_file(output_file, all_mappings, inconsistencies)
    print(f"已将读取到的映射关系保存到文件: {output_file}")

    # 输出不一致的记录
    if inconsistencies:
        print("以下字段不符合预期\n")
        for mission_id, field, values in inconsistencies:
            print(f'missionID: {mission_id} 中的 {field} 不符合预期，应为: {values}')
    else:
        print("所有字段均符合预期")

if __name__ == "__main__":
    main()