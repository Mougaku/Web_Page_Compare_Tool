from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from PIL import Image,ImageChops
import numpy as np
import time
import os

import config
import csv_controller



class start_test():

    def __init__(self, link_pairs):
        self.link_pairs = link_pairs


    def start_test(self, end, time_now):

        # 初始化模块，启动webdriver并点击同意按钮
        auto_test = test_tool(end, time_now)
        res = []

        # 对每对URL进行对比
        for i in range(len(self.link_pairs)):
            if end == "chrome":
                res = auto_test.site_diff(self.link_pairs[i])
            else:
                res = auto_test.layout_diff(self.link_pairs[i])
            auto_test.save(res)
        auto_test.quit()



class test_tool():

    def __init__(self, end, time_now):
        self.time_now = time_now
        self.end = end

        # 根据测试设备创建文件夹
        os.mkdir(f"result\\{self.time_now}\\{end}")
        os.mkdir(f"result\\{self.time_now}\\{end}\\screenshot")
        os.mkdir(f"result\\{self.time_now}\\{end}\\layout_res")

        # 创建result文档
        self.csv_write = csv_controller.csv_write(f"result//{self.time_now}//{end}//result.csv")
        
        # 根据测试设备启动selenium并写入title(除chrome外, 其他设备只需要测试layout)
        if end == "firefox" :
            self.driver = webdriver.Firefox(firefox_binary=r"C:\Program Files\Mozilla Firefox\firefox.exe")
            self.csv_write.writerow_csv(["No", "Old Page", "New Page", "Layout"])
        else :
            opt = Options()
            # chrome模拟移动端设备需要设置option
            if end != "chrome":
                opt.add_experimental_option("mobileEmulation", { "deviceName": end })
                self.csv_write.writerow_csv(["No", "Old Page", "New Page", "Layout"])
            else:
                self.csv_write.writerow_csv(["No", "Old Page", "New Page", "Title", "Description", "Keywords", "Alt", "Links", "Layout"])
            self.driver = webdriver.Chrome(options = opt)
        
        self.site_init(config.domain)
        

    # 初始化页面，登录测试账号，点击同意按钮（需要根据不同站点修改）
    def site_init(self, main_page):
        if main_page:
            driver = self.driver

            # 在原站点点击同意
            # driver.get(main_pages[0])
            # driver.find_element(By.ID, "authenticationBtn").click()
            
            try:
                # 登录测试账号
                driver.get(main_page)
                driver.find_element(By.ID, "idp1").click()
                driver.find_element(By.ID, "username").send_keys(config.username)
                driver.find_element(By.ID, "password").send_keys(config.password)
                driver.find_element(By.ID, "submit_button").click()
                
                # 火狐浏览器不会自动等待加载完成，需要手动等待
                if self.end == "firefox":
                    time.sleep(60)
            except:
                pass

            # 在新站点点击同意
            # driver.find_element(By.ID, "authenticationBtn").click()


    # 获取截图，根据窗口高度滑动获取多张截图，再使用PIL和numpy包拼接
    def get_screen_shot(self, page_no, type):
        driver = self.driver
        window_height = driver.get_window_size()['height'] # 窗口高度

        page_height = driver.execute_script('return document.documentElement.scrollHeight') # 页面高度
        driver.save_screenshot(f'{self.end}_page_{page_no}_{type}.png')

        if page_height != window_height:
            n = page_height // window_height # 需要滚动的次数
            base_mat = np.atleast_2d(Image.open(f'{self.end}_page_{page_no}_{type}.png')) # 打开截图并转为二维矩阵
            os.remove(f'{self.end}_page_{page_no}_{type}.png')
            for i in range(n):
                driver.execute_script(f'document.documentElement.scrollTop={window_height*(i+1)};')
                time.sleep(.5)
                driver.save_screenshot(f'{self.end}_{page_no}_{i}.png') # 保存截图
                mat = np.atleast_2d(Image.open(f'{self.end}_{page_no}_{i}.png')) # 打开截图并转为二维矩阵
                os.remove(f'{self.end}_{page_no}_{i}.png')
                base_mat = np.append(base_mat, mat, axis=0) # 拼接图片的二维矩阵
            Image.fromarray(base_mat).save(f'{self.end}_page_{page_no}_{type}.png')
        os.rename(f'{self.end}_page_{page_no}_{type}.png', f'result\\{self.time_now}\\{self.end}\\screenshot\\page_{page_no}_{type}.png')


    # 对比新旧站点的截图，输出结果
    def check_layout(self, page_no):
        # Check layout
        image_old = Image.open(f'result\\{self.time_now}\\{self.end}\\screenshot\\page_{page_no}_old.png').convert('RGB')
        image_new = Image.open(f'result\\{self.time_now}\\{self.end}\\screenshot\\page_{page_no}_new.png').convert('RGB')
        try: 
            diff = ImageChops.difference(image_old, image_new)
            if diff.getbbox() is None:
            # 图片间没有任何不同则直接退出
                layout_res = True
            else:
                # 将对比图片颜色反转，反色转为正常色；然后保存
                inverted = ImageChops.invert(diff)
                inverted.save(f'result\\{self.time_now}\\{self.end}\\layout_res\\page_{page_no}.png')
                layout_res = False
        except ValueError as e:
            layout_res = "Error"

        return layout_res


    # 获取页面信息
    def get_info(self, link, page_no, type):
        driver = self.driver

        # 打开该页面
        driver.get(link)

        # 获取SEO Meta Tag
        title = driver.title
        try:
            description = driver.find_element(By.NAME, "Description").get_attribute("content")
        except:
            description = driver.find_element(By.NAME, "description").get_attribute("content")

        # skip from error
        # if str(page_no) in ["1", "7", "8"]:
        #     kewords = ""
        # else:
        try:
            kewords = driver.find_element(By.NAME, "Keywords").get_attribute("content")
        except:
            kewords = driver.find_element(By.NAME, "keywords").get_attribute("content")

        # 获取所有图片元素
        imgs = driver.find_elements(By.TAG_NAME, "img")
        # 获取所有Link元素
        links = driver.find_elements(By.TAG_NAME, "a")

        # 对当前页面截图
        self.get_screen_shot(page_no, type)

        return title, description, kewords, imgs, links


    # 执行Layout测试任务
    def layout_diff(self, link_pair):
        try:
            # Get links
            page_no = link_pair[0]
            page_old = link_pair[1]
            page_new = link_pair[2]

            # 获取新旧站点截图
            self.driver.get(page_old)
            self.get_screen_shot(page_no, "old")
            self.driver.get(page_new)
            self.get_screen_shot(page_no, "new")

            # 对比截图
            res = self.check_layout(page_no)

            return [page_no, page_old, page_new, res]
        except:
            return [page_old, page_new, "Error"]


    # 执行整体测试任务
    def site_diff(self,link_pair):
        try:
            # Get links
            page_no = link_pair[0]
            page_old = link_pair[1]
            page_new = link_pair[2]

            # Get information from old page
            info_old = self.get_info(page_old, page_no, "old")

            # Get Alt info of old page from img elements
            imgs_old = info_old[3]
            alt_old = []
            for i in imgs_old:
                try:
                    alt_old.append(i.get_attribute("alt"))
                except:
                    continue

            # Get Links info
            # links_old = info_old[4]
            # link_old = []
            # for i in links_old:
            #     try:
            #         link_old.append(self.url_handler(i.get_attribute("href")))
            #     except:
            #         continue
            # url_old = []
            # for i in info_old[4]:
            #     try:
            #         if i.get_attribute("href") == "" or \
            #             i.get_attribute("href") == None or \
            #             i.get_attribute("href").split("#")[0] == page_old :
            #             continue
            #         else :
            #             url_old.append(i.get_attribute("href")) 
            #     except:
            #         continue

            # Get information from new page
            info_new = self.get_info(page_new, page_no, "new")

            # Compare SEO Meta tag
            # if info_old[0].split("｜")[0].split("|")[0].strip() == info_new[0].split("｜")[0].split("|")[0].strip():
            #     title_res = True
            # else :
            #     title_res = info_new[0]
            # if info_old[1] == info_new[1]:
            #     description_res = True
            # else :
            #     description_res = info_new[1]
            # if info_old[2] == info_new[2]:
            #     kewords_res = True
            # else :
            #     kewords_res = info_new[2]

            # Get SEO Meta tag (根据业务需要，有时新站点与原站点不一定一致，需要获取下来手动与需求文档对比)
            title_res = info_new[0]
            description_res = info_new[1]
            kewords_res = info_new[2]
            

            # Compare images alt, 若该元素没有alt或该alt在老站点页面中不存在，则输出该图片的src
            imgs_new = info_new[3]
            alt_res = []
            for i in imgs_new:
                try:
                    alt = i.get_attribute("alt")
                    if alt == "" or alt not in alt_old:
                        alt_res.append(i.get_attribute("src"))
                except:
                    alt_res = False
                    break
            if alt_res == []:
                alt_res = True

            # Check links，先去掉没有href的元素和外部链接
            url = []
            for i in info_new[4]:
                try:
                    if i.get_attribute("href") == "" or \
                        i.get_attribute("href") == None or \
                        i.get_attribute("href").split("#")[0] == page_new :
                        continue
                    else :
                        url.append(i.get_attribute("href")) 
                except:
                    continue
            # 判断是否有url带php或html
            link_res = []
            for i in url:
                if config.domain in i and ( "html" in i or "php" in i) :
                    link_res.append(i)
                # else:
                #     self.driver.get(i)
                #     if self.driver.title == "404 Not Found": 
                #         link_res = False
                #         break

            if link_res == []:
                link_res = True

            # 对比截图
            layout_res = self.check_layout(page_no)
            
            # Write result into csv
            res = [page_no, page_old, page_new, title_res, description_res, kewords_res, alt_res, link_res, layout_res]
            return res

        except:
            return [page_old, page_new, "Error"]


    # 关闭selenium并删除临时文件
    def quit (self):
        self.driver.quit()
    

    # 将结果写入csv文件
    def save(self, res):
        self.csv_write.writerow_csv(res)