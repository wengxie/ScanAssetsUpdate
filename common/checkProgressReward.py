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
    """解析文件并提取指定条件的数据块"""
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()
    # 找到所有 progressRewards { ... };
    pattern = r'progressRewards\s*\{\s*([^}]+)\s*\};'
    blocks = re.findall(pattern, content)
    result = []
    for block in blocks:
        # 匹配每一项 key="value";
        pairs = re.findall(r'(\w+)\s*=\s*"([^"]+)"', block)
        d = {k: v for k, v in pairs}
        # 满足 tpId 以"971"开头 且 count > 3
        if d.get("tpId", "").startswith("971") and int(d.get("count", "0")) > 1:
            result.append(d)
    return result

def main():
    # 用列表管理需要检查的多个文件名（相对路径）
    mission_paths = [
        r"datapool\ElementData\BaseData\POINT_PROGRESS_REWARD_ENDLESS.data.txt",
        r"datapool\ElementData\BaseData\POINT_PROGRESS_REWARD.data.txt",
    ]
    all_results = {}
    for mission_path in mission_paths:
        file_path = os.path.join(path_config.DOMESTIC_UNITY_ROOT_PATH, mission_path)
        if not os.path.exists(file_path):
            print(f"文件不存在：{file_path}")
            continue
        filtered_blocks = parse_file(file_path)
        all_results[file_path] = filtered_blocks
        print(f"{file_path} 检查结果: {filtered_blocks}")
    # print(all_results)

if __name__ == "__main__":
    main()