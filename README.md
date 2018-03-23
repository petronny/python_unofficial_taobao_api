非官方淘宝API
====
# __Warning__
__USING ANY CONTENT OF THIS REPOSITORY IS ON YOUR OWN RISK.__

# Features
* 登录
	* 淘宝账号登录
	* 微博账号登录
* 获取订单
	* 获取未发货订单
	* 获取退款订单
* 订单解析
	* 商品名称
	* 收货地址
	* 手机号
* 订单发货
	* 虚拟商品发货(无物流)
* 退款处理
	* 拒绝退款
	* 添加退款说明与附加图片

# Dependencies
* Python 3
* BeautifulSoup4
* selenium
* Firefox / Chrome
* geckodriver / chromedriver

# Installation
Just clone this repository
```sh
$ git clone https://github.com/petronny/python_unofficial_taobao_api
```

# Usage
```python
from taobao_store import TaobaoStore

store = TaobaoStore("username", "password", login_method='weibo')
orders = store.get_undelivered_orders()
for order in orders:
    order.deliver()
```

Please install [XVFB](https://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml) to run it on a Linux server.

# License
* [Apache-2.0](https://github.com/petronny/unofficial-taobao-api/blob/master/LICENSE)

# Acknowledgement
* [localhost02/Taobao_order_robot](https://github.com/localhost02/Taobao_order_robot)
