from datetime import datetime
import os

from wordcloud import WordCloud
# doc: https://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba
import pandas as pd

import windrecorder.utils as utils
from windrecorder.dbManager import dbManager
import windrecorder.files as files



# 读取跳过词
def read_stopwords(filename):
    stopwords = []
    with open(filename, 'r', encoding='utf-8') as file:
        stopwords = file.read().split(',')
        stopwords = [word.strip() for word in stopwords]
    return stopwords


stopwords = read_stopwords("config/wordcloud_stopword.txt")


# 生成词云
def generate_word_cloud_pic(text_file_path,img_save_path):
    # 打开文本
    # with open(text_file_path,encoding="utf-8") as f:
    #     s = f.read()
    with open(text_file_path) as f:
        s = f.read()

    # 中文分词
    text = ' '.join(jieba.cut(s))

    # 生成对象
    img = Image.open("__assets__/mask_cloud.png") # 打开遮罩图片
    mask = np.array(img) #将图片转换为数组

    wc = WordCloud(font_path="msyh.ttc",
                   mask=mask,
                   width = 1000,
                   height = 800,
                   min_font_size = 8,
                   max_font_size = 150,
                   mode="RGBA",
                   background_color=None,
                   max_words=300,
                   stopwords=stopwords,
                   min_word_length=2,
                   relative_scaling=0.4,
                   repeat=False
                   ).generate(text)

    # 显示词云
    plt.imshow(wc, interpolation='bilinear')# 用plt显示图片
    plt.axis("off")  # 不显示坐标轴
    plt.show() # 显示图片

    # 保存到文件
    wc.to_file(img_save_path)


# 获取某个时间戳下当月的所有识别内容
def get_month_ocr_result(timestamp):
    timestamp_datetime = utils.seconds_to_datetime(timestamp)
    #查询当月所有识别到的数据，存储在文本中
    date_in = datetime(timestamp_datetime.year,
                       timestamp_datetime.month,
                       1,
                       0,0,1)
    date_out = datetime(timestamp_datetime.year,
                       timestamp_datetime.month,
                       utils.get_days_in_month(timestamp_datetime.year,timestamp_datetime.month),
                       23,59,59)
    df,_,_ = dbManager.db_search_data("",date_in,date_out,0,is_p_index_used=False)
    # ocr_text_data = df["ocr_text"].to_string(index=False)
    ocr_text_data = ''.join(df['ocr_text'].tolist())
    ocr_text_data = utils.delete_short_lines(ocr_text_data,less_than=10)

    # 移除换行符
    ocr_text_data = ocr_text_data.replace("\n", "").replace("\r", "")
    # 输出到文件
    files.check_and_create_folder("catch")
    text_file_path = "catch/get_month_ocr_result_out.txt"
    with open(text_file_path, "w") as file:
        file.write(ocr_text_data)
    return text_file_path

    # 以csv列输出
    # output_file = "catch/out.txt"
    # ocr_text_data.to_csv(output_file, index=False, header=False, sep="\t")

  
# 根据某时数据生成该月的词云
def generate_word_cloud_in_month(timestamp,img_save_name="default"):
    # 取得当月内所有ocr结果
    text_file_path = get_month_ocr_result(timestamp)

    img_save_dir = "wordcloud_result"
    files.check_and_create_folder(img_save_dir)
    img_save_name = img_save_name + ".png"
    img_save_path = os.path.join(img_save_dir,img_save_name)

    # 生成词云图片
    generate_word_cloud_pic(text_file_path,img_save_path)


