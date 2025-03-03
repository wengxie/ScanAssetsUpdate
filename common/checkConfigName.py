import json
import logging
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, List, Tuple, Any

import chardet
from config import path_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('resource_check.log'),
        logging.StreamHandler()
    ]
)

@dataclass(unsafe_hash=True)
class ResourceEntry:
    """资源条目类（增加哈希支持）"""
    field_value: str
    resource_name: str

    def serialize(self) -> str:
        return f"{self.field_value};;{self.resource_name}"

    @classmethod
    def deserialize(cls, data: str):
        try:
            field_value, resource_name = data.split(";;")
            return cls(field_value=field_value, resource_name=resource_name)
        except ValueError as e:
            logging.error(f"反序列化失败: {data} - {str(e)}")
            return None

# 配置路径
BASELINE_FILE = "../result/domesticLogs/checkConfigNameLogs/config_baseline.json"
DIFF_REPORT_DIR = "../result/domesticLogs/checkConfigNameLogs/diff_reports"
EXCLUSION_CONFIG = "../config/filter_config.json"

def find_all_configuration_in_in_bundle(all_files_inbundle: Set[str], directory: str):
    """收集目录下所有资源文件名和路径"""
    for root, _, files in os.walk(directory):
        for filename in files:
            relative_path = os.path.relpath(os.path.join(root, filename), directory).replace(os.sep, '/')
            all_files_inbundle.add(relative_path)

def normalize_data(data: Any) -> Any:
    """数据标准化"""
    if isinstance(data, dict):
        sorted_data = {k: normalize_data(v) for k, v in sorted(data.items(), key=lambda x: x[0])}
        return sorted_data
    elif isinstance(data, (list, set)):
        sorted_list = sorted([normalize_data(item) for item in data], key=lambda x: str(x))
        return sorted_list
    elif isinstance(data, tuple):
        return normalize_data(list(data))
    return data

