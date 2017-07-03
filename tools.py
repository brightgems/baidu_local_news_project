#coding:utf-8
import csv

import baidu_Spider
import utils
import city_risklevel_profile

#现在每日的新闻数据

# baidu_city_basepath = 'D:/baiduCityNews/'

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

def daily_city_risklevel(start_time, end_time, city_tuple_list, city_news_basepath, save_path, type = 0):
    '''
    计算城市风险水平，并保存到本地csv文件中
    :param start_time: 计算时间范围的起始时间
    :param end_time: 计算时间范围的结束时间
    :param city_tuple_list: 需要计算的城市，最后保存结果中一列为一个城市的风险水平
    :param city_news_basepath: 城市新闻数据保存地址
    :param save_path: 计算城市风险水平csv文件保存路径
    :param type:计算每日(type = 0)风险水平还是每周(type = 1)、每月(type = 2)还是整体(其它值)
    :return:
    '''

    model_path = 'model/'
    period_list = utils.generate_period_list(start_time, end_time, type=type)
    # period_list = [['2017-06-11']]
    # city_tuple_list = [(u'安徽',u'合肥')]
    # city_news_basepath = u'C:/4code/data/'
    city_date_label_count = city_risklevel_profile.get_city_date_label_distribution_v2(model_path, period_list, city_tuple_list, place_news_base_path = city_news_basepath, path_encoding = 'gbk')
    city_date_riskLevel = city_risklevel_profile.compute_city_date_risk_level(city_date_label_count)
    #变量格式：city_date_label_count {u'\u5408\u80a5': {'2017-06-21': {'1': 10, '0': 34}}}
    #变量格式：city_date_riskLevel {u'\u5408\u80a5': {'2017-06-21': 0.22727272727272727}}

    ###将信息保存到本地csv文件
    csv_writer = csv.writer(file(save_path, 'wb'))
    first_row = ['']
    for key in city_tuple_list:
        first_row.extend([(u'%s:news_count'%key[1]).encode('gbk'),(u'%s:risk_level'%key[1]).encode('gbk')])
    csv_writer.writerow(first_row)

    for date_period in period_list:
        date_string = date_period[0]
        row_list = [date_string]
        for city_tuple in city_tuple_list:
            city = city_tuple[1]

            row_list.append(sum(city_date_label_count.setdefault(city, dict()).setdefault(date_string, dict()).values()))
            row_list.append('%.4f'%(city_date_riskLevel.setdefault(city,dict()).get(date_string, 0)))

        csv_writer.writerow(row_list)

if __name__ == '__main__':

    # daily_news_download('2017-06-20', '2017-06-20')
    '''
    yesterday_date_string = utils.get_yesterday_date_string()
    city_tuple_list = [(u'北京',u'北京')]
    place_news_base_path = u'D:/baiduCityNews/news_day_xml/'
    path_encoding = conf.SpiderConf.PATH_ENCODING

    print city_risk_profile.daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = u'D:/baiduCityNews/news_day_xml/', path_encoding = 'gbk')
    '''

    ''' '''
    ###计算城市的风险水平并保存到本地
    # city_news_basepath = u'C:/4code/data/'
    city_news_basepath = u'D:/baiduCityNews/news_day_xml/'
    city_tuple_list = [(u'安徽',u'合肥')]
    daily_city_risklevel('2016-05-25', '2017-06-30', city_tuple_list, city_news_basepath, save_path = 'output/temp.csv',type=0)

