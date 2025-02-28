# -*- coding: utf-8 -*-
import os
import re
import datetime
from all_config import path_config
from collections import defaultdict
from ScanAssetsUpdate.checkConfigurationTableUpdate import find_all_Configuration_in_InBundle


# --------------------------
# 核心校验模块
# --------------------------
def validate_extension(ext):
    """严格校验后缀规则（只允许纯小写字母）"""
    errors = []
    if ext:
        ext_part = ext[1:]  # 去除扩展名的点
        if not ext_part:
            errors.append("空后缀")
        elif not re.fullmatch(r'^[a-z]+$', ext_part):
            errors.append("非纯小写字母")
    return errors


def get_abnormal_extensions(directory):
    """获取非法后缀文件"""
    all_files = []
    find_all_Configuration_in_InBundle(all_files, directory)

    error_dict = defaultdict(list)
    for file_path in all_files:
        ext = os.path.splitext(file_path)[1]
        if errors := validate_extension(ext):
            error_type = "+".join(errors)
            error_dict[error_type].append(file_path)

    for key in error_dict:
        error_dict[key] = sorted(error_dict[key], key=lambda x: x.lower())
    return error_dict


# --------------------------
# 重名文件检测模块
# --------------------------
def find_duplicate_prefab_files(directory, subdirectories=None):
    """查找重名prefab文件"""
    files_dict = defaultdict(list)
    subdirectories = subdirectories or ['']

    for subdir in subdirectories:
        current_dir = os.path.join(directory, subdir)
        for root, _, files in os.walk(current_dir):
            for file in files:
                if file.lower().endswith('.prefab'):
                    full_path = os.path.join(root, file)
                    normalized = os.path.normpath(full_path).lower()
                    files_dict[file.lower()].append(normalized)

    duplicates = {}
    for name, paths in files_dict.items():
        if len(paths) > 1:
            duplicates[name] = sorted(list(set(paths)))
    return duplicates


# --------------------------
# 报告生成模块
# --------------------------
def parse_benchmark(content):
    """解析基准文件内容（增强路径标准化）"""
    benchmark = {
        'abnormal': set(),
        'duplicates': defaultdict(set)
    }

    current_section = None
    current_group = None

    for line in content.split('\n'):
        line = line.strip()  # 新增：去除首尾空白
        if '===' in line:
            if '非法文件后缀检查' in line:
                current_section = 'abnormal'
            elif '重名Prefab文件检查' in line:
                current_section = 'duplicates'
            else:
                current_section = None
            continue

        if current_section == 'abnormal' and line.startswith('→'):
            path = os.path.normpath(line[1:].strip()).lower()  # 统一处理箭头符号
            benchmark['abnormal'].add(path)

        elif current_section == 'duplicates':
            if line.startswith(('1.', '2.', '3.')):
                current_group = line.split('同名文件: ')[1].strip().lower()
            elif line.startswith('▸'):
                path = os.path.normpath(line[1:].strip()).lower()  # 统一处理符号
                benchmark['duplicates'][current_group].add(path)

    return benchmark


def generate_full_report(abnormal, duplicates):
    """生成完整报告用于更新基准"""
    content = []
    if abnormal:
        content.append("=== 非法文件后缀检查 ===\n")
        for err_type, files in abnormal.items():
            # 统一使用标准化路径
            sorted_files = sorted([os.path.normpath(f) for f in files], key=lambda x: x.lower())
            content.append(f"⛔ 违规类型：{err_type}（{len(sorted_files)}个）\n")
            content.extend(f"   → {f}\n" for f in sorted_files)
            content.append("\n")

    if duplicates:
        content.append("\n=== 重名Prefab文件检查 ===\n")
        for idx, (name, paths) in enumerate(duplicates.items(), 1):
            content.append(f"{idx}. 同名文件: {name}\n")
            sorted_paths = sorted([os.path.normpath(p) for p in paths], key=lambda x: x.lower())
            content.extend(f"   ▸ {p}\n" for p in sorted_paths)
            content.append("\n")

    return "".join(content)


