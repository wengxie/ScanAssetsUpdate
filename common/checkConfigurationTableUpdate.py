# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import os
import time

# 用于往txt中导入颜色字体
import colorama

from config import path_config


# 找出“\client\MainProject\Assets\InBundle”文件夹下所有文件
def find_all_Configuration_in_InBundle(allFiles_InBundle,configuration_table_path):
    # 将所有找到的文件存在列表中
    for filepath, dirnames, filenames in os.walk(configuration_table_path):
        for filename in filenames:
            allFiles_InBundle.append(os.path.join(filepath, filename))
    # 用于输出所有找到的文件
    # for file in allFiles_InBundle:
    #     print(file)

# 记录“\client\MainProject\Assets\InBundle”文件夹下所有文件最近一次的更新时间
def record_file_update(storage_echo_filelastUpdate_time_list, allFiles_InBundle):
    for file in allFiles_InBundle:
        file_lastUpdate_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file)))
        storage_echo_filelastUpdate_time_list.append((file,os.path.getmtime(file), file_lastUpdate_time))
    return storage_echo_filelastUpdate_time_list

# 将各个资源文件的最新更新时间保存下来，方便对比
def write_fileUpdateLogs(fileUpdateLogs_path,storage_echo_filelastUpdate_time_tuple):
    logsfile = fileUpdateLogs_path + '\\Configuration' + time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
    with open(logsfile,'w',encoding='utf-8') as f:
        f.write("(\n")
        for echo_filelastUpdate_time in storage_echo_filelastUpdate_time_tuple:
            f.write(str(echo_filelastUpdate_time) + '\n')
        f.write(")")

# 查文件的更新、删除、新增
def check_file_update(allFiles_InBundle,fileUpdateLogs_name_path,checkUpdateLogs_path):
    # 将历史更新日志文件提取出来转换为元组保存
    with open(fileUpdateLogs_name_path, 'r', encoding='utf-8') as f:
        historyFileUpdateTimelogs_list = f.read().split('\n')[1:-1]
        historyFileUpdateTimelogs_list_temp = []
        for historyFileUpdateTimelog in historyFileUpdateTimelogs_list:
            historyFileUpdateTimelogs_list_temp.append(eval(historyFileUpdateTimelog))
        historyFileUpdateTimelogs_tuple = tuple(historyFileUpdateTimelogs_list_temp)
        # print(historyFileUpdateTimelogs_tuple)

    store_updatetimefiles_logs = []
    store_deletefiles_logs = []
    store_addfiles_logs = []
    for historyfilepath, historyfilepath_time, historyfilepathtime_format in historyFileUpdateTimelogs_tuple:
        #print(historyfilepath, historyfilepath_time, historyfilepathtime_format)
        # 历史资源文件在更新后没有被删除的情况下
        if historyfilepath in allFiles_InBundle:
            # 如果文件最新时间大于历史此文件更新时间，说明文件被更新过
            if os.path.getmtime(historyfilepath) > historyfilepath_time:
                allFiles_InBundle.remove(historyfilepath)
                store_updatetimefiles_logs.append(historyfilepath+"文件被更新过，最新更新时间为："+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(historyfilepath)))+"\n")
            # 文件没有被更新过
            else:
                allFiles_InBundle.remove(historyfilepath)
                continue
        else:
            store_deletefiles_logs.append(colorama.Fore.RED + historyfilepath + " 文件被删除，请着重注意！！！！！！\n")

    # 如果文件列表中还有剩余元素，说明新增的文件资源，也需要着重注意
    if len(allFiles_InBundle) != 0:
        for historyfilepath_after_remove in allFiles_InBundle:
            store_addfiles_logs.append(colorama.Fore.YELLOW + "项目更新后，新增文件资源："+historyfilepath_after_remove + " 需要着重注意！！！！！！\n")

    store_allfiles_logs = (store_updatetimefiles_logs + [colorama.Fore.YELLOW+"-------以下为新增资源-------\n"]
                           + store_addfiles_logs + [colorama.Fore.RED+"-------以下为被删除资源-------\n"] + store_deletefiles_logs)

    print(*store_allfiles_logs)

    checkUpdateLogsfile = checkUpdateLogs_path + '\\checkConfigurationUpdateLog' + time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
    with open(checkUpdateLogsfile, 'w', encoding='utf-8') as f:
        f.writelines(store_allfiles_logs)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # 个人国内Unity工程的策划表路径，直接去修改config下的path_config文件
    configuration_table_path = path_config.DOMESTIC_UNITY_ROOT_PATH + r'\datapool\策划模板导出工具'
    # 文件更新时间记录路径
    fileUpdateLogs_path = os.path.dirname(os.path.split(os.path.realpath(__file__))[0]) + r'\dataBackup\domesticBackup\historyConfigurationFileUpdateTime'
    # 用于存储每次对比文件更新的日志记录路径
    checkUpdateLogs_path = os.path.dirname(os.path.split(os.path.realpath(__file__))[0]) + r'\result\domesticLogs\checkConfigurationUpdateLogs'
    # 用于对比的历史文件名路径
    fileUpdateLogs_name_path = fileUpdateLogs_path + '\\' + 'Configuration20241219_155508'

    # 找出“\client\MainProject\Assets\InBundle”文件夹下所有文件
    allFiles_InBundle = []
    find_all_Configuration_in_InBundle(allFiles_InBundle, configuration_table_path)

    # 记录“\client\MainProject\Assets\InBundle”文件夹下所有文件最近一次的更新时间
    storage_echo_filelastUpdate_time_list =[]
    # 将文件时间以三元组的方式存储(文件,文件最近一次更新时间戳,时间戳格式转换年月日格式)
    storage_echo_filelastUpdate_time_tuple = tuple(record_file_update(storage_echo_filelastUpdate_time_list, allFiles_InBundle))

    # 将各个配置表文件的最新更新时间保存下来，方便对比
    #write_fileUpdateLogs(fileUpdateLogs_path,storage_echo_filelastUpdate_time_tuple)

    # 用最新的资源文件更新时间与旧的时间对比，从而找出哪些文件更新了
    check_file_update(allFiles_InBundle,fileUpdateLogs_name_path,checkUpdateLogs_path)

