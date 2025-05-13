my_list = ["hello world", "python is great", "another example"]
substring = "python"

# 使用列表推导式和any()
if substring in my_list:
    print("子字符串存在于列表中")
else:
    print("子字符串不存在于列表中")