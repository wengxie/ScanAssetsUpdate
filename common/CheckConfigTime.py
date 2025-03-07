import os
import re
import datetime
import pandas as pd

from config.path_config import EXCEL_PATH
import chardet

# 加载 TXT 文件，注意修改文件路径和分隔符

time_config_path=file_path = os.path.join(EXCEL_PATH,'TIMER_MAIN.data.txt')

# 打开txt文件，读取所有内容到data字符串
with open(time_config_path, 'r', encoding='UTF-16') as f:
    blocks = f.read().split('\n\n')  # 分割每一对大括号及其内容为一行

time_format = "%Y-%m-%d %H:%M:%S"

# 分别定义红色、绿色和黄色的ANSI escape code
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  # 用于重置颜色

for block in blocks:
    id = re.search(r'id="(.*?)"', block)  # 获取id
    name=re.search(r'name="(.*?)"', block) # 获取name
    open_time = re.search(r'openTime="(.*?)"', block)  # 获取openTime
    end_time = re.search(r'endTime="(.*?)"', block)  # 获取endTime

    if id and open_time and end_time and name:
        id = id.group(1)
        name=name.group(1)
        open_time = open_time.group(1)
        end_time = end_time.group(1)

        try:
            # 计算时间间隔
            open_date = datetime.datetime.strptime(open_time, time_format)
            end_date = datetime.datetime.strptime(end_time, time_format)
            delta = end_date - open_date

            interval_days = delta.days
            interval_hours = delta.seconds // 3600  # 计算超过整天部分的小时数
            interval_minutes = (delta.seconds // 60) % 60  # 计算超过整小时部分的分钟数

            if not (interval_days == 3 and interval_minutes < 1 or
                    interval_days == 7 and interval_minutes < 1 or
                    interval_days == 14 and interval_minutes < 1 or
                    interval_days == 2 and interval_hours == 23 and interval_minutes >= 59 or
                    interval_days == 6 and interval_hours == 23 and interval_minutes >= 59 or
                    interval_days == 13 and interval_hours == 23 and interval_minutes >= 59):
                print(
                    f"{RED}需要注意的活动时间配置:{RESET} ID: {id}, Name: {name}, openTime: {open_time}, endTime: {end_time}, {YELLOW}活动持续时间：{interval_days} days {interval_hours} hours {interval_minutes} minutes")
        except ValueError:
            print(f"{YELLOW}无效的活动时间配置： ID: {id}, Name: {name}, open_time={open_time}, end_time={end_time}")