def generate_diff_report(diffs: Tuple[Dict, Dict, Dict], report_type: str = "resource"):
    """生成差异报告"""
    os.makedirs(DIFF_REPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(DIFF_REPORT_DIR, f"{report_type}_diff_{timestamp}.txt")

    added, removed, modified = diffs

    with open(report_path, 'w', encoding='utf-8') as f:
        if added:
            f.write("=== 新增资源 ===\n")
            for entry_str, files in added.items():
                entry = ResourceEntry.deserialize(entry_str)
                if entry:
                    f.write(f"字段: {entry.field_value}\n资源: {entry.resource_name}\n相关文件: {', '.join(files)}\n\n")

        if removed:
            f.write("=== 删除资源 ===\n")
            for entry_str, files in removed.items():
                entry = ResourceEntry.deserialize(entry_str)
                if entry:
                    f.write(f"字段: {entry.field_value}\n资源: {entry.resource_name}\n相关文件: {', '.join(files)}\n\n")

        if modified:
            f.write("=== 修改资源 ===\n")
            for entry_str, (old_files, new_files) in modified.items():
                entry = ResourceEntry.deserialize(entry_str)
                if entry:
                    f.write(f"字段: {entry.field_value}\n资源: {entry.resource_name}\n")
                    f.write(f"原文件: {', '.join(sorted(old_files))}\n")
                    f.write(f"新文件: {', '.join(sorted(new_files))}\n\n")

    logging.info(f"差异报告已生成：{report_path}")

def compare_with_baseline(current: Dict[str, List[str]], baseline: Dict[str, List[str]]) -> Tuple[Dict, Dict, Dict]:
    """比较当前与基准的数据"""
    added = {entry: current[entry] for entry in current if entry not in baseline}
    removed = {entry: baseline[entry] for entry in baseline if entry not in current}
    modified = {
        entry: (sorted(baseline[entry]), sorted(current[entry]))
        for entry in current
        if entry in baseline and sorted(current[entry]) != sorted(baseline[entry])
    }

    return added, removed, modified

def validate_resource_name(name: str) -> bool:
    """验证资源名称是否符合规范"""
    pattern = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(?:/[A-Za-z][A-Za-z0-9_]*)*$')
    return bool(pattern.fullmatch(name))


def load_exclusion_config(config_path: str) -> Dict:
    """加载排除配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            excluded_files = {os.path.basename(f.lower().strip()) for f in config.get("excluded_files", [])}
            excluded_fields = defaultdict(set)
            for raw_file, fields in config.get("excluded_fields", {}).items():
                file = os.path.basename(raw_file.lower().strip())
                excluded_fields[file].update(field.lower().strip() for field in fields)
            return {"excluded_files": excluded_files, "excluded_fields": excluded_fields}
    except Exception as e:
        logging.error(f"配置加载失败: {e}")
        return {"excluded_files": set(), "excluded_fields": defaultdict(set)}

def is_valid_text_file(filepath: str) -> bool:
    """检查文件是否为有效文本文件"""
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read(512)
            detect = chardet.detect(raw_data)
            return detect['encoding'] is not None
    except Exception as e:
        logging.error(f"文件读取错误: {filepath} - {e}")
        return False

def read_file_contents(filepath: str) -> str:
    """读取文件内容并返回文本"""
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
            return raw_data.decode(encoding)
    except Exception as e:
        logging.error(f"读取文件内容失败: {filepath} - {e}")
        return ""

def parse_config_contents(content: str) -> List[Tuple[str, str]]:
    """解析配置文件内容"""
    pattern = re.compile(r'^\s*(\w+)\s*=\s*\"([^\"]*)\"', re.MULTILINE)
    parsed_entries = pattern.findall(content)

    # 过滤掉显然不是资源路径的内容
    # 假设资源路径不包含 HTML 标签及其他特殊字符，并且不包含占位符(%d, %s等)
    # filtered_entries = [
    #     (field, value) for field, value in parsed_entries
    #     if (re.fullmatch(r'^[A-Za-z0-9_\/]+$', value)
    #         and not re.search(r'%\w|<[^>]+>', value)
    #         and not re.search(r'[\u4e00-\u9fff]', value)
    #     )
    # ]
    filtered_entries = [
        (field, value) for field, value in parsed_entries
        if re.fullmatch(r'^[A-Za-z0-9_\/\.]+$', value)
           and not re.search(r'%\w|<[^>]+>|[\u4e00-\u9fff]', value)
    ]
    return filtered_entries

def is_path_in_bundle(path: str, bundle_resources: Set[str]) -> bool:
    """逐级检查路径是否存在于资源包中"""
    parts = path.split('/')
    for i in range(1, len(parts) + 1):
        sub_path = '/'.join(parts[:i])
        if sub_path not in bundle_resources:
            return False
    return True

def collect_missing_resources(config_dir: str, bundle_resources: Set[str], exclusions: Dict) -> Dict[ResourceEntry, Set[str]]:
    """收集缺失资源"""
    findings = defaultdict(set)
    excluded_files = exclusions["excluded_files"]
    excluded_fields = exclusions["excluded_fields"]

    for filename in os.listdir(config_dir):
        file_base = os.path.basename(filename).lower()

        # 只处理 .txt 文件
        if not filename.lower().endswith('.txt'):
            continue

        # 文件级排除检查
        if file_base in excluded_files:
            continue

        file_path = os.path.join(config_dir, filename)

        # 检查文件是否为有效文本文件
        if not is_valid_text_file(file_path):
            logging.warning(f"非文本文件或编码检测失败: {filename}")
            continue

        # 读取文件内容
        content = read_file_contents(file_path)
        if not content:
            logging.warning(f"文件内容读取失败: {filename}")
            continue

        # 获取该文件对应的字段排除规则
        fields_to_exclude = excluded_fields.get(file_base, set())

        # 解析和处理每个配置项
        for field, value in parse_config_contents(content):
            if field.lower() in fields_to_exclude:
                continue

            resource_path = value.strip()
            if '/' in resource_path:
                # 资源路径包含子路径，进行路径逐级检查
                if not is_path_in_bundle(resource_path, bundle_resources):
                    entry = ResourceEntry(field_value=field, resource_name=resource_path)
                    findings[entry].add(filename)
                    # logging.debug(f"缺失资源: {resource_path} 于字段 {field} 文件 {filename}")
            else:
                # 资源路径不包含子路径，进行简单的资源名验证和存在性检查
                resource_name = os.path.splitext(resource_path)[0]
                if not validate_resource_name(resource_name):
                    # logging.warning(f"无效资源名: {resource_path} 来自 {filename}.{field}")
                    continue

                if resource_name not in bundle_resources:
                    entry = ResourceEntry(field_value=field, resource_name=resource_name)
                    findings[entry].add(filename)
                    # logging.debug(f"缺失资源: {resource_name} 于字段 {field} 文件 {filename}")

    return findings

def main():
    """主执行流程"""
    print("扫描资源中，请稍后...")

    # 获取包内所有配置资源
    bundle_resources = set()
    find_all_configuration_in_in_bundle(bundle_resources, path_config.INBUNDLE_DIRECTORY)

    # 加载排除配置
    exclusions = load_exclusion_config(EXCLUSION_CONFIG)

    # 收集缺失资源
    current_findings = collect_missing_resources(path_config.EXCEL_PATH, bundle_resources, exclusions)

    # 序列化结果并对文件名列表排序
    current_serialized = {entry.serialize(): sorted(list(files)) for entry, files in current_findings.items()}

    # 处理基准文件
    if not os.path.exists(BASELINE_FILE):
        os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
        with open(BASELINE_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_serialized, f, indent=2, ensure_ascii=False)
        logging.info(f"基准文件已生成")
        return

    # 加载基准文件并进行对比
    with open(BASELINE_FILE, 'r', encoding='utf-8') as f:
        baseline_findings = json.load(f)

    # 比较当前资源与基准资源
    diffs = compare_with_baseline(current_serialized, baseline_findings)

    # 如果有差异，则生成差异报告并更新基准文件
    if any(diffs):
        generate_diff_report(diffs)
        # with open(BASELINE_FILE, 'w', encoding='utf-8') as f:
        #     json.dump(current_serialized, f, indent=2, ensure_ascii=False)
        # logging.info("基准文件已更新")
    else:
        logging.info("资源状态与基准一致，无差异")

if __name__ == "__main__":
    main()
