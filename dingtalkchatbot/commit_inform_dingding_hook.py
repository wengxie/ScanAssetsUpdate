import sys
import re


def inform_commit_messages_to_dingding_hook():
    """
    定义一个hook，用于捕捉项目存在提交动作时，触发弹窗，让开发人员确定是否
    将提交内容消息通过群机器人的方式同步到群里
    :return:
    """
    print("处理处理!!!!!!!!!!!!!!!!!!!!!!!!")

if __name__ == '__main__':
    sys.exit(inform_commit_messages_to_dingding_hook())