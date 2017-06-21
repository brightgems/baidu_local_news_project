#coding:utf-8

import baidu_Spider
import utils

#现在每日的新闻数据

baidu_city_basepath = 'D:/baiduCityNews/'

def daily_news_download(start_date, end_date):
    '''
    根据本地每小时下载的新闻列表，对每日新闻进行汇总并下载新闻正文。前提需要：本地每小时新闻列表需要存在！
    :param start_date: 开始时间
    :param end_date: 结束时间
    :return: 把新闻下载到本地
    '''
    date_list = utils.generate_date_list(start_date, end_date)

    hourBasePath = baidu_city_basepath + 'news_hour_xml'
    saveBasePath = baidu_city_basepath + 'news_day_xml/'

    for datetime_string in date_list:
        baidu_Spider.get_all_province_news_content(datetime_string, hourBasePath = hourBasePath, saveBasePath = saveBasePath)

def daily_city_risklevel():

    model_path = 'model/'
    period_list = [['2017-06-11']]
    city_tuple_list = [(u'北京',u'北京')]
    place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    city_date_lable_count = get_city_date_label_distribution_v2(model_path, period_list, city_tuple_list, place_news_base_path = place_news_base_path, path_encoding = 'gbk')







if __name__ == '__main__':


    daily_news_download('2017-06-20', '2017-06-20')
    '''

    yesterday_date_string = utils.get_yesterday_date_string()
    city_tuple_list = [(u'北京',u'北京')]
    place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    path_encoding = conf.SpiderConf.PATH_ENCODING

    print city_risk_profile.daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', path_encoding = 'gbk')
    '''