# -*- coding: utf-8 -*-
import time
import re
import requests
import json
import sys
import os
import logging
from bs4 import BeautifulSoup
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
from config import delay_wait

logger = logging.getLogger()

class TaobaoOrder:
    __deliver_url__ = "https://wuliu.taobao.com/user/consign.htm?trade_id="
    __refund_url__ = "https://refund.taobao.com/view_refund_detail.htm?bizOrderId="

    def __init__(self, data, driver):
        self.__data__ = data
        self.__driver__ = driver

    def __getitem__(self, key):
        return self.__data__[key]

    def __repr(self):
        return __str__(self)

    def __str__(self):
        return 'TaobaoOrder' + self.__data__.__str__()
        #return 'TaobaoOrder' + json.dumps(self.__data__, ensure_ascii=False, sort_keys=True)

    def deliver(self):
        self.__driver__.get(self.__deliver_url__ + self['id'])
        no_need_logistics_a = self.__driver__.find_element_by_xpath("//*[@id='dummyTab']/a")
        no_need_logistics_a.click()
        self.__driver__.find_element_by_id("logis:noLogis").click()
        time.sleep(1)

    def decline_refunding(self):
        self.__driver__.get(self.__refund_url__ + self['id'])
        self.__driver__.find_element_by_xpath("//div[@class='center button-item normal']").click()
        time.sleep(1)
        form = self.__driver__.find_element_by_xpath('//textarea[@class="textarea"]')
        form.send_keys('\n不听不听我不听\n略')
        photoUploader = self.__driver__.find_element_by_name('photoUploader')
        photoUploader.send_keys(os.path.realpath('tmp/b.jpg'))
        time.sleep(1)
        photoUploader = self.__driver__.find_element_by_name('photoUploader')
        photoUploader.send_keys(os.path.realpath('tmp/b.jpg'))
        time.sleep(1)
        photoUploader = self.__driver__.find_element_by_name('photoUploader')
        photoUploader.send_keys(os.path.realpath('tmp/b.jpg'))
        time.sleep(1)
        self.__driver__.find_element_by_xpath("//div[@class='center button-item highlight']").click()
        time.sleep(1)
        self.__driver__.find_element_by_xpath("//div[@class='button-item highlight']").click()
        time.sleep(1)
        #print(self.__driver__.page_source)

