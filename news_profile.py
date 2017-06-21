#coding:utf-8
import pickle, os, json, types, sys

import jieba.analyse
from gensim.models.ldamodel import LdaModel

import cityNewsXML2json
import utils
import conf
reload(sys)
sys.setdefaultencoding('utf-8')


def news_predict(news_string, model_path = './model'):
    '''
    预测新闻风险类别
    :param news_string:新闻内容，或是列表，只能是String或是list格式
    :return: 新闻风险类别或是新闻
    '''
    # model_path = './model'
    model_type = '2'

    vectorizer = pickle.load(open(model_path + ('/vectorizer.%s.pkl'%model_type), 'r'))
    ch2 = pickle.load(open(model_path + ('/ch2.%s.pkl'%model_type), 'r'))
    clf = pickle.load(open(model_path + ('/model.%s.pkl'%model_type), 'r'))

    if type(news_string) == types.StringType:
        news_list = [news_string]
    elif type(news_string) == types.ListType:
        news_list = news_string
    else:
        print 'False! input type is wrong!'
        return False

    news_list_word_cut = [utils.word_cut_remove_stopwords(news_content) for news_content in news_list]

    news_vector = vectorizer.transform(news_list_word_cut)
    feature_vector = ch2.transform(news_vector)
    news_label =  clf.predict(feature_vector)

    if len(news_label) == 1:
        return news_label[0]
    else:
        return news_label

def newsList_labeled(news_list, model_path = './model'):
    '''
    对news_list中的新闻进行风险标签预测，在原来news_json的基础上增加'risk_label'的值
    :param news_list: 新闻json的列表数据，[{'content':content, 'title':title, 'title':title, 'news_time':2017-04-07 11:34 }]
    :param model_path: 本地保存的分类器文件
    :return: 添加'risk_label'的值之后的新闻List
    '''
    content_list = ['%s %s %s' % (news_object['title'], news_object['title'], news_object['content']) for news_object in news_list]
    label_list = news_predict(content_list, model_path=model_path)
    for i in range(len(label_list)):
        news_list[i]['risk_label'] = label_list[i].encode('utf-8')

    return news_list

def get_keywords(string, topn = 10):
    '''
    根据新闻中文获取新闻中的topn关键词
    :param string: 新闻正文
    :param topn: 前topn个关键词
    :return: 关键词List：[(keyword, weight), (keyword, weight)]
    '''
    string_list = utils.str2List(string)
    keyword_list = list()
    for string in string_list:
        all_keyword_weight = jieba.analyse.textrank(string, withWeight=True, allowPOS=('ns', 'n', 'vn'))
        #最多只保留前n个
        if len(all_keyword_weight) >= topn:
            keyword_weight = [all_keyword_weight[i] for i in range(topn)]
        else:
            keyword_weight = [all_keyword_weight[i] for i in range(len(all_keyword_weight))]
        keyword_list.append(keyword_weight)
    if len(keyword_list) == 1:
        return keyword_list[0]
    else:
        return keyword_list

def newsList_keywords(news_list,topn=10):
    '''
    输入新闻列表json_list，在news_json中添加keyword的值：[(keyword, weight)]
    :param json_list: 新闻json的列表
    :param topn: 前N个关键词
    :return: 包含keword的新闻json
    '''
    for news_json in news_list:
        news_title = news_json['title']
        news_content = news_json['content']
        if not news_content:
            news_content = news_title * 3
        all_content = news_title + news_content
        keyword_list = get_keywords(all_content, topn)

        news_json['keywords'] = keyword_list

    return news_list


def newsList_topicInfer(news_list, model_basepath = './model', reserved_word_path = ''):
    dictionary_path = model_basepath + '/dictionary.pickle'
    fr = file(dictionary_path, 'rb')
    dictionary = pickle.load(fr)
    model_path = model_basepath + '/lda_100.model'
    lda = LdaModel.load(model_path, mmap='r')

    for news_json in news_list:
        news_title = news_json['title']
        news_content = news_json['content']
        if not news_content:
            news_content = news_title * 3
        all_content = news_title + news_content

        word_list = utils.wordcut4lda(all_content, reserved_word_path=reserved_word_path).split()
        topic_vec = [str(key[1]) for key in lda.get_document_topics(dictionary.doc2bow(word_list), minimum_probability=0)]

        news_json['topic'] = topic_vec

