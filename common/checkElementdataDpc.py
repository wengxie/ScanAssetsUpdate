# 目的：检查钓鱼项目策划修改配置表后是否存在表未导表的情况
# 设计思路：所有的配置表A.data.txt修改都都需要导表成一个elementdata.dpc文件，如果存在表时间比dpc时间完的情况，说明此表未导
# 开发人员：翁勰
# 开发时间：2025.05.13
import os
import time
import colorama

# 全局变量
from config import path_config

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 项目策划表路径
    planning_table_path = path_config.ELEMENT_DATA_DPC_ROOT_PATH + r'\datapool\策划模板导出工具'
    # elementdata.dpc文件路径
    elementdata_dpc_path = path_config.ELEMENT_DATA_DPC_ROOT_PATH + r'\client\MainProject\Assets\elementdata.dpc'
    # elementdata.dpc文件最新时间
    elementdata_dpc_path_lastUpdate_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(elementdata_dpc_path)))
    #print(elementdata_dpc_path_lastUpdate_time)
    allPlanning_table = []
    # 判断是否存在有表未导成dpc文件
    if_exist_planningTable_not_exported_to_dpc = False
    # 提取所有配置表
    for filepath, dirnames, filenames in os.walk(planning_table_path):
        for filename in filenames:
            allPlanning_table.append(os.path.join(filepath, filename))
    # 将所有配置表时间与dpc对比
    print(colorama.Fore.BLUE +"DPC文件：elementdata.dpc 最新更新时间为："+elementdata_dpc_path_lastUpdate_time+"\n")
    for echo_planning_table in allPlanning_table:
        # 如果识别到当前表时间 > dpc时间，说明存在此表未导表
        if os.path.getmtime(echo_planning_table) > os.path.getmtime(elementdata_dpc_path):
            if_exist_planningTable_not_exported_to_dpc = True
            print(colorama.Fore.RED + "策划表：" + echo_planning_table + "  未导表成elementdata.dpc文件，此表最新时间为："
                  + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(echo_planning_table))))

    if if_exist_planningTable_not_exported_to_dpc == False:
        print(colorama.Fore.GREEN + "所有的配置表都已成功导为dpc！！！！！！！！！")