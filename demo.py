#!/bin/python3
from nicelogger import enable_pretty_logging
enable_pretty_logging('INFO')
import logging
logger = logging.getLogger(__name__)
logger.info('Loading libraries')

import time
import json
from util.str_util import print_msg, send_mail
from taobao_store import TaobaoStore
#from spider.csdn_downloader import CsdnDownloader
#from mail.mail_sender import *
#from mail.mail_sender_browser import *
from config import *
from selenium.common.exceptions import TimeoutException

check_order_period = 60
check_refunding_period = 3600

if __name__ == '__main__':

    # 1.初始化需要的对象
    logger.info('Logging into Taobao store system')
    store = TaobaoStore(taobao_username, taobao_password, 'weibo')
    logger.info('Logged into Taobao store system')
    #downloader = CsdnDownloader(csdn_username, csdn_password)
    #sender = MailSender(mail_username, mail_authorization_code)
    #sender_browser = MailSenderBrowser(mail_username, mail_password, mail_password2)

    # 正则：解析留言内容
    #re_note = re.compile(r"^留言:\s*([\w.-]+@[\w.-]+\.\w+)[\s\S]+?((?:https?://)?[-A-Za-z0-9+&@#/%?=~_|!,.;]+[-A-Za-z0-9+&@#/%=~_|])\s*$")
    # 休眠总时间
    sleep_total_time = 0
    # 存在未留言订单
    #exists_no_note_order = False

    # 2.1上架宝贝
    #store.shelve()
    while True:
        # 2.2爬取订单
        logger.info('Checking for new orders')
        try:
            orders = store.get_new_orders()
        except TimeoutException:
            logger.warning('Timeout when checking for new orders')
            continue
        logger.info('Found %d new orders' % len(orders))

        for order in orders:
            logger.info('Processing order %s' % order)

            ## 2.3下载资源
            #local_path = downloader.download(remote_url, local_dir)
            #if local_path is None:
            #    send_mail(sender, message_download_false, order[0])
            #    continue
            #else:
            #    print_msg("【资源下载成功】本地路径：" + local_path)

            ## 2.4进行下架判断
            #if downloader.download_count == download_total - 1:
            #    if store.unshelve() is False:
            #        send_mail(sender, message_unshelve_false, downloader.download_count)

            ## 2.5 发送邮件
            #if mail_send_type == 0:
            #    download_url = server_file_url + os.path.basename(local_path)
            #    if sender.send(Mail(user_to, download_url)):
            #        print_msg("【邮件发送成功】")
            #    else:
            #        send_mail(sender, message_send_false, order[0])
            #        continue
            #elif mail_send_type == 1:
            #    if sender.send(Mail(user_to, local_path, 2)):
            #        print_msg("【邮件发送成功】")
            #    else:
            #        send_mail(sender, message_send_false, order[0])
            #        continue
            #else:
            #    ret = sender_browser.send(user_to, local_path)
            #    if ret is None:
            #        print_msg("【邮件-浏览器-附件发送成功】")
            #    else:  # 发送失败
            #        send_mail(sender, message_send_mail_error, order[0], ret)
            #        continue

            # 2.6 订单改为已发货
            logger.info('Delivering order %s' %order['id'])
            order.deliver()
            logger.info('Delivered order %s' %order['id'])

        if sleep_total_time >= check_refunding_period:  # 每指定时间检查一次退款和未留言订单
            logger.info('Checking for refunding orders')
            try:
                refunding_orders = store.get_refunding_orders()
                logger.info('Found %d refunding orders' %len(refunding_orders))
                refunding_orders = [order for order in refunding_orders if order['dispute'] == '请卖家处理']
                logger.info('Found %d refunding orders to decline' %len(refunding_orders))
                for order in refunding_orders:
                    logger.info('Declining refunding order %s' % order['id'])
                    order.decline_refunding()
                    logger.info('Declined refunding order %s' % order['id'])
            except TimeoutException:
                logger.warning('Timeout when checking for refunding orders')
        #        send_mail(sender, message_exists_refunding)
        #    if exists_no_note_order:
        #        send_mail(sender, message_notice_for_no_note)
        #        exists_no_note_order = False
            sleep_total_time = 0

        logger.info('Now sleeping for %s seconds' %check_order_period)
        time.sleep(check_order_period)  # 每指定时间抓一次
        sleep_total_time += check_order_period
