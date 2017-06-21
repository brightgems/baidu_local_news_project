#coding:utf-8

import place_data_process
import model
import utils
import pickle
import csv
import os
import json

from hotword_data_process import prepare_train_data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import chi2



#place_news_base_path = u'../running_spider/baidu_spider/spider_v3.2/news_day_xml/'

def get_city_date_label_distribution(train_start_time, train_end_time, period_list, city_tuple_list, place_news_base_path = u'../running_spider/baidu_spider/spider_v3.2/news_day_xml/', path_encoding = 'gbk'):
    '''
    从本地读取hotword的数据，并训练SVM模型，预测每日各城市的新闻的风险标签。
    :param train_start_time:
    :param train_end_time:
    :param period_list: 要预测的不同时间段，（日，周，月）
    :param city_tuple_list:
    :param place_news_base_path:
    :param path_encoding:
    :return:
    '''
    risk_basepath = '../data_sets/baidu_hotword2016/riskdata/'
    news_xml_basepath = '../data_sets/baidu_hotword2016/newsxml/'
    stop_word_path = './sys_data/stopwords.txt'

    train_id_list, train_label_list, train_content_list = zip(*prepare_train_data(train_start_time, train_end_time, risk_basepath, news_xml_basepath, stop_word_path))
    train_label_list = utils.label_8class_to_2class(train_label_list)
    # train_content_list, train_label_list =utils.risk_data_duplicate(train_content_list, train_label_list, times=2)

    vectorizer = TfidfVectorizer(min_df=1, decode_error='ignore', sublinear_tf=True)
    X_train_vectorized = vectorizer.fit_transform(train_content_list)

    feature_percent = 20
    ch2 = SelectPercentile(chi2, percentile=feature_percent)
    X_train_vectorized = ch2.fit_transform(X_train_vectorized, train_label_list)
    # print utils.risk_label_count(train_label_list)

    city_date_lable_count = {} ##{u'北京':{20160916:{'0':28, '1':90}}}
    for city_tuple in city_tuple_list:
        city_name = city_tuple[1]
        date_label_dist = {}
        for period in period_list:
            start_time = period[0]
            end_time = period[-1]

            places_data_list = place_data_process.prepare_palce_data(start_time, end_time, city_tuple, place_news_base_path, stop_word_path, path_encoding)
            if places_data_list:
                place_news_id_list, place_news_content_list = zip(*places_data_list)
                place_news_vectorized_list = vectorizer.transform(place_news_content_list)

                place_news_vectorized_list = ch2.transform(place_news_vectorized_list)

                palce_news_label = model.train_model_pridict(X_train_vectorized, train_label_list, place_news_vectorized_list)
                date_label_dist[start_time] = utils.risk_label_count(palce_news_label)
            else:
                date_label_dist[start_time] = {'0':0, '1':0}
        # print date_label_dist
        city_date_lable_count[city_name] = date_label_dist

    return city_date_lable_count


def get_city_date_label_distribution_v2(model_path, period_list, city_tuple_list, place_news_base_path = u'../running_spider/baidu_spider/spider_v3.2/news_day_xml/', stop_word_path = '', path_encoding = 'gbk'):
    '''
    从本地读取hotword的数据，并训练SVM模型，预测每日各城市的新闻的风险标签。
    :param train_start_time:
    :param train_end_time:
    :param period_list: 要预测的不同时间段，（日，周，月）
    :param city_tuple_list:
    :param place_news_base_path:
    :param path_encoding:
    :return:
    '''

    model_type = '2'
    vectorizer = pickle.load(open(model_path + ('/vectorizer.%s.pkl'%model_type), 'r'))
    ch2 = pickle.load(open(model_path + ('/ch2.%s.pkl'%model_type), 'r'))
    clf = pickle.load(open(model_path + ('/model.%s.pkl'%model_type), 'r'))

    city_date_lable_count = {} ##{u'北京':{20160916:{'0':28, '1':90}}}
    for city_tuple in city_tuple_list:
        city_name = city_tuple[1]
        date_label_dist = {}
        for period in period_list:
            start_time = period[0]
            end_time = period[-1]

            places_data_list = place_data_process.prepare_palce_data(start_time, end_time, city_tuple, place_news_base_path, stop_word_path, path_encoding)
            if places_data_list:
                place_news_id_list, place_news_content_list = zip(*places_data_list)
                place_news_vectorized_list = vectorizer.transform(place_news_content_list)

                place_news_vectorized_list = ch2.transform(place_news_vectorized_list)

                palce_news_label = clf.predict(place_news_vectorized_list)
                date_label_dist[start_time] = utils.risk_label_count(palce_news_label)
            else:
                date_label_dist[start_time] = {'0':0, '1':0}
        # print date_label_dist
        city_date_lable_count[city_name] = date_label_dist

    return city_date_lable_count


def compute_city_date_risk_level(city_date_label_distribution):
    city_date_risk_level = {} #{Beijing:{2016-09-16:0.25}}
    for city in city_date_label_distribution:

        date_label_distribution = city_date_label_distribution[city]
        date_risk_level = {}
        for date_string in date_label_distribution:

            label_distribution = date_label_distribution[date_string]
            label_0 = label_distribution.get('0', 0)
            label_1 = label_distribution.get('1', 0)

            all_news =  label_0 + label_1
            if all_news > 0:
                risk_level = 1.0*label_1/all_news
            else:
                risk_level = 0

            date_risk_level[date_string] = risk_level
        city_date_risk_level[city] = date_risk_level
    return city_date_risk_level

def daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', risk_level_basepath = u'D:/baiduCityNews/news_day_xml/',path_encoding = 'gbk'):
    model_path = './model/'
    period_list = [[yesterday_date_string]]

    city_date_lable_count = place_data_process.get_day_news_count(yesterday_date_string, city_tuple_list, place_news_base_path, path_encoding = path_encoding)
    sorted_city_newscount = sorted(city_date_lable_count.items(), key=lambda a:a[1], reverse=True)

    # city_date_risk_distribution = get_city_date_label_distribution( HotwordDataConf.TRAIN_DATA_START_DATE_STRING, HotwordDataConf.TRAIN_DATA_END_DATE_STRING, [[yesterday_date_string]], CityPredictConf.CITY_TUPLE_LIST,
    #                                                                 risk_basepath = HotwordDataConf.RISK_DATA_BASEPATH, news_xml_basepath = HotwordDataConf.NEWS_XML_BASEPATH, place_news_base_path = place_news_base_path,
    #                                                                 stop_word_path = HotwordDataConf.STOP_WORD_PATH, path_encoding = SpiderConf.PATH_ENCODING)

    city_date_risk_distribution = get_city_date_label_distribution_v2(model_path, period_list, city_tuple_list, place_news_base_path = place_news_base_path, path_encoding = path_encoding)
    city_risklevel_distribution = compute_city_date_risk_level(city_date_risk_distribution)

    city_risk_level_dict = {}
    for city in city_risklevel_distribution:
        city_risk_level_dict[city] = city_risklevel_distribution[city][yesterday_date_string]

    sorted_city_risklevel = sorted(city_risk_level_dict.iteritems(), key=lambda d:d[1], reverse = True)

    print '===============开始城市风险水平计算=================='
    for city_count in sorted_city_newscount:
        print '%s:%d'%city_count

    for key in sorted_city_risklevel:
        print '%s:%.4f'%key

    if not os.path.exists(risk_level_basepath):
        os.makedirs(risk_level_basepath)

    OUTPUT = file('%s/%s.NEWSCOUNT'%(risk_level_basepath, yesterday_date_string), 'w')
    OUTPUT.write(json.dumps(sorted_city_newscount, indent=4, ensure_ascii=False))
    OUTPUT.close()

    OUTPUT = file('%s/%s.RISKLEVEL'%(risk_level_basepath, yesterday_date_string), 'w')
    OUTPUT.write(json.dumps(sorted_city_risklevel, indent=4, ensure_ascii=False))
    OUTPUT.close()

    return sorted_city_newscount, sorted_city_risklevel


def wirte_risk_level_2_csv(city_date_risk_level, city_list, period_list, csv_path):
    csv_writer = csv.writer(file(csv_path, 'wb'))
    date_list = [key[0] for key in period_list]
    csv_writer.writerow([''] + date_list)

    for city in city_list:
        city_risk_list = [city.encode('gbk')] + utils.get_values_form_dict(city_date_risk_level[city], date_list)
        print city_risk_list
        csv_writer.writerow(city_risk_list)

if __name__ == '__main__':
    '''
    predict_start_time = '2016-05-25'
    predict_end_time = '2016-10-20'
    type_list = [0,1,2,3]
    for type in type_list:
        csv_path = './city_date_risk_level_%d.csv'%type

        period_list = utils.generate_period_list(predict_start_time, predict_end_time, type=type)
        city_tuple_list = [(u'北京',u'北京'),(u'安徽',u'合肥'),(u'福建',u'福州'),(u'福建',u'厦门'),(u'甘肃',u'酒泉'),
                           (u'广东',u'广州'),(u'广东',u'深圳'),(u'广西',u'南宁'),(u'贵州',u'贵阳'),(u'海南',u'海口'),
                           (u'河北',u'石家庄'),(u'河南',u'郑州'),(u'黑龙江',u'哈尔滨'),(u'四川',u'成都'),(u'天津',u'天津'),
                           (u'湖北',u'武汉'),(u'湖南',u'长沙'),(u'吉林',u'长春'),(u'江苏',u'南京'),(u'云南',u'昆明'),
                           (u'江西',u'南昌'),(u'辽宁',u'沈阳'),(u'内蒙古',u'呼和浩特'),(u'宁夏',u'银川'),(u'青海',u'西宁'),
                           (u'山东',u'济南'),(u'山东',u'青岛'),(u'山西',u'太原'),(u'陕西',u'西安'),(u'上海',u'上海'),
                           (u'西藏',u'拉萨'),(u'新疆',u'乌鲁木齐'),(u'浙江',u'杭州'),(u'重庆',u'重庆')]

        province_list, city_list = zip(*city_tuple_list)
        # city_date_label_distribution = get_city_date_label_distribution('2016-01-01', '2016-10-16', period_list, city_tuple_list)
        city_date_label_distribution = get_city_date_label_distribution('2016-01-01', '2016-10-16', period_list, city_tuple_list)
        city_date_risk_level = compute_city_date_risk_level(city_date_label_distribution)

        wirte_risk_level_2_csv(city_date_risk_level, city_list, period_list, csv_path)
    '''

    # model_path = 'model/'
    # period_list = [['2017-06-11']]
    # city_tuple_list = [(u'北京',u'北京')]
    # place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    # city_date_lable_count = get_city_date_label_distribution_v2(model_path, period_list, city_tuple_list, place_news_base_path = place_news_base_path, path_encoding = 'gbk')

    # yesterday_date_string = utils.get_yesterday_date_string()
    yesterday_date_string = '2017-06-12'
    city_tuple_list = [(u'北京',u'北京')]
    place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    # path_encoding = conf.SpiderConf.PATH_ENCODING

    print daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', path_encoding = 'gbk')