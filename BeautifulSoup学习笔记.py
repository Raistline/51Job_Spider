import requests
from bs4 import BeautifulSoup
import importlib
import sys;
importlib.reload(sys);

"""
                                      爬虫学习笔记 
  BeautifulSoup将复杂的HTMl文档转换成一个复杂的树形结构，每个节点都是Python对象，所有对象可以归为以下四种：
  ·Tag
  ·NavigableString
  ·BeautifulSoup
  ·Comment

  ①Tag
  Tag是 HTML 中的一个一个标签加上里面包括的内容，如：
  <title>The Dormouse's story</title>
  可以通过soup.<标签名称>来获取Tag
  注：这一方式返回的是所有内容中第一个符合要求的标签！

  对于 Tag 而言，有两个重要的属性，是name和attrs。name表示标签本身的名称，attrs表示标签的全部属性。
  还可以通过直接声明的方式对属性和内容进行修改，甚至可以对这个属性进行删除
  del soup.p['class']

  ②NavigableString
  获取标签内的内容，用.string即可
  print(soup.p.string)

  ③BeautifulSoup
  BeautifulSoup 对象表示的是一个文档的全部内容。大部分时候，可以把它当作 Tag 对象，是一个特殊的 Tag，我们可以分别获取它的类型，名称，以及属性来感受一下
  print(type(soup.name))
  print(soup.name)
  print(soup.attrs)

  ④Comment树
  Comment 对象是一个特殊类型的 NavigableString 对象，其实输出的内容仍然不包括注释符号
  但是如果不好好处理它，可能会对我们的文本处理造成意想不到的麻烦。 我们找一个带注释的标签
  print soup.a
  print soup.a.string
  print type(soup.a.string)
  运行结果如下：
  <a class="sister" href="http://example.com/elsie" id="link1"><!-- Elsie --></a>
  Elsie 
  <class 'bs4.element.Comment'>

  a 标签里的内容实际上是注释，但是如果我们利用 .string 来输出它的内容，我们发现它已经把注释符号去掉了，所以这可能会给我们带来不必要的麻烦。
  另外我们打印输出下它的类型，发现它是一个 Comment 类型，所以，我们在使用前最好做一下判断，判断代码如下：
  if type(soup.a.string)==bs4.element.Comment:
      print soup.a.string

"""
# 如何遍历文档树
"""
对于文档树，如果希望遍历节点，一般采用如下代码：
for each in html.(所希望得到的节点列表):
    *自定义操作

# ①直接子节点
# Tag 的contents属性，查看
   print(soup.head.contents[0])
# .contents方法：输出head标签的全部子节点，输出数据格式为列表，可以用列表索引获取其中某一个元素
# Tag 的children属性，将tag的子节点以列表的方式输出
   print(soup.head.children)
# 为了获取其中的内容，可以用for循环遍历其中内容：
   for child in  soup.body.children:
       print(child)
# ②所有子孙节点
# Tag 的descendants属性，查看
   for child in soup.descendants:
       print(child)
# ③节点内容
# Tag 的.string属性
# 如果 tag 只有一个 NavigableString 类型子节点，那么这个 tag 可以使用 .string 得到子节点。
# 如果一个 tag 仅有一个子节点，那么这个 tag 也可以使用 .string 方法，输出结果与当前唯一子节点的 .string 结果相同。
# 通俗点说就是：如果一个标签里面没有标签了，那么 .string 就会返回标签里面的内容。如果标签里面只有唯一的一个标签了，那么 .string 也会返回最里面的内容。

# 如果 tag 包含了多个子节点，tag 就无法确定，string 方法应该调用哪个子节点的内容，.string 的输出结果是 None
# ④多个内容
# .stripped_strings使用可以去除遍历得到的多余的空白内容
# ⑤父节点
# .parent属性：可以递归得到元素的所有父辈节点
# ⑥全部父节点
# 对.parent属性进行递归可以得到元素的全部父辈节点
# ⑦平行子节点
# .next_sibling      返回按照HTML文本顺序的下一个平行节点标签
# .next_siblings     迭代类型，返回按照HTMl文本顺序的后续所有平行节点标签
# .previous_sibling  返回按照HTML文本顺序的上一个平行节点标签
# .previous_siblings 迭代类型，返回按照HTML文本顺序的前续的所有平行节点标签
"""
"""
                                     信息标记的三种形式
XML:用尖括号和标签标记信息的表达形式
（最早的通用信息标记语言，相当繁琐）（应用：网络上的信息交互与传递）
JSON:有类型的键值对
（信息有类型，适合程序处理，较为简洁）（应用：移动应用云端和节点的信息通信，无注释）
YAML:无类型键值对（键值对套键值对，利用缩进表达所属关系，利用-号表达并列关系，利用|表达整块数据）
（文本信息比例最高，可读性好）（应用：各类系统的配置文件，有注释易读）
"""
"""
                                      信息提取的一般方法
方法一：完整解析信息的标记形式，再提取关键信息，一般需要标记解析器，例如：bs4库的标签树遍历
    优点：信息解析准确
    缺点：提取过程繁琐，速度慢
方法二：无视标记形式，直接搜索关键信息
    优点：提取过程简洁，速度较快
    缺点：提取结果准确性与信息内容直接相关

"""
def get_movies():
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.90 Safari/537.36 ",
        'Host': 'movie.douban.com'
    }
    # 这 里 的User‐Agent和Host要 根 据 自 己 的 浏 览 器 和 目 标 网 站 进 行 修 改
    movie_list = []
    for i in range(0, 10):
        link = 'https://movie.douban.com/top250?start=' + str(i * 25)
        print(link)
        html = requests.get(link, headers=headers, timeout=10)
        html.raise_for_status()                                 # 如果状态码不是200，则引起一个HTTPError异常
        print(str(i + 1), "页 响 应 状 态 码:", html.status_code)  # 发起requests请求后，网页会出现一个返回码，用于标识请求完成情况
        soup = BeautifulSoup(html.text, "lxml")
        div_list = soup.find_all('div', class_='pic')           # 这里是查找标签div中，标签的class属性为hd的那一部分
        for each in div_list:
            try:                                                # 查看源码，然后自定义筛选独一无二的特征，可以是某个标签的属性值，也可以是tag的内容，都可以实现
                movie = each.img['alt'].strip()
            except:
                continue
            movie_list.append(movie)
    return movie_list



