import os

import numpy
import pandas
import re
import xlrd

if __name__ == '__main__':
    # listname = os.listdir("D:\svn\svnReleasetrunkCHS\client\MainProject\Assets\ArtImport\Art_scene")
    # for i in listname:
    #     if "meta" not in i:
    #         print(i)

    excelpath = r'D:\wengxie\Pycharm\PythonProject\ScanAssetsUpdate\AssetsPath.xlsx'
    dataframe = pandas.read_excel(excelpath)
    textpath = r'D:\wengxie\Pycharm\PythonProject\ScanAssetsUpdate\text'
    path_array = dataframe[['资源文件名','资源详细介绍']].to_numpy()
    print("全部数据：")
    print(path_array)
    keys = []
    for key in path_array[:, 0]:
        keys.append(key[key.rfind('\\') + 1:])

    values = path_array[:, 1]  # 第三列数据作为值
    result_dict = {k: v for k, v in zip(keys, values)}
    print(result_dict)

    text = r'018\\male_018_lowerbody_3p.prefab'
    # pattern = r'\\([^\\.]+)\.'
    # matches = re.findall(pattern, text)
    last_slash_index = text.rfind('\\')
    matches = text[last_slash_index + 1:]
    print(matches)
    print(result_dict[matches])
    # with open(textpath,'w',encoding='utf-8') as f:
    #     f.write(dataframe['主路径'].dropna().to_string())
    # print("全部数据：")
    # path_array, indices = numpy.unique(dataframe['主路径'].dropna().to_numpy(),return_index=True)
    # print(path_array)
    # print(dataframe['主路径'].dropna().to_numpy()[numpy.sort(indices)])
    # unity_root_path = r'D:\svn\svnReleasetrunkCHS\client\MainProject'
    # allFiles_InBundle = []
    # for items in path_array.flat:
    #     items_path = unity_root_path + '\\' + items
    #     for filepath, dirnames, filenames in os.walk(items_path):
    #         for filename in filenames:
    #             allFiles_InBundle.append(os.path.join(filepath, filename))
    # # 用于输出所有找到的文件
    # for file in allFiles_InBundle:
    #     print(file)