def news_profile(news_list, model_basepath, topn = 10, reserved_word_path = '' ):


    #step2:新闻分类
    print 'news num: %d'%len(news_list)
    if len(news_list) == 0:
        return list()
    print '... begain news_label'
    newsList_labeled(news_list, model_basepath)
    #step3:提取关键词
    print '... begain news keyword'
    newsList_keywords(news_list, topn=topn)
    #step3:新闻推断话题
    print '... begain news topic'
    newsList_topicInfer(news_list, model_basepath, reserved_word_path=reserved_word_path)
    print 'news profile done!'

    return news_list

def period_cityTuple_news_profile(city_tuple_list, city_news_basepath, start_date = '2017-04-06', end_date = '2017-04-06',  model_basepath = './model', topn = 10, reserved_word_path = ''):


    cityTuple_newsList = cityNewsXML2json.city_news2json(city_news_basepath, city_tuple_list, start_date = start_date, end_date = end_date)
    for news_list in cityTuple_newsList:
        print '===============开始城市画像=================='
        print 'city: %s'%(city_tuple_list[cityTuple_newsList.index(news_list)][1])
        news_profile(news_list, model_basepath, topn = topn, reserved_word_path = reserved_word_path )

    return cityTuple_newsList

def save_news_profile(city_tuple_list, cityTuple_newsList, date_string,save_basepath, path_encoding='gbk'):
    for i in range(len(city_tuple_list)):
        province = city_tuple_list[i][0]
        city = city_tuple_list[i][1]

        city_path = (u'%s/%s/%s'%(save_basepath, province, city)).encode(path_encoding)
        if not os.path.exists(city_path):
            os.makedirs(city_path)

        news_profile_path = (u'%s/%s/%s/%s.newsProfile'%(save_basepath, province, city, date_string)).encode(path_encoding)

        utils.dumps_news2json(cityTuple_newsList[i], news_profile_path)

def daily_news_profile(cityProfile_tuple_list, city_news_basepath, news_profile_basepath,date_string, reserved_word_path, path_encoding='gbk'):

    cityTuple_newsList = period_cityTuple_news_profile(cityProfile_tuple_list, city_news_basepath, start_date = date_string, end_date = date_string,  model_basepath = './model', topn = 10, reserved_word_path = reserved_word_path)
    save_news_profile(cityProfile_tuple_list, cityTuple_newsList, date_string = date_string,save_basepath =  news_profile_basepath, path_encoding=path_encoding)

if __name__ == '__main__':

    '''
    reserved_word_path = conf.BaseConf.RESERVEDWORD
    #step1:获取新闻list
    # city_tuple_list = [(u'北京',u'北京')]
    city_tuple_list = [(u'重庆',u'重庆')]
    city_news_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_xml/'

    cityTuple_newsList = period_cityTuple_news_profile(city_tuple_list, city_news_basepath, start_date = '2017-06-02', end_date = '2017-06-02',  model_basepath = './model', topn = 10, reserved_word_path = reserved_word_path)

    for news in cityTuple_newsList[0]:
        print news['risk_label'],news['keywords'], news['topic'], news['content']

    save_news_profile(city_tuple_list, cityTuple_newsList, date_string = '2017-06-02',save_basepath=u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_profile/')
    '''
    cityProfile_tuple_list = [(u'北京',u'北京')]
    date_string = '2017-06-16'
    city_news_basepath = u'D:/baiduCityNews/news_day_xml/'
    news_profile_basepath = u'D:/baiduCityNews/news_day_profile/'
    reserved_word_path =  'sys/reservedWord.txt'


    daily_news_profile(cityProfile_tuple_list, city_news_basepath, news_profile_basepath,date_string, reserved_word_path)