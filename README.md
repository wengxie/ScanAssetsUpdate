## 环境依赖

终端下执行pip install -r requirements.txt 安装依赖包

## 目录结构描述
### common 
该目录下是通用的资源扫描脚本  
- checkAssetsUpdate：检测国服项目特定的资源文件是否更新、删除、修改
- CheckConfigName：资源文件存在性检查脚本，用于检测配置表中已配置的资源在InBundle文件中是否存在（严格区分大小写）
- CheckConfigTime：扫描游戏活动时间配置
- CheckConfigurationTableUpdate：检测项目配置表文件是否更新、删除、修改
- CheckFileName：扫描文件名称合法性
- CheckGlobalAssetsUpdate： 检测海外项目特定的资源文件是否更新、删除、修改
- CheckResourceName：配置表查找工具，用于查找指定资源文件在配置表中位置

### config
该目录下是通用的配置文件
- filter_config.json：需要过滤掉的配置表/字段序列，需要定期维护
- path_config.py：本地工程路径配置


### dataBackup
该目录下是资源扫描后的数据备份
- domesticBackup：国内资源扫描结果备份
  - historyAssetFileUpdateTime: 资源扫描记录文件夹
  - historyConfigurationFileUpdateTime：配置表扫描记录文件夹
- globalBackup：海外资源扫描结果备份
  - historyAssetFileUpdateTime: 资源扫描记录文件夹

### dingtalkchatbot
该目录下是项目代码连接钉钉自定义机器人的处理模块

### result
该目录下是做资源扫描的输出结果
- domesticLogs：国内资源扫描结果
  - checkAssetsUpdateLogs：资源扫描结果记录文件夹
  - checkConfigurationUpdateLogs：配置表扫描结果记录文件夹
- globalLogs：海外资源扫描结果
  - checkAssetsUpdateLogs：资源扫描结果记录文件夹


### testcase 
该目录下用于存放后续可能需要用到的测试用例，例如Excel表格


## 项目资源更新检测脚本使用方式

1.打开checkAssetsUpdate.py脚本，根据自己项目的路径修改下方路径配置字段值

    # 个人代码项目工程中，AssetsPath.xlsx文件的绝对路径
    excel_path = r'D:\wengxie\Pycharm\PythonProject\ScanAssetsUpdate\AssetsPath.xlsx'
    # 个人Unity工程路径下项目的MainProject路径
    unity_root_path = r'D:\svn\svnReleasetrunkCHS\client\MainProject'


2.在checkAssetsUpdate.py脚本的最下方，先将check_file_update注释掉，然后右键运行checkAssetsUpdate.py脚本，
目的在于扫描excel中配置的各主要资源（Avatar、鱼竿与鱼竿皮肤、挂件、钓点背景）文件的时间，保存在historyAssetsFileUpdateTime文件夹下。

    # 用最新的资源文件更新时间与旧的时间对比，从而找出哪些文件更新了
    #check_file_update(allFiles_InBundle,fileUpdateLogs_name_path,checkUpdateLogs_path)

3.在checkAssetsUpdate.py脚本的最下方，再将write_fileUpdateLogs注释掉，并且去掉check_file_update的注释，
然后回到项目文件中更新文件资源后，再右键运行checkAssetsUpdate.py脚本，就会输出检测项目资源新增、删除以及更新的检查结果日志，
并且将日志保存在checkAssetsUpdateLogs中

    # 将各个资源文件的最新更新时间保存下来，方便对比
    # write_fileUpdateLogs(fileUpdateLogs_path,storage_echo_filelastUpdate_time_tuple)

    # 用最新的资源文件更新时间与旧的时间对比，从而找出哪些文件更新了
    check_file_update(allFiles_InBundle,fileUpdateLogs_name_path,checkUpdateLogs_path)

## 资源文件后缀合法性检测脚本使用说明（checkFileName.py）

1.修改配置路径为本地路径

    # 在config.py文件中修改配置路径。

2.运行checkFileName.py脚本。输出结果保存在checkFileName.txt中，每次运行脚本会覆盖之前的纪录

3.分析输出文件checkFileName.txt
    
    #xxx：后缀含有大写字母的文件名
    #xxx：后缀含有空格的文件名
    #xxx；fish文件夹中的重名文件

资源文件存在性检测脚本使用说明（checkConfigName.py）：

1.修改配置路径为本地路径

    # 在config.py文件中修改配置路径。

2.运行checkConfigName.py脚本。输出结果保存在checkConfigName.txt中，每次运行脚本会覆盖之前的纪录

3.分析输出文件checkFileName.txt
    
    #Missing resource files:Inbundle文件夹中缺失的资源文件名
    #输出格式：【字段名】【资源文件名】【所在配置表名】
    
    








