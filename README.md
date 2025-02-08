### **#环境依赖**

1.终端下执行pip install -r requirements.txt 安装依赖包

### **#目录结构描述**

##### ├──checkAssetsUpdateLogs                _# 资源扫描结果记录文件夹_
##### │   ├──checkAssetsUpdateLogXXXX         _# 资源扫描结果1_
##### │   ├──checkAssetsUpdateLogXXXX         _# 资源扫描结果2_
##### ├──checkConfigurationUpdateLogs         _# 配置表扫描结果记录文件夹_
##### │   ├──checkConfigurationUpdateLogXXX   _# 配置表扫描结果1_
##### │   ├──checkConfigurationUpdateLogXXX   _# 配置表扫描结果2_
##### ├──historyAssetsFileUpdateTime          _# 资源扫描记录文件夹_
##### │   ├──Assets20250104_102630            _# 25年1月4号10点26分30秒扫描的资源时间记录_
##### │   ├──Assets20250107_101151            _# 25年1月7号10点11分51秒扫描的资源时间记录_
##### ├──historyConfigurationFileUpdateTime   _# 配置表扫描记录文件夹_
##### │   ├──Configuration20241118_144209     _# 24年11月18日14点42分09秒扫描的配置表时间记录
##### │   ├──Configuration20241219_155508     _# 24年12月19日15点55分08秒扫描的配置表时间记
##### ├──checkFileName                        _# 资源扫描结果纪录文件夹
#####     ├──config.py                        _# 本地工程路径
#####     ├──filter_config.json               _# 枚举需要过滤掉的配置表/字段，需要定期维护
#####     ├──checkFileName.txt                _# checkFileName结果纪录文件
#####     ├──checkConfigName.txt              _# checkConfigName.py结果纪录文件
##### ├──AssetsPath.xlsx*                     _# 各主要资源（Avatar、鱼竿与鱼竿皮肤、挂件、钓点背景）路径整理_
##### ├──checkAssetsUpdate.py*                _# 项目资源检测脚本_
##### ├──checkConfigurationTableUpdate.py     _# 配置表检测脚本_
##### ├──checkConfigName.py*                  _# 资源文件存在性检测脚本_
##### ├──checkFileName.py*                    _# 资源文件后缀合法性检测脚本_
##### ├──requirements-all.txt                 _# 环境导出的依赖包_
（其中使用*结尾的文件是比较重要的文件）

### **#使用方式**
以项目资源更新检测为例：

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

资源文件后缀合法性检测脚本使用说明（checkFileName.py）；

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
    
    #xxx：后缀含有大写字母的文件名
    #xxx：后缀含有空格的文件名
    #xxx；fish文件夹中的重名文件
    
    








