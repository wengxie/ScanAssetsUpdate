import os
import subprocess
import chardet
from datetime import datetime
from pathlib import Path
from config import path_config

def get_svn_log(repository_path, start_date=None, end_date=None):
    """
    获取指定仓库路径的SVN日志，支持可选的日期范围筛选。
    参数:
    - repository_path: SVN仓库的本地路径或URL
    - start_date: 筛选日志的起始日期 (可选，格式 'YYYY-MM-DD')
    - end_date: 筛选日志的结束日期 (可选，格式 'YYYY-MM-DD')
    返回:
    - log: SVN日志输出的字符串
    """
    command = ['svn', 'log', '--verbose', repository_path]
    if start_date and end_date:
        # 转换日期格式为SVN所需的'{YYYY-MM-DD}'或'{YYYY-MM-DDTHH:MM:SS}'
        start_date_str = f"{{{start_date}}}"
        end_date_str = f"{{{end_date}}}"
        command.extend(['-r', f"{start_date_str}:{end_date_str}"])

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    detected_encoding = chardet.detect(stdout)['encoding']

    try:
        log_output = stdout.decode(detected_encoding)
    except (UnicodeDecodeError, TypeError) as e:
        raise Exception(f"无法使用编码 {detected_encoding} 解码标准输出: {e}")

    error_output = stderr.decode('utf-8', errors='ignore')

    if process.returncode != 0:
        raise Exception(f"svn log 命令执行失败，错误信息: {error_output}")

    return log_output

def parse_and_save_log(log, filename, file_endings):
    """
    解析SVN日志并保存解析后的输出到指定文件，按文件类型进行筛选。
    参数:
    - log: SVN日志数据字符串
    - filename: 保存解析日志的文件名
    - file_endings: 需包含的文件后缀列表
    """
    with open(filename, 'w', encoding='utf-8') as log_file:
        entries = log.split('------------------------------------------------------------------------')
        for entry in entries:
            if entry.strip():
                lines = entry.strip().split('\n')
                revision_info = lines[0]
                changes = [line for line in lines[1:] if line.startswith('   ')]
                msg = "\n".join(line for line in lines[1:] if not line.startswith('   '))

                filtered_changes = [change for change in changes if
                                    any(change.endswith(ending) for ending in file_endings)]

                if filtered_changes:
                    log_file.write('--------------------------------------------------\n')
                    log_file.write(f"🖋提交记录：{revision_info}\n")
                    log_file.write(f"提交信息:\n{msg.strip()}\n")
                    log_file.write("📁 改动文件:\n")
                    for change in filtered_changes:
                        log_file.write(f"{change.strip()}\n")
                    log_file.write('\n')

def main():
    repository_path = path_config.DOMESTIC_UNITY_ROOT_PATH

    log_path = Path("../result/domesticLogs/checkFileNameLogs")
    log_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = log_path / f"svn_log_{timestamp}.txt"

    start_date = '2025-05-12'
    end_date = '2025-05-14'

    file_endings = [''] # 可修改为需要过滤的文件后缀

    try:
        svn_log = get_svn_log(repository_path, start_date, end_date)
        parse_and_save_log(svn_log, log_filename, file_endings)
        print(f"从 {start_date} 到 {end_date} 的SVN日志已保存到 {log_filename}")
    except Exception as e:
        print(f"获取或保存SVN日志时发生错误: {e}")

if __name__ == "__main__":
    main()