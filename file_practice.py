import os

with open('fuck_OFF.txt', 'a', encoding='gbk') as f:
    for i in range(1000000):
        f.write('我真棒棒！')
        f.write("那必须的！\n")
        f.write("也不行也不行。")
    # write方法不会在结尾加换行符，需要手动添加