def generate_diff_report(current_abnormal, current_dups, benchmark):
    """生成差异报告（增强路径对比）"""
    content = []
    new_abnormal = defaultdict(list)
    new_duplicates = defaultdict(list)

    # 异常文件对比（双重标准化）
    bench_abnormal = {os.path.normpath(p).lower() for p in benchmark['abnormal']}
    for err_type, files in current_abnormal.items():
        filtered = [
            f for f in files
            if os.path.normpath(f).lower() not in bench_abnormal
        ]
        if filtered:
            new_abnormal[err_type] = filtered

    # 重名文件对比（精确匹配）
    for name, paths in current_dups.items():
        bench_paths = benchmark['duplicates'].get(name.lower(), set())
        current_set = {os.path.normpath(p).lower() for p in paths}

        if name.lower() not in benchmark['duplicates']:
            new_duplicates[name] = paths
        else:
            new_paths = [p for p in paths
                         if os.path.normpath(p).lower() not in bench_paths]
            if new_paths:
                new_duplicates[name] = new_paths

    # 生成报告内容
    if new_abnormal:
        content.append("=== 新增非法后缀文件 ===\n")
        for err_type, files in new_abnormal.items():
            content.append(f"⛔ 违规类型：{err_type}（{len(files)}个）\n")
            content.extend(f"   → {os.path.normpath(f)}\n" for f in files)
            content.append("\n")

    if new_duplicates:
        if content:  # 添加分隔换行
            content.append("\n")
        content.append("=== 新增重名文件 ===\n")
        for idx, (name, paths) in enumerate(new_duplicates.items(), 1):
            content.append(f"{idx}. 同名文件: {name}\n")
            content.extend(f"   ▸ {os.path.normpath(p)}\n" for p in paths)
            content.append("\n")

    report_content = "".join(content).strip()
    return report_content or "✅ 无新增异常文件", new_abnormal, new_duplicates


# --------------------------
# 主程序逻辑
# --------------------------
def main():
    output_dir = "checkFileNameLog"
    benchmark_path = os.path.join(output_dir, "checkFileName.txt")
    os.makedirs(output_dir, exist_ok=True)

    print(f"基准文件存储路径：{os.path.abspath(benchmark_path)}")  # 调试输出

    # 获取当前检测结果
    current_abnormal = get_abnormal_extensions(path_config.INBUNDLE_DIRECTORY)
    current_dups = find_duplicate_prefab_files(
        path_config.ASSETS_DIRECTORY,
        ['ArtImport/Fish', 'InBundle/Fish']
    )

    # 读取基准文件
    if os.path.exists(benchmark_path):
        with open(benchmark_path, 'r', encoding='utf-8') as f:
            benchmark = parse_benchmark(f.read())
    else:
        benchmark = {'abnormal': set(), 'duplicates': defaultdict(set)}

    # 生成差异报告
    diff_content, new_abnormal, new_duplicates = generate_diff_report(
        current_abnormal, current_dups, benchmark
    )

    # 输出逻辑（严格匹配）
    if diff_content != "✅ 无新增异常文件":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(output_dir, f"diff_{timestamp}.txt")
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        print(f">> 发现新增异常，报告已生成：{result_path}")

        # 控制台摘要
        new_abnormal_count = sum(len(v) for v in new_abnormal.values())
        print(f"\n[检测摘要]")
        print(f"新增异常文件: {new_abnormal_count}个")
        print(f"新增重名组数: {len(new_duplicates)}组")
    else:
        print(">> 状态正常：无新增异常文件")

    # 必须更新基准文件（关键修复）
    # try:
    #     with open(benchmark_path, 'w', encoding='utf-8') as f:
    #         full_report = generate_full_report(current_abnormal, current_dups)
    #         f.write(full_report)
    #         print(f"基准文件已更新：{os.path.getsize(benchmark_path)} 字节")  # 新增验证
    # except PermissionError as e:
    #     print(f"权限错误：{str(e)}")
    # except Exception as e:
    #     print(f"未知错误：{str(e)}")


if __name__ == "__main__":
    main()
