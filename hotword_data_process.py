#coding:utf-8
import os, csv, sys, datetime

from utils import *

from gensim.models import doc2vec
from collections import namedtuple
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier

import xml.etree.cElementTree as ET
import jieba.posseg as pseg
import jieba

risk_label_dict = {'国家安全':'1','金融经济':'2','精神文明':'3','日常生活':'4','社会稳定':'5','政府执政':'6','资源环境':'7','无风险':'8',}

def hotword_risk_xml_parse(risk_xml_path):
    '''
    读取riskxml中的数据，返回数据：{id:(keyword, label)}
    :param risk_xml_path: xml文件路径
    :return: {id:(keyword, label), }
    '''
    hotword_dict = {}

    etree = ET.parse(risk_xml_path)
    root = etree.getroot()
    hotword_list = root.find('Total').getchildren()


    for hotword_item in hotword_list:
        keyword = hotword_item.find('keyword').text.strip()
        risk_label = risk_label_dict[hotword_item.find('bigrisk').text.strip().encode('utf-8')]
        hotword_id = hotword_item.find('id').text.strip()
        hotword_dict[hotword_id] = (keyword, risk_label)

    return  hotword_dict

def newsxml_content_parse(news_xml_path):
    '''
    读取newsxml/0.xml文件，返回所有的新闻list
    :param news_xml_path: xml文件的路径
    :return: [(news_id, news_content)]
    '''
    news_list = []

    etree = ET.parse(news_xml_path)
    root = etree.getroot()
    news_node_list = root.getchildren()

    for news_node in news_node_list:
        if not news_node.tag == 'item':
            continue

        news_id = news_node.find('id').text
        # 对新闻正文进行提取+拼接
        news_title = news_node.find('title').text.strip()
        if news_node.find('txt').text:
            news_txt = news_node.find('txt').text.strip()
        else:
            news_txt = news_title
        all_content = news_title + ' ' + news_txt
        news_list.append((news_id, all_content))
        # print news_id, all_content
    return news_list

def get_oneday_labeled_news(date_string, risk_basepath, news_xml_basepath, ):
    '''
    获取一天内的所有的新闻正文，并赋予风险类别，新闻ID拼接：hotword2016103101001，时间，热搜词编号（2位），新闻编号（3位），其中
    新闻正文 = 热搜词*3 + 新闻标题 + 新闻正文
    :param date_string: 日期字符串，2016-10-31
    :param risk_basepath: riskdata文件夹路径
    :param news_xml_basepath: newsxml文件夹路径
    :return: [(news_id, news_label, newscontent)]
    '''

    labeled_news_list = []

    risk_xml_path = '%s/%s.xml'%(risk_basepath,date_string)
    if not os.path.exists(risk_xml_path):
        print 'no file! : %s' %risk_xml_path
        return labeled_news_list
    hotword_dict = hotword_risk_xml_parse(risk_xml_path)

    for hotword_id in hotword_dict:
        # print hotword_id
        news_xml_path = '%s/%s/%s.xml'%(news_xml_basepath, date_string, hotword_id)
        hotword_keyword = hotword_dict[hotword_id][0]
        hotword_label = hotword_dict[hotword_id][1]
        if not os.path.exists(news_xml_path):
            news_id = 'hotword' + date_string.replace('-', '') + str(hotword_id).zfill(2) + '000'
            news_content = (hotword_keyword + ' ')*5
            news_tuple = (news_id, hotword_label, news_content)
            labeled_news_list.append(news_tuple)
            continue

        news_content_list = newsxml_content_parse(news_xml_path)

        for news_content in news_content_list: ###news_content : (news_id, news_title + news_txt)
            ###拼接新闻id
            news_id = 'hotword' + date_string.replace('-', '') + str(hotword_id).zfill(2) + news_content[0].zfill(3)
            ###新闻正文
            news_all_content = (hotword_keyword + ' ') * 3 + news_content[1]

            news_tuple = (news_id, hotword_label, news_all_content)
            labeled_news_list.append(news_tuple)

    return labeled_news_list

def get_period_labeled_news(start_date_string, end_date_string, risk_basepath, news_xml_basepath):
    '''
    获取一段时间内的有标签新闻
    :param start_date_string: 开始时间字符串，2016-10-01
    :param end_date_string: 结束时间字符串, 2016-10-31
    :param risk_basepath: riskdata文件夹路径
    :param news_xml_basepath: newsxml文件夹路径
    :return: [(news_id, news_label, newscontent)]，其中newscontent没有切词的结果
    '''

    date_string_list = generate_date_list(start_date_string, end_date_string)
    all_date_labeled_news = []

    for date_string in date_string_list:
        oneday_labelded_news_list = get_oneday_labeled_news(date_string, risk_basepath, news_xml_basepath, )
        all_date_labeled_news += oneday_labelded_news_list

    return all_date_labeled_news

def prepare_train_data(start_date_string, end_date_string, risk_basepath, news_xml_basepath, stop_word_path):
    '''
    获取一段时间内的新闻数据的切词结果，并去停用词，停用词表不存在的话为不去停词
    :param start_date_string: 开始时间字符串，2016-10-01
    :param end_date_string: 结束时间字符串, 2016-10-31
    :param risk_basepath: riskdata文件夹路径
    :param news_xml_basepath: newsxml文件夹路径
    :param stop_word_path: 停词的文件路径，文件中一行为一个停词
    :return: [(news_id, news_label, newscontent)]，其中newscontent为切词之后结果
    '''
    stop_word_dict = get_stop_word_dict(stop_word_path)
    all_date_labeled_news = get_period_labeled_news(start_date_string, end_date_string, risk_basepath, news_xml_basepath)
    all_cut_word_news = []

    for labeled_news in all_date_labeled_news:
        news_id = labeled_news[0]
        news_label = labeled_news[1]
        news_content = labeled_news[2]
        news_content_cutword = word_cut_remove_stopwords(news_content, stop_word_dict = stop_word_dict)

        all_cut_word_news.append((news_id, news_label, news_content_cutword))
    return all_cut_word_news

def train_vec(model_path, news_cutword_list):

    vec_list = []
    model = doc2vec.Doc2Vec.load(model_path)

    for news_words  in news_cutword_list:
        vec = model.infer_vector(news_words)
        vec_list.append(vec)
    return vec_list

if __name__ == '__main__':
    risk_basepath = './data/baidu_hotword/riskdata/'
    news_xml_basepath = './data/baidu_hotword/newsxml/'
    stop_word_path = ''

    start_date_string = '2016-10-01'
    end_date_string = '2016-10-01'
    id_list, label_list, content_list = zip(* prepare_train_data(start_date_string, end_date_string, risk_basepath, news_xml_basepath, stop_word_path))

    y_list = label_8class_to_2class(label_list)


    model_path = './doc2vec_model/doc2vec.model'

    X_list = train_vec(model_path, content_list)

    print len(X_list)
    ###训练模型
    clf = KNeighborsClassifier(n_neighbors=77)
    clf.fit(X_list, y_list)###训练模型
    pred = clf.predict(X_list)###训练训练集，计算训练集的准确率
    score = metrics.accuracy_score(y_list, pred) ###训练集准确率
    print metrics.classification_report(y_list, pred)
    print score