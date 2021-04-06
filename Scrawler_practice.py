import requests


# robots协议：网站维护人员对于资源爬取的规范
# User-agent: *
# Disallow:???


def scrawl_framework(url):
    try:
        headers = {"User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3"
                                 "6 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
        html = requests.get(url, headers=headers, timeout=30)
        html.raise_for_status()                        # 如果返回状态码不是200，则引起HttpError异常
        html.encoding = html.apparent_encoding         # 大部分时间中，apparent_encoding预测的编码要比encoding更准一些
        return html.text
    except:
        return "产生异常"


def scrawl_picture(url, path:str):
    try:
        headers = {"User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.3"
                                 "6 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"}
        html = requests.get(url, headers=headers, timeout=30)
        html.raise_for_status()                        # 如果返回状态码不是200，则引起HttpError异常
        html.encoding = html.apparent_encoding         # 大部分时间中，apparent_encoding预测的编码要比encoding更准一些
        with open(path, "wb") as f:
            f.write(html.content)                      # r.content表示返回内容的二进制形式
        f.close()
        return html.text
    except:
        return "产生异常"


def search_engine(url, params):
    # 直接在搜索引擎中获取信息（不包含处理）
    html = requests.get(url=url, params=params)
    print(html.request.url)
    print(len(html.text))

if __name__ == "__main__":
    params = {
        "wd": "python"
    }
    path = "D:/abc.jpg"     # 图片存取路径
    url = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Ftr-osdcp.qunarzz.com%2Ftr-osd-tr-space%2Fimg%2F2a42e" \
          "d8896045bf1c46a96b53ef1c1b2.jpg_r_720x480x95_b5bbe8b7.jpg&refer=http%3A%2F%2Ftr-osdcp.qunarzz.com&app=2002" \
          "&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1619612631&t=a354397fa58b30422c452d9ee364c9a6"
    scrawl_picture(url, path)
    # search_engine(url, params)















