from selenium import webdriver
import json                               # 对于json字符串的处理
import re                                 # 正则表达式的运用，本例中没有用到
import time
import os
import csv
import logging
from pprint import pprint
from collections import Counter
import selenium
import requests
import jieba
import pymysql
from gevent.pool import Pool
from queue import Queue
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import chardet                     # 判断编码类型
import matplotlib
import matplotlib.pyplot as plt


POOL_MAXSIZE = 8  # 线程池最大容量
LOG_LEVEL = logging.INFO    # 日志等级
# 爬取网站url
O_URL = "https://jobs.51job.com/"

# 爬取数据总量设定
NUM_OF_DATA = 3300         # 至少爬取100条数据
# 计算爬取页数
N_PAGE = int(NUM_OF_DATA/50) - 1
# 输入爬取关键字
KEY_WORDS = 'Python'
# 网页头
HEADERS = {                # requests请求头
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5'
                  '37.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
}


def get_logger():
    """
    创建日志实例
    """
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    logger = logging.getLogger("monitor")
    logger.setLevel(LOG_LEVEL)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def ranging(item: float, a: float, b: float):         # 判断工资范围函数
    if (item > a) & (item <= b):
        return True
    else:
        return False


logger = get_logger()


class JobSpider:

    def __init__(self):
        self.count = 1                                                               # 记录当前爬第几条数据
        self.company = []
        self.desc_url_queue = Queue()                                                # 线程池队列
        self.pool = Pool(POOL_MAXSIZE)                                               # 线程池管理线程,最大协程数

    def job_spider(self, n_page: int, key_words: str):
        """爬虫入口"""
        driver = webdriver.Chrome()                                                  # 使用webdriver启动chrome浏览器
        driver.get(O_URL)                                                            # 模拟浏览器打开网页
        driver.find_element_by_xpath('//*[@id="kwdselectid"]').clear()               # 清空输入框
        driver.find_element_by_xpath('//*[@id="kwdselectid"]').send_keys(key_words)  # 在输入框内输入关键字
        driver.find_element_by_xpath('//*[@id="searchForm"]/button').click()         # 点击确认，进入搜索结果页面
        time.sleep(1.2)                                                              # 休息1.2秒，等待浏览器渲染
        for i in range(n_page):                                                      # 开始对每一页进行爬取
            logger.info("爬取第 {} 页".format(i + 1))
            a = driver.find_elements_by_class_name('e')                              # find_elements方法返回一个列表，元素是标签值为e的标签
            for b in a:                                                              # 对a进行迭代
                try:
                    location = b.find_elements_by_class_name('d')                    # 后面四行代码分别爬取工作地点，工作名称，薪资水平和内容网页链接
                    job_name = b.find_elements_by_class_name('at')[0]
                    salary = b.find_elements_by_class_name('sal')[0]
                    href = b.find_elements_by_tag_name('a')[0].get_attribute('href')
                    item = {                                                         # 将其存为json字典格式
                        'locate': [location1.text for location1 in location],
                        'post': job_name.text,
                        'salary': salary.text,
                        'href': href
                    }
                    self.desc_url_queue.put(href)                                    # 这里有可能并不能清洗掉无用数据，代码写完后需要运行查看一下
                    self.company.append(item)
                    print(job_name.text)
                    print(salary.text)
                    print([location1.text for location1 in location])
                    print(href)
                except selenium.common.exceptions.NoSuchElementException as e:       # 如果classname发生变动，这里就会报错
                    print(e)
                finally:
                    continue
            if i <= 5:                                                               # 这里的if判断语句起到点击下一页的作用
                driver.find_element_by_xpath(
                    "/html/body/div[2]/div[3]/div/div[2]/div[4]/div[2]/div/div/div/ul/li[{}]/a".format(
                        str(i + 3))).click()
                time.sleep(1.0)
            else:
                driver.find_element_by_xpath(
                    "/html/body/div[2]/div[3]/div/div[2]/div[4]/div[2]/div/div/div/ul/li[8]/a").click()
                time.sleep(1.0)                                                       # 点击之后等待浏览器渲染
            # 点击下一页，重复爬取信息
        # 打印队列长度,即多少条岗位详情 url
        logger.info("队列长度为 {} ".format(self.desc_url_queue.qsize()))               # 打印日志

    def post_require(self):
        """
        爬取职位描述
        """
        while True:                                            # 当队列不为空
            # 从队列中取 url
            try:
                URL_URL = self.desc_url_queue.get(block=False, timeout=30)            # block设置为false防止出现阻塞
                resp = requests.get(url=URL_URL, headers=HEADERS)
            except Exception as e:
                logger.error(e)
                logger.warning(URL_URL)
                self.desc_url_queue.task_done()
                continue
            if resp.status_code == 200:                                               # 判断网页返回状态码是否正常
                logger.info("爬取第 {} 条岗位详情".format(self.count))
                encoding_dict = chardet.detect(resp.content)
                web_encoding = encoding_dict['encoding']
                if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
                    html = resp
                else:
                    html = resp.content.decode('gbk')
                self.desc_url_queue.task_done()
                self.count += 1
            else:
                self.desc_url_queue.task_done()                                       # 如果不正常，则将网址重新放回队列，等待后续重新访问
                continue
            try:
                bs = BeautifulSoup(html, "lxml").find(
                    "div", class_="bmsg job_msg inbox"
                ).text
                s = bs.replace("微信", "").replace("分享", "").replace("邮件", "").replace(
                    "\t", "").replace('\xa0', '').strip()                         # 进行内容预清洗
                with open(
                        os.path.join("data", "post_require.txt"), "a", newline='', encoding="utf-8"
                ) as f:
                    f.write(s)                                                        # 将爬到的内容写入post_require文件
                print(s)
            except Exception as e:
                logger.error(e)
                logger.warning(URL_URL)

    @staticmethod
    def post_desc_counter():
        """
        职位描述统计
        """
        # import thulac
        post = open(
            os.path.join("data", "post_require.txt"), "r", encoding="utf-8"
        ).read()
        # 使用 thulac 分词
        # thu = thulac.thulac(seg_only=True)
        # thu.cut(post, text=True)
        bd = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+，。！？“”《》：、． 的和1234567890以上与够至少具根据及并等和有（）；~¥者一定能有对中如一种'
        # bd清洗无用词汇
        post = post.replace('\n', '')
        for i in bd:
            post = post.replace(i, '')
        # 使用 jie ba 分词
        file_path = os.path.join("data", "user_dict.txt")
        jieba.load_userdict(file_path)
        seg_list = jieba.cut(post, cut_all=False)
        counter = dict()
        for seg in seg_list:
            counter[seg] = counter.get(seg, 1) + 1
        counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)
        # pprint(counter_sort)
        with open(
                os.path.join("data", "post_pre_desc_counter.csv"), "w+", newline='', encoding="utf-8"
        ) as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_sort)

    def post_counter(self):
        """
        职位统计
        """
        lst = [c.get("post") for c in self.company]
        counter = Counter(lst)
        counter_most = counter.most_common()
        pprint(counter_most)
        with open(
                os.path.join("data", "post_pre_counter.csv"), "w+", newline='',  encoding="utf-8"
        ) as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter_most)

    def post_salary_locate(self):
        """
        招聘大概信息，职位，薪酬以及工作地点
        """
        lst = []
        for c in self.company:
            lst.append((c.get("salary"), c.get("post"), c.get("locate")[-1].strip()))
        pprint(lst)
        with open(
                os.path.join("data", "post_salary_locate.csv"), "w+", newline='', encoding="utf-8"
        ) as f:
            f_csv = csv.writer(f)
            f_csv.writerows(lst)

    @staticmethod
    def post_salary():
        """
        薪酬统一处理
        """
        mouth = []
        year = []
        thousand = []
        with open(
                os.path.join("data", "post_salary_locate.csv"), "r", encoding="utf-8"
        ) as f:
            f_csv = csv.reader(f)
            print(f_csv)
            for row in f_csv:
                if row:
                    if "万/月" in row[0]:
                        mouth.append((row[0][:-3], row[2], row[1]))
                    elif "万/年" in row[0]:
                        year.append((row[0][:-3], row[2], row[1]))
                    elif "千/月" in row[0]:
                        thousand.append((row[0][:-3], row[2], row[1]))
                else:
                    continue
        pprint(mouth)

        calc = []
        for m in mouth:
            s = m[0].split("-")
            calc.append(
                (round((float(s[1]) - float(s[0])) * 0.4 + float(s[0]), 1), m[1], m[2])
            )
        for y in year:
            s = y[0].split("-")
            calc.append(
                (
                    round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 12, 1),
                    y[1],
                    y[2],
                )
            )
        for t in thousand:
            s = t[0].split("-")
            calc.append(
                (
                    round(((float(s[1]) - float(s[0])) * 0.4 + float(s[0])) / 10, 1),
                    t[1],
                    t[2],
                )
            )
        pprint(calc)
        with open(os.path.join("data", "post_salary.csv"), "w+", newline='', encoding="utf-8") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(calc)

    @staticmethod
    def post_salary_counter():
        """
        薪酬统计
        """
        with open(os.path.join("data", "post_salary.csv"), "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            lst = [row[0] for row in f_csv]
        counter = Counter(lst).most_common()
        pprint(counter)
        with open(
                os.path.join("data", "post_salary_counter1.csv"), "w+", newline='', encoding="utf-8"
        ) as f:
            f_csv = csv.writer(f)
            f_csv.writerows(counter)

    @staticmethod
    def world_cloud():
        """
        生成词云
        """
        counter = {}
        with open(
                os.path.join("data", "post_pre_desc_counter.csv"), "r", encoding="utf-8"
        ) as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                counter[row[0]] = counter.get(row[0], int(row[1]))
            # pprint(counter)
        file_path = os.path.join("font", "msyh.ttf")
        wc = WordCloud(
            font_path=file_path, max_words=100, height=600, width=1200
        ).generate_from_frequencies(
            counter
        )
        plt.switch_backend('agg')
        plt.imshow(wc)
        plt.axis("off")
        plt.show()
        wc.to_file(os.path.join("images", "word_cloud.jpg"))

    @staticmethod
    def pie_of_salary():
        """
        生成工资饼状图
        """
        colors = ['c', 'y', 'r', 'gray', 'g']
        salary = [0, 0, 0, 0, 0]
        with open(
                os.path.join("data", "post_salary_counter1.csv"), "r", encoding="utf-8"
        ) as f:
            f_csv = csv.reader(f)
            for item in f_csv:
                if ranging(item=float(item[0]), a=0, b=1.0):
                    salary[0] = salary[0]+int(item[1])
                elif ranging(item=float(item[0]), a=1.0, b=1.5):
                    salary[1] = salary[1] + int(item[1])
                elif ranging(item=float(item[0]), a=1.5, b=2.0):
                    salary[2] = salary[2] + int(item[1])
                elif ranging(item=float(item[0]), a=2.0, b=2.5):
                    salary[3] = salary[3] + int(item[1])
                elif ranging(item=float(item[0]), a=2.5, b=100):
                    salary[4] = salary[4] + int(item[1])
        plt.rcParams['font.sans-serif'] = 'SimHei'
        plt.figure(figsize=(8, 6))
        label = ['[0,1.0]万/月:{}'.format(salary[0]), '[1.1,1.5]万/月:{}'.format(salary[1]), '[1.6,2.0]万/月:{}'.format(salary[2]), '[2.1,2.5]万/月:{}'.format(salary[3]), '>2.5万/月:{}'.format(salary[4])]
        explode = [0.01, 0.01, 0.01, 0.01, 0.01]
        plt.pie(salary, explode=explode, labels=label, autopct='%1.1f%%', radius=1, pctdistance=0.85, colors=colors,
                startangle=180, wedgeprops={'width': 0.3, 'edgecolor': 'w'})
        # plt.xticks(rotation=45)
        # plt.xlabel('工资/月')
        # plt.ylabel('人数')
        # plt.grid(alpha=0.4)
        plt.title('工资范围分布')
        # plt.legend(loc='upper left')
        # for x1, y1 in zip(label, salary):
        #     plt.text(x1, y1 + 1, str(y1), ha='center', va='bottom', fontsize=20, rotation=0)
        plt.savefig(os.path.join('images', "pie_of_salary.jpg"))
        plt.show()

    @staticmethod
    def histogram_of_post():
        matplotlib.rc('font', family='SimHei', weight='bold')
        plt.rcParams['axes.unicode_minus'] = False
        colors = ['red', 'yellow', 'blue', 'green', 'gray']
        post_list = []
        post_number = []
        font = {'family': 'simhei',
                'weight': 'normal',
                'size': 18}
        with open(os.path.join('data', 'post_pre_counter.csv'), 'r', encoding='utf-8') as f:
            histogram = csv.reader(f)
            for rows in histogram:
                # print(rows)
                if int(rows[1]) >= 20:
                    post_list.append(rows[0])
                    post_number.append(rows[1])
                    print(rows)
        post_number.reverse()
        post_list.reverse()
        f, ax = plt.subplots(figsize=(15, 6))
        barh = plt.barh(post_list, post_number, color=colors)
        barh[-1].set_color('green')
        for y, x in enumerate(post_number):
            plt.text(x, y-0.2, '%s' % x)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # axes = plt.gca()
        # axes.set_xlim([0, 56])
        plt.tick_params(labelsize=10)
        plt.xlabel('人数分布', font=font)
        plt.ylabel('职位分布', font=font)
        # 尝试画水平柱状分布图
        # plt.barh(range(len(post_number)), post_number, tick_label=post_list, color=colors)
    # b = ax.barh(range(len(post_list)), post_number, color=['r', 'b', 'y', 'green'], alpha=0.9, tick_label=post_list)
        plt.title('Histogram_Of_Post Figure', loc='center', fontsize='25',
                  fontweight='bold', color='red')
        plt.savefig(os.path.join('images', "Histogram_of_Post.jpg"))
        plt.show()

    @staticmethod
    def insert_into_db():
        """
        插入数据到数据库
        create table jobpost(
            j_salary float(3, 1),
            j_locate text,
            j_post text
        );
        """
        conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            passwd="0303",
            db="chenx",
            charset="utf8",
        )
        cur = conn.cursor()
        with open(os.path.join("data", "post_salary.csv"), "r", encoding="utf-8") as f:
            f_csv = csv.reader(f)
            sql = "insert into jobpost(j_salary, j_locate, j_post) values(%s, %s, %s)"
            for row in f_csv:
                value = (row[0], row[1], row[2])
                try:
                    cur.execute(sql, value)
                    conn.commit()
                except Exception as e:
                    logger.error(e)
        cur.close()

    def execute_more_tasks(self, target):
        """
        协程池接收请求任务,可以扩展把解析,存储耗时操作加入各自队列,效率最大化
        :param target: 任务函数
        :param count: 启动线程数量
        """
        for i in range(POOL_MAXSIZE):
            self.pool.apply_async(target)
        self.pool.join()

    def run(self):
        """
        多线程爬取数据
        """
        self.job_spider(n_page=N_PAGE, key_words=KEY_WORDS)
        self.execute_more_tasks(self.post_require)
        self.desc_url_queue.join()  # 主线程阻塞,等待队列清空


if __name__ == "__main__":
    spider = JobSpider()
    start = time.time()
    # spider.run()
    logger.info("总耗时 {} 秒".format(time.time() - start))
    # 按需启动
    # spider.post_counter()
    # spider.post_salary_locate()
    # spider.post_salary()
    # # # spider.insert_into_db()
    # spider.post_salary_counter()
    # spider.post_desc_counter()
    # spider.world_cloud()
    # spider.pie_of_salary()                          # 绘制工资-人数折线图
    spider.histogram_of_post()
