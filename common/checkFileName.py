# -*- coding: utf-8 -*-
import datetime
import os
import re
from collections import defaultdict
from checkConfigurationTableUpdate import find_all_Configuration_in_InBundle
from config import path_config


#路径配置
output_dir = "../result/domesticLogs/checkFileNameLogs"
inbundle_path = "client/MainProject/Assets/InBundle"

# --------------------------
# 文件后缀校验模块
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
            normalized_path = os.path.normpath(file_path).lower()
            error_dict[error_type].append((file_path, normalized_path))

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
                    files_dict[file.lower()].append((full_path, normalized))

    duplicates = {}
    for name, paths in files_dict.items():
        if len(paths) > 1:
            duplicates[name] = sorted(paths, key=lambda x: x[1])
    return duplicates

# --------------------------
# 报告生成模块
# --------------------------
def parse_benchmark(content):
    """解析基准文件内容（增强路径标准化）"""
    benchmark = {
        'abnormal': defaultdict(set),
        'duplicates': defaultdict(set)
    }

    current_section = None
    current_group = None

    for line in content.split('\n'):
        line = line.strip()
        if '===' in line:
            if '非法文件后缀检查' in line:
                current_section = 'abnormal'
            elif '重名Prefab文件检查' in line:
                current_section = 'duplicates'
            else:
                current_section = None
            continue

        if current_section == 'abnormal' and line.startswith('→'):
            path = os.path.normpath(line[1:].strip()).lower()
            benchmark['abnormal']['非法文件后缀检查'].add(path)

        elif current_section == 'duplicates':
            if line.startswith(('1.', '2.', '3.')):  # 检测同名文件组
                current_group = line.split('同名文件: ')[1].strip().lower()
            elif line.startswith('▸'):
                path = os.path.normpath(line[1:].strip()).lower()
                benchmark['duplicates'][current_group].add(path)

    return benchmark


def generate_full_report(abnormal, duplicates):
    """生成完整报告用于更新基准"""
    content = []
    if abnormal:
        content.append("=== 非法文件后缀检查 ===\n")
        for err_type, files in abnormal.items():
            sorted_files = sorted(files, key=lambda x: x[1])
            content.append(f"⛔ 违规类型：{err_type}（{len(sorted_files)}个）\n")
            content.extend(f"   → {f[0].split('InBundle', 1)[-1]}\n" for f in sorted_files)
            content.append("\n")

    if duplicates:
        content.append("\n=== 重名Prefab文件检查 ===\n")
        for idx, (name, paths) in enumerate(duplicates.items(), 1):
            content.append(f"{idx}. 同名文件: {name}\n")
            sorted_paths = sorted(paths, key=lambda x: x[1])
            content.extend(f"   ▸ {p[0].split('InBundle', 1)[-1]}\n" for p in sorted_paths)
            content.append("\n")

    return "".join(content)


def generate_diff_report(current_abnormal, current_dups, benchmark):
    """生成差异报告（包括新增及减少的文件和文件组，排除顺序干扰）"""
    content = []
    new_abnormal = defaultdict(list)
    new_duplicates = defaultdict(list)
    removed_abnormal = defaultdict(list)
    removed_duplicates = defaultdict(list)

    bench_abnormal_paths = set(item for sublist in benchmark['abnormal'].values() for item in sublist)
    current_abnormal_paths = set(f[1] for files in current_abnormal.values() for f in files)  # 提取当前所有路径

    # 检测新增非法后缀文件
    for err_type, files in current_abnormal.items():
        filtered = [f for f in files if f[1] not in bench_abnormal_paths]
        if filtered:
            new_abnormal[err_type].extend(filtered)

    # 检测减少非法后缀文件
    for path in bench_abnormal_paths - current_abnormal_paths:
        for err_type, files in benchmark['abnormal'].items():
            if path in files:
                removed_abnormal[err_type].append(path)
                break

    # 检测新增重名文件组
    for name, paths in current_dups.items():
        current_paths_set = set(p[1] for p in paths)  # 集合化处理路径
        bench_paths_set = benchmark['duplicates'].get(name.lower(), set())

        new_paths = current_paths_set - bench_paths_set
        if new_paths:
            new_duplicates[name].extend([p for p in paths if p[1] in new_paths])

    # 检测减少重名文件组
    bench_duplicates = set(benchmark['duplicates'])
    current_duplicates = set(current_dups)

    for name in bench_duplicates - current_duplicates:
        removed_duplicates[name.lower()].extend(list(benchmark['duplicates'][name]))

    if new_abnormal:
        content.append("=== 新增非法后缀文件 ===\n")
        for err_type, files in new_abnormal.items():
            content.append(f"⛔ 违规类型：{err_type}（{len(files)}个）\n")
            content.extend(f"   → {f[0].split('InBundle', 1)[-1]}\n" for f in files)
            content.append("\n")

    if removed_abnormal:
        content.append("=== 减少非法后缀文件 ===\n")
        for err_type, files in removed_abnormal.items():
            content.append(f"⛔ 违规类型：{err_type}（{len(files)}个）\n")
            content.extend(f"   → {f.split('InBundle', 1)[-1]}\n" for f in files)
            content.append("\n")

    if new_duplicates:
        content.append("\n=== 新增重名文件 ===\n")
        for idx, (name, paths) in enumerate(new_duplicates.items(), 1):
            content.append(f"{idx}. 同名文件: {name}\n")
            sorted_paths = sorted(paths, key=lambda x: x[1])
            content.extend(f"   ▸ {p[0].split('InBundle', 1)[-1]}\n" for p in sorted_paths)
            content.append("\n")

    if removed_duplicates:
        if content:
            content.append("\n")
        content.append("=== 减少重名文件组 ===\n")
        for idx, (name, paths) in enumerate(removed_duplicates.items(), 1):
            content.append(f"{idx}. 同名文件组: {name}\n")
            sorted_paths = sorted(paths, key=lambda x: x[1])
            content.extend(f"   ▸ {p.split('InBundle', 1)[-1]}\n" for p in sorted_paths)
            content.append("\n")

    report_content = "".join(content).strip()
    return report_content or "✅ 无新增或减少异常文件", new_abnormal, new_duplicates, removed_abnormal, removed_duplicates

def select_benchmark():
    """选择国内/海外基准文件"""
    input_string = input("请选择国内或海外，国内为1，海外为2：").strip()
    if input_string == "1":
        return (os.path.join(output_dir, "checkFileName.txt"), path_config.DOMESTIC_UNITY_ROOT_PATH)
    elif input_string == "2":
        return (os.path.join(output_dir, "checkFileName_global.txt"), path_config.GLOBAL_UNITY_ROOT_PATH)
    else:
        print("输入有误，请输入对应数字！")
        return select_benchmark()

# --------------------------
# 主程序逻辑
# --------------------------
def main():
    benchmark_path, UNITY_ROOT_PATH = select_benchmark()
    os.makedirs(output_dir, exist_ok=True)

    # print(f"基准文件存储路径：{os.path.abspath(benchmark_path)}")  # 调试输出

    # 获取当前检测结果
    current_abnormal = get_abnormal_extensions(os.path.join(UNITY_ROOT_PATH, inbundle_path))
    current_dups = find_duplicate_prefab_files(
        UNITY_ROOT_PATH,
        ['client/MainProject/Assets/ArtImport/Fish', 'client/MainProject/Assets/InBundle/Fish']
    )

    # 读取或初始化基准文件
    if os.path.exists(benchmark_path):
        with open(benchmark_path, 'r', encoding='utf-8') as f:
            benchmark = parse_benchmark(f.read())
    else:
        benchmark = {'abnormal': defaultdict(set), 'duplicates': defaultdict(set)}
        # 创建新的基准文件并写入当前检测结果
        try:
            with open(benchmark_path, 'w', encoding='utf-8') as f:
                full_report = generate_full_report(current_abnormal, current_dups)
                f.write(full_report)
                # print(f"基准文件创建并初始化：{os.path.getsize(benchmark_path)} 字节")
        except PermissionError as e:
            print(f"权限错误：{str(e)}")
        except Exception as e:
            print(f"未知错误：{str(e)}")

    # 生成差异报告
    diff_content, new_abnormal, new_duplicates, removed_abnormal, removed_duplicates = generate_diff_report(
        current_abnormal, current_dups, benchmark
    )

    # 输出逻辑（严格匹配）
    if diff_content != "✅ 无新增或减少异常文件":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(output_dir, f"diff_{timestamp}.txt")
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        print(f">> 发现异常变化，报告已生成：{result_path}")

        # 控制台摘要
        new_abnormal_count = sum(len(v) for v in new_abnormal.values())
        removed_abnormal_count = sum(len(v) for v in removed_abnormal.values())
        print(f"\n[检测摘要]")
        print(f"新增异常文件: {new_abnormal_count}个")
        print(f"减少异常文件: {removed_abnormal_count}个")
        print(f"新增重名组数: {len(new_duplicates)}组")
        print(f"减少重名组数: {len(removed_duplicates)}组")
    else:
        print(">> 状态正常：无新增或减少异常文件")

    # 更新基准文件（可选）
    # try:
    #     with open(benchmark_path, 'w', encoding='utf-8') as f:
    #         full_report = generate_full_report(current_abnormal, current_dups)
    #         f.write(full_report)
    #         print(f"基准文件已更新：{os.path.getsize(benchmark_path)} 字节")
    # except PermissionError as e:
    #     print(f"权限错误：{str(e)}")
    # except Exception as e:
    #     print(f"未知错误：{str(e)}")


if __name__ == "__main__":
    main()