class TaobaoStore:

    __login_url__ = "https://login.taobao.com/member/login.jhtml"
    __orders_url__ = "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=PAID&tabCode=waitSend"
    # 卖家正出售宝贝URL
    __auction_url__ = "https://sell.taobao.com/auction/merchandise/auction_list.htm"
    # 卖家仓库中宝贝URL
    __repository_url__ = "https://sell.taobao.com/auction/merchandise/auction_list.htm?type=1"
    # 卖家退款URL
    __refunding_url__ = "https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=REFUNDING&tabCode=refunding"
    # 请求留言URL
    __message_url__ = "https://trade.taobao.com/trade/json/getMessage.htm?archive=false&biz_order_id="
    __address_url__ = "https://trade.taobao.com/trade/detail/trade_order_detail.htm?biz_order_id="

    def __init__(self, username, password, login_method='taobao'):
        self.__session__ = requests.Session()
        self.__username__ = username
        self.__password__ = password
        self.cookies = {}
        assert login_method in ['taobao', 'weibo']

        try:
            self.__driver__ = webdriver.Firefox()
        except:
            self.__driver__ = webdriver.Chrome()
        self.__driver__.maximize_window()
        if self.__driver__.get_window_size()['width'] < 800:
            self.__driver__.set_window_size(800,600)
        self.__driver__.set_page_load_timeout(delay_wait)  # 设定页面加载限制时间

        self.login(login_method)

    def __del__(self):
        self.__driver__.close()

    def login(self, login_method):
        self.__driver__.get(self.__login_url__)
        try:
            # 1.点击密码登录，切换到密码登录模式 默认是二维码登录
            username_login_btn = self.__driver__.find_element_by_xpath("//a[@class='forget-pwd J_Quick2Static']")
            if username_login_btn.is_displayed() is True:
                username_login_btn.click()
        except exceptions.ElementNotInteractableException:
            pass

        retry = 0
        while True:
            try:
                if login_method == 'taobao':
                    self.__taobao_login__()
                elif login_method == 'weibo':
                    self.__weibo_login__()
                break
            except:
                retry += 1
                if retry == 5:
                    raise Exception
        self.__save_cookies__()

    def __taobao_login__(self):
        self.__driver__.find_element_by_id("TPL_username_1").send_keys(self.__username__)
        self.__driver__.find_element_by_id("TPL_password_1")
        username_input.send_keys(self.__username)
        password_input.send_keys(self.__password)
        # 4.取得滑块所在div，判断是否display 一般首次登陆不需要滑块验证
        slide_div = self.__driver__.find_element_by_id("nocaptcha")
        if slide_div.is_displayed():
            retry = 0
            while True:
                slide_span = self.__driver__.find_element_by_id("nc_1_n1z")  # 取得滑块span
                action = ActionChains(self.__driver__)
                action.click_and_hold(slide_span)  # 鼠标左键按住span
                action.move_by_offset(259, 10)  # 向右拖动258像素完成验证
                action.perform()
                try:
                    # “点击刷新再来一次”
                    slide_refresh = self.__driver__.find_element_by_xpath("//a[@href='javascript:noCaptcha.reset(1)']")
                    slide_refresh.click()
                    retry += 1
                    if retry == 5:
                        raise Exception
                except exceptions.NoSuchElementException:  # 滑动成功
                    if '验证通过' in self.__driver__.page_source:
                        break
        # 5.获取登陆按钮，并点击登录
        submit_btn = self.__driver__.find_element_by_id("J_SubmitStatic")
        submit_btn.click()
        time.sleep(5)
        # 6.根据提示判断是否登录成功
        try:
            message = self.__driver__.find_element_by_id("J_Message").find_element_by_class_name("error")
            if message.text == u"为了你的账户安全，请拖动滑块完成验证":
                raise Exception
        except exceptions.NoSuchElementException:
            pass

        # 7.有时检测当前环境是否异常，此时休眠一段时间让它检测
        try:
            self.__driver__.find_element_by_id("layout-center")
        except exceptions.NoSuchElementException:
            time.sleep(9)

    def __weibo_login__(self):
        self.__driver__.find_element_by_class_name('weibo-login').click()
        self.__driver__.find_element_by_name("username").send_keys(self.__username__)
        self.__driver__.find_element_by_name("password").send_keys(self.__password__)
        self.__driver__.find_element_by_class_name("W_btn_g").click()
        while 'weibo' in self.__driver__.current_url:
            time.sleep(1)

    def __save_cookies__(self):
        # self.__driver__.switch_to_default_content() #需要返回主页面，不然获取的cookies不是登陆后cookies
        list_cookies = self.__driver__.get_cookies()
        self.cookies = {}
        for s in list_cookies:
            self.cookies[s['name']] = s['value']

    def __get_orders_per_page(self):
        # 1.bs4将资源转html
        html = BeautifulSoup(self.__driver__.page_source, "html5lib")
        # 2.取得所有的订单div
        order_div_list = html.find_all("div", {"class": "item-mod__trade-order___2LnGB trade-order-main"})
        # 3.遍历每个订单div，获取数据
        data_array = []
        for index, order_div in enumerate(order_div_list):
            order={}
            order['id'] = order_div.find("input", attrs={"name": "orderid"}).attrs["value"]
            order['date'] = order_div.find("span", attrs={"data-reactid": re.compile(r"\.0\.5\.3:.+\.0\.1\.0\.0\.0\.6")}).text
            order['item'] = order_div.find("div", attrs={"class": "ml-mod__container___dVhLg production-mod__production___1MKah suborder-mod__production___1eyM1"}).text
            order['buyer'] = order_div.find("a", attrs={"class": "buyer-mod__name___S9vit"}).text
            order['dispute'] = order_div.find("a", attrs={"class": "text-mod__link___2PH1j text-mod__secondary___1Q6zm text-mod__hover___2FQsC"}).text
            # 4.根据订单id组合url，请求订单对应留言
            # order_message = json.loads(self.__session.get(self.__message_url__ + order_id).text)['tip']
            # data_array.append((order_id, order_date, order_buyer, order_message))
            try:
                order['address'] = re.search(r'JSON\.parse\(\'(.*)\'\);',self.__session.get(self.__address_url__ + order['id']).text)
                order['address'] = order['address'].group(1).encode('utf8').decode('unicode_escape')
                try:
                    order['address'] = json.loads(order['address'], encoding='utf8')['tabs'][0]['content']['address']
                except:
                    order['address'] = json.loads(order['address'], encoding='utf8')['tabs'][1]['content']['address']
                assert not order['address'] is None
            except:
                order['address'] = '地址获取失败'
            order['phone'] = re.findall(r'[0-9]{11}', order['address'])
            if len(order['phone']) != 1:
                order['phone'] = '手机号解析失败'
            else:
                order['phone'] = order['phone'][0]
            data_array.append(TaobaoOrder(order, self.__driver__))
        return data_array

    def __get_orders(self):
        result = []
        # 1.进入待发货订单页面
        while True:
            # 2.获取当前页面的订单信息
            time.sleep(2)  # 两秒等待页面加载
            _orders = self.__get_orders_per_page()
            result.extend(_orders)
            try:
                # 3.获取下一页按钮
                next_page_li = self.__driver__.find_element_by_class_name("pagination-next")
                # 4.判断按钮是否可点击，否则退出循环
                next_page_li.get_attribute("class").index("pagination-disabled")
                # print_msg("到达最后一页")
                break
            except ValueError:
                # print_msg("跳转到下一页")
                print(next_page_li.find_element_by_tag_name("a").text)
                next_page_li.click()
                time.sleep(1)
            except exceptions.NoSuchElementException:
                pass
        return result

    def get_new_orders(self):
        self.__driver__.get(self.__orders_url__)
        time.sleep(2)
        return self.__get_orders()

    def unshelve(self):
        try:
            # 1.进入正出售宝贝页面
            self.__driver__.get(self.__auction_url__)
            # 2.点击下架
            choose_checkbox = self.__driver__.find_element_by_xpath("//*[@id='J_DataTable']/table/tbody[1]/tr[1]/td/input[1]")
            choose_checkbox.click()
            unshelve_btn = self.__driver__.find_element_by_xpath("//*[@id='J_DataTable']/div[2]/table/thead/tr[2]/td/div/button[2]")
            unshelve_btn.click()
            return True
        except:
            return False

    def shelve(self):
        # 1.进入仓库宝贝页面
        self.__driver__.get(self.__repository_url__)
        # 2.点击上架
        try:
            choose_checkbox = self.__driver__.find_element_by_xpath("//*[@id='J_DataTable']/table/tbody[1]/tr[1]/td/input")
            choose_checkbox.click()
            shelve_btn = self.__driver__.find_element_by_xpath("//*[@id='J_DataTable']/div[3]/table/tbody/tr/td/div/button[2]")
            shelve_btn.click()
        except exceptions.NoSuchElementException:
            pass

    def get_refunding_orders(self):
        self.__driver__.get(self.__refunding_url__)
        return self.__get_orders()

if __name__ == '__main__':
    store = TaobaoStore("username", "password", login_method='weibo')
    orders = store.get_new_orders()
    for order in orders:
        print(order)
