import datetime
import json
import sys
import git
from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard, FeedLink, CardItem
import easygui

if __name__ == '__main__':
    # 新版的钉钉自定义机器人必须配置安全设置（自定义关键字、加签、IP地址/段），其中“加签”需要传入密钥才能发送成功
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=617840966c93c50d23069a00df7971158877b7a49ffde3e28bd0c29ccf702c38'
    secret = 'SEC3d5ac1ea14fa293b715ab2d7033e2a4e5818214ce656088d85a5c44c687c1269'
    # 捕获git提交的信息，包含开发人员、提交内容、提交时间
    repo = git.Repo(search_parent_directories=True)
    authorName = repo.commit().author.name
    message = repo.commit().message
    date = repo.commit().committed_datetime
    date_str = datetime.datetime.strftime(date, '%Y年%m月%d日%H时%M分%S秒')
    # 获取改动文件列表
    changed_files = repo.head.commit.stats.files

    # 初始化机器人
    # 新版安全设置为“加签”时，需要传入请求密钥
    # 同时支持设置消息链接跳转方式，默认pc_slide=False为跳转到浏览器，pc_slide为在PC端侧边栏打开
    # 同时支持设置消息发送失败时提醒，默认fail_notice为false不提醒，开发者可以根据返回的消息发送结果自行判断和处理
    robotxiaoding = DingtalkChatbot(webhook, secret, pc_slide=True, fail_notice=False)


    # 通过弹窗确定是否同步修改内容
    ret = easygui.indexbox(
        "请确定是否需要将提交内容通过机器人同步到钉钉群中\n\n注意：如果选择同步，将会@所有群成员！！",
        title='确定是否将提交内容同步群成员', choices=['确认同步', '暂不同步'])
    if ret == 0:
        # text 控制钉钉自定义机器人中发送消息
        robotxiaoding.send_text(msg="提交代码： " + authorName +
                                    "\n提交时间： " + date_str +
                                    "\n修改内容： " + message +
                                    "改动文件： " + json.dumps(changed_files, indent=4), is_at_all=False)
        sys.exit(0)
    else :
        sys.exit(0)
