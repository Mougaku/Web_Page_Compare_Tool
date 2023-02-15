from threading import Thread
import time
import os

from auto_test import start_test
import csv_controller
import config


if __name__=="__main__":
    # 从CSV读取Sitemap list
    csv_read = csv_controller.csv_read(config.check_list)
    link_pairs = csv_read.get_csv()[1:]

    # 获取当前时间并创建result文件夹
    time_now = time.strftime("%Y%m%d_%H_%M_%S", time.localtime()) 
    os.mkdir(f"result\\{time_now}")

    # 创建对象
    test_obj = start_test(link_pairs)

    # 创建多线程
    chrome_test = Thread(target=test_obj.start_test, args=("chrome", time_now,))
    iphone_test  = Thread(target=test_obj.start_test, args=("iPhone 12 Pro", time_now,))
    android_test = Thread(target=test_obj.start_test, args=("Samsung Galaxy S8+", time_now, ))
    ipadair_test = Thread(target=test_obj.start_test, args=("iPad Air", time_now, ))
    ipadmini_test = Thread(target=test_obj.start_test, args=("iPad Mini", time_now, ))
    firefox_test = Thread(target=test_obj.start_test, args=("firefox", time_now, ))

    # 开始执行测试任务
    chrome_test.start()
    iphone_test.start()
    # android_test.start()
    # ipadair_test.start()
    # ipadmini_test.start()
    # firefox_test.start()
    

'''
备注:
    · 网络/网页性能较差时, 多线程可能因为响应过慢导致打开网页时Timeout


优化点:
    · 维护到github, 进行版本管理(!!删除敏感信息) - Normal, Low
    · 优化config(内容优化，读取方式优化) - Normal, Low
    · 添加log模块 - Normal, Low

    · 优化代码结构(重构屎山) - Normal, Low
    · 优化alt对比 - Hard, Middle
    · 增加link对比(目前只对比了是否带有html或php, 逻辑设计比较有难度) - Hard, Middle
    · 完善火狐浏览器的对比(目前火狐浏览器会产生各种问题，包括验证失败，截图滚动错误等) - Hard, Middle
'''