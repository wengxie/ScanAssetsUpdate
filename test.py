import datetime
import sys
import git
from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard, FeedLink, CardItem
import easygui

# 捕获git提交的信息，包含开发人员、提交内容、提交时间
repo = git.Repo(search_parent_directories=True)
authorName = repo.commit().author.name
message = repo.commit().message
date = repo.commit().committed_datetime
date_str = datetime.datetime.strftime(date, '%Y年%m月%d日%H时%M分%S秒')
print(repo.commit())