#coding:utf-8
import os

from utils import *

import xml.etree.cElementTree as ET



def place_xml_parse(place_xml_path, city_code = 'cityNews'):

    news_list = [] ##[(news_id, news_content)]
    etree = ET.parse(place_xml_path)
    root = etree.getroot()
    node_list = root.find('Total').getchildren()

    news_raw_id = 0
    for news_info in node_list:
        title = news_info.find('title').text
        content = news_info.find('news_content').text
        if content:
            all_content = title + ' ' + content
        else:
            all_content = title + ' ' + title
        #从路径中获得新闻事件
        news_date_string = place_xml_path.split('/')[-1].replace('.xml', '')
        newsID = city_code + news_date_string.replace('-', '') + str(news_raw_id).zfill(3)
        news_raw_id += 1

        news_list.append((newsID, all_content))
    return news_list

def news_list_wordcut(news_list, stop_word_dict={}):
    '''
    对输入的新闻列表进行切词，输入形式为[(news_id, news_content)]
    :param news_list: 新闻list, 其格式为[(news_id, news_content)]
    :param stop_word_dict: 停用词列表，默认为空
    :return: 切词之后的新闻list：[(news_id, news_content)]
    '''

    news_list_withou_stops = []

    for news_tuple in news_list:
        news_id = news_tuple[0]
        news_content = news_tuple[1]
        news_content = word_cut_remove_stopwords(news_content, stop_word_dict, word_max=5000)
        news_list_withou_stops.append((news_id, news_content))
    return news_list_withou_stops

def get_period_news_list(start_time, end_time, city_tuple, base_path, path_encoding = 'gbk'):
    all_news = []
    city_code = 'cityNews'
    date_list = generate_date_list(start_time, end_time)
    for date_string in date_list:
        place_xml_path = (u'%s/%s/%s/%s.xml'%(base_path,city_tuple[0],city_tuple[1],date_string)).encode(path_encoding)
        if not os.path.exists(place_xml_path):
            print 'no file! %s'%place_xml_path.decode(path_encoding).encode('utf-8')
            continue

        if len(city_tuple) == 3:
            city_code = city_tuple[2]
        try:
            news_list = place_xml_parse(place_xml_path, city_code='cityNews')
        except:
            news_list = []
            print 'Error parse xml: %s' %place_xml_path.decode(path_encoding).encode('utf-8')
        all_news += news_list
    return all_news


    # print end_time

def prepare_palce_data(start_time, end_time, city_tuple, base_path, stopword_path, path_encoding = 'gbk'):

    all_news = get_period_news_list(start_time, end_time, city_tuple, base_path, path_encoding)
    stopword = get_stop_word_dict(stopword_path)

    all_news = news_list_wordcut(all_news, stop_word_dict={})

    return all_news

def get_day_news_count(date_string, city_tuple_list, base_path, path_encoding = 'gbk'):
    '''
    得到一个城市某天的新闻数量
    :param date_string:日期
    :param city_tuple_list:[(u'河北',u'石家庄')]
    :param base_path:每日数据存储路径
    :param path_encoding:路径编码（windows为gbk，linux为utf-8）
    :return:{city:news_count}#city编码为unicode
    '''
    city_news_count_dict = {}
    for city_tuple in city_tuple_list:
        place_xml_path = (u'%s/%s/%s/%s.xml'%(base_path,city_tuple[0],city_tuple[1],date_string)).encode(path_encoding)

        if not os.path.exists(place_xml_path):
            print 'no file! %s'%place_xml_path
            news_list = []
        else:
            try:
                news_list = place_xml_parse(place_xml_path)
            except:
                news_list = []
        news_count = len(news_list)
        city_news_count_dict[city_tuple[1]] = news_count
    return city_news_count_dict

if __name__ == '__main__':
    place_xml_path = u'./data/news_day_xml/北京/北京/2016-05-25.xml'.encode('gbk')
    base_path = u'./data/news_day_xml/'
    print 'a'

    news_list = place_xml_parse(place_xml_path, city_code='cityNews')
    # print news_list_wordcut(news_list, stop_word_dict={})

    # print get_period_news_list('2016-01-01', '2016-10-05', (u'北京', u'北京', 'beijing'), base_path)
    print prepare_palce_data('2016-10-01', '2016-10-05', (u'北京', u'北京', 'beijing'), base_path, '')