def practice():
    url = "https://movie.douban.com/top250?start=0"
    movie_list = []
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.90 Safari/537.36 ",
        'Host': 'movie.douban.com'
    }
    html = requests.get(url, headers=headers, timeout=10)
    print(str(1), "页 响 应 状 态 码:", html.status_code)
    soup = BeautifulSoup(html.text, "lxml")
    div_list = soup.find_all('div', class_='hd')
    for each in div_list:
        movie = each.a.span.text.strip()
        movie_list.append(movie)
    print(movie_list)

    # html = html.text
    # print(html)


# repr()方法将对象外层用双引号包起来
# eval()方法将数字对象的外层引号去掉，返回值是int或者float
if __name__ == '__main__':

    get_movies()
    print(get_movies())
    # practice()

    """
    html = '
    <html><head><title>The Dormouse's story</title></head>
    <body>
    <p class="title" name="dromouse"><b>The Dormouse's story</b></p>
    <p class="story">Once upon a time there were three little sisters; and their names were
    <a href="http://example.com/elsie" class="sister" id="link1"><!-- Elsie --></a>,
    <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
    <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
    and they lived at the bottom of a well.</p>
    <p class="story">...</p>'
    
    soup = BeautifulSoup(html)     # 将爬取下来得到的网站进行数据处理
    # soup = BeautifulSoup(open('index.html'))
    # 上面是利用本地HTMl文件进行创建对象的代码
    for child in soup.descendants:
        print(child)
    
    print(soup.prettify())         # 打印得到该html的内容

    # 以下为几个简单的浏览结构化数据的方法：
    print(soup.title)
    # <title>The Dormouse's story</title>

    print(soup.title.name)
    # 'title'

    print(soup.title.string)
    # 'The Dormouse's story'

    print(soup.title.parent.name)
    # 'head'

    print(soup.p)
    # <p class="title"><b>The Dormouse's story</b></p>

    print(soup.p['class'])       # 单独获取Tag的属性“class”
    # 'title'

    # 上述代码也可以通过get方法实现：
    print(soup.p.get('class'))

    print(soup.a)
    # <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>

    print(soup.find_all('a'))
    # [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
    #  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
    #  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

    print(soup.find(id='link3'))
    # <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>

    del(soup.p['class'])           # 删除Tag的class属性
    
"""






