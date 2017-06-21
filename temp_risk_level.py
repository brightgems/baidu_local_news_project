#coding:utf-8
import conf
import place_data_process
import utils

import city_risk_profile


def daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', path_encoding = 'gbk'):
    model_path = './model/'
    period_list = [[yesterday_date_string]]

    city_date_lable_count = place_data_process.get_day_news_count(yesterday_date_string, city_tuple_list, place_news_base_path, path_encoding = conf.SpiderConf.PATH_ENCODING)
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

    for city_count in sorted_city_newscount:
        print '%s:%d'%city_count

    for key in sorted_city_risklevel:
        print '%s:%.4f'%key

    return sorted_city_newscount, sorted_city_risklevel

if __name__ == '__main__':

    yesterday_date_string = utils.get_yesterday_date_string()
    city_tuple_list = [(u'北京',u'北京')]
    place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    path_encoding = conf.SpiderConf.PATH_ENCODING

    print city_risk_profile.daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', path_encoding = 'gbk')
