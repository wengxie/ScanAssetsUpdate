

from dingtalkchatbot.chatbot import DingtalkChatbot, ActionCard, FeedLink, CardItem



if __name__ == '__main__':
    # 新版的钉钉自定义机器人必须配置安全设置（自定义关键字、加签、IP地址/段），其中“加签”需要传入密钥才能发送成功
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=617840966c93c50d23069a00df7971158877b7a49ffde3e28bd0c29ccf702c38'
    secret = 'SEC3d5ac1ea14fa293b715ab2d7033e2a4e5818214ce656088d85a5c44c687c1269'

    #用户手机号列表
    at_mobiles = ['13394604978']

    # 初始化机器人
    # 新版安全设置为“加签”时，需要传入请求密钥
    # 同时支持设置消息链接跳转方式，默认pc_slide=False为跳转到浏览器，pc_slide为在PC端侧边栏打开
    # 同时支持设置消息发送失败时提醒，默认fail_notice为false不提醒，开发者可以根据返回的消息发送结果自行判断和处理
    robotxiaoding = DingtalkChatbot(webhook, secret, pc_slide=True, fail_notice=False)



    # text 控制钉钉自定义机器人中发送消息
    robotxiaoding.send_text(msg="测试测试",is_at_all=False)

    # image
    # robotxiaoding.send_image(pic_url='https://i.postimg.cc/T32bVBFc/xw.png')
    #
    # # link
    # robotxiaoding.send_link(title='万万没想到，某小璐竟然...',
    #                    text='故事是这样子的...',
    #                    message_url='http://www.kwongwah.com.my/?p=454748',
    #                    pic_url='https://pbs.twimg.com/media/CEwj7EDWgAE5eIF.jpg')
    #
    # # markdown
    # # 1、提醒所有人
    # robotxiaoding.send_markdown(title='氧气文字', text='#### 广州天气\n'
    #                                               '> 9度，西北风1级，空气良89，相对温度73%\n\n'
    #                                               '> ![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n'
    #                                               '> ###### 10点20分发布 [天气](https://www.seniverse.com/) \n',
    #                        is_at_all=True)
    # # 2、提醒指定手机用户，并在text内容中自定义”@用户“的位置
    # robotxiaoding.send_markdown(title='氧气文字', text='#### 广州天气 @18825166XXX\n'
    #                                               '> 9度，西北风1级，空气良89，相对温度73%\n\n'
    #                                               '> ![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n'
    #                                               '> ###### 10点20分发布 [天气信息](https://www.seniverse.com/)\n',
    #                        at_mobiles=at_mobiles, is_auto_at=False)
    #
    # # 整体跳转ActionCard
    # btns1 = [CardItem(title="查看详情", url="https://www.dingtalk.com/")]
    # actioncard1 = ActionCard(title='万万没想到，竟然...',
    #                          text='![markdown](http://www.songshan.es/wp-content/uploads/2016/01/Yin-Yang.png) \n### 故事是这样子的...',
    #                          btns=btns1,
    #                          btn_orientation=1,
    #                          hide_avatar=1)
    # robotxiaoding.send_action_card(actioncard1)
    #
    # # 单独跳转ActionCard
    # # 1、两个按钮选择
    # btns2 = [CardItem(title="支持", url="https://www.dingtalk.com/"),
    #          CardItem(title="反对", url="https://www.dingtalk.com/")]
    # actioncard2 = ActionCard(title='万万没想到，竟然...',
    #                          text='![markdown](http://www.songshan.es/wp-content/uploads/2016/01/Yin-Yang.png) \n### 故事是这样子的...',
    #                          btns=btns2,
    #                          btn_orientation=1,
    #                          hide_avatar=1)
    # robotxiaoding.send_action_card(actioncard2)
    # # 2、三个按钮选择
    # btns3 = [CardItem(title="支持", url="https://www.dingtalk.com/"),
    #          CardItem(title="中立", url="https://www.dingtalk.com/"),
    #          CardItem(title="反对", url="https://www.dingtalk.com/")]
    # actioncard3 = ActionCard(title='万万没想到，竟然...',
    #                          text='![markdown](http://www.songshan.es/wp-content/uploads/2016/01/Yin-Yang.png) \n### 故事是这样子的...',
    #                          btns=btns3,
    #                          btn_orientation=1,
    #                          hide_avatar=1)
    # robotxiaoding.send_action_card(actioncard3)
    #
    # # FeedCard类型
    # card1 = CardItem(title="氧气美女", url="https://www.baidu.com/",
    #                  pic_url="http://pic1.win4000.com/wallpaper/2020-03-11/5e68b0557f3a6.jpg")
    # card2 = CardItem(title="氧眼美女", url="https://www.baidu.com/",
    #                  pic_url="http://pic1.win4000.com/wallpaper/2020-03-11/5e68b0557f3a6.jpg")
    # card3 = CardItem(title="氧神美女", url="https://www.baidu.com/",
    #                  pic_url="http://pic1.win4000.com/wallpaper/2020-03-11/5e68b0557f3a6.jpg")
    # cards = [card1, card2, card3]
    # robotxiaoding.send_feed_card(cards)

    #文件类型
    # file_path = r'D:\wengxie\Pycharm\PythonProject\ScanAssetsUpdate\result\domesticLogs\checkAssetsUpdateLogs\checkAssetsUpdateLog20250529_113202'
    # #robotxiaoding.send_file(file_path)
    # url = "https://oapi.dingtalk.com/media/upload"
    # headers = {
    #     "Content-Type": "multipart/form-data"
    # }
    # files = {'file': open(file_path, 'rb')}
    # params = {
    #     "webhook": webhook,  # 从钉钉开放平台获取的access_key
    #     "secret": secret  # 从钉钉开放平台获取的secret
    # }
    # response = requests.post(url, headers=headers, files=files, params=params)
    # response.raise_for_status()  # 确保请求成功
    # print(response.json().get('media_id'))