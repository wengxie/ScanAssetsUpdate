import os.path
import re
import chardet
from config import path_config

def detect_encoding(file_path):
    """检测文件的编码格式"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def parse_file(file_path):
    """解析mission_condition文件并提取ids"""
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()

    # 使用正则表达式提取所有的mission ID和missionCondition ID
    mission_id_pattern = re.compile(r'missionID="(\d+)";')
    mission_condition_id_pattern = re.compile(r'missionConditionID="(\d+)";')

    mission_ids = mission_id_pattern.findall(content)
    mission_condition_ids = mission_condition_id_pattern.findall(content)

    return mission_ids, mission_condition_ids

def check_uniqueness(ids_list):
    """检查id列表中的唯一性"""
    unique_ids = set(ids_list)
    if len(unique_ids) == len(ids_list):
        return True, []
    else:
        duplicates = [item for item in ids_list if ids_list.count(item) > 1]
        return False, duplicates

def main():
    mission_path = "datapool\ElementData\BaseData\MISSION_MAIN.data.txt"
    file_path = os.path.join(path_config.DOMESTIC_UNITY_ROOT_PATH, mission_path)

    # 解析文件并提取ID
    mission_ids, mission_condition_ids = parse_file(file_path)

    # 检查唯一性
    is_mission_ids_unique, mission_id_duplicates = check_uniqueness(mission_ids)
    is_mission_condition_ids_unique, mission_condition_id_duplicates = check_uniqueness(mission_condition_ids)

    # 输出检查结果
    if is_mission_ids_unique:
        print("missionIDs 是唯一的。")
    else:
        print("missionIDs 存在重复值：", mission_id_duplicates)

    if is_mission_condition_ids_unique:
        print("missionConditionIDs 是唯一的。")
    else:
        print("missionConditionIDs 存在重复值：", mission_condition_id_duplicates)

if __name__ == "__main__":
    main()