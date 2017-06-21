#coding:utf-8
import os, json
import utils, conf
import xml.etree.cElementTree as ET

path_encoding = conf.BaseConf.PATH_ENCODING

def place_xml_parse(place_xml_path, city_code = 'cityNews'):

    news_list = [] ##[{news_content, }]
    etree = ET.parse(place_xml_path)
    root = etree.getroot()
    node_list = root.find('Total').getchildren()

    news_raw_id = 0
    for news_info in node_list:
        news_info_dict = dict()
        title = news_info.find('title').text
        content = news_info.find('news_content').text
        news_time = news_info.find('news_time').text
        news_source = news_info.find('source').text
        news_link = news_info.find('news_link').text

        news_date_string = news_time.split()[0]
        newsID = city_code + news_date_string.replace('-', '') + str(news_raw_id).zfill(3)
        news_raw_id += 1

        provinve = place_xml_path.split('/')[-3].decode('gbk')
        city = place_xml_path.split('/')[-2].decode('gbk')

        # print provinve
        news_info_dict['title'] = title
        news_info_dict['content'] = content
        news_info_dict['news_time'] = news_time
        news_info_dict['province'] = provinve
        news_info_dict['city'] = city
        news_info_dict['id'] = newsID
        news_info_dict['source'] = news_source
        news_info_dict['news_link'] = news_link

        news_list.append(news_info_dict)
    return news_list

def city_news2json(city_news_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_xml/',city_tuple_list = [], start_date = '2016-05-25', end_date = '2017-02-23'):

    date_list = utils.generate_date_list(start_date, end_date)
    cityTuple_newsList = list()

    for city_tuple in city_tuple_list:
        provine = city_tuple[0]
        city = city_tuple[1]
        news_list = []

        for date_string in date_list:
            place_xml_path = (u'%s/%s/%s/%s.xml'%(city_news_basepath, provine, city, date_string)).encode(path_encoding)
            if not os.path.exists(place_xml_path):
                path_info = place_xml_path.split('/')
                #TODO: log
                print 'no data! %s %s:%s' %(date_string, provine, city)
                continue
            try:
                news_list += place_xml_parse(place_xml_path, city_code = 'cityNews')
            except:
                #TODO: log
                print 'xml parse error! %s %s:%s' %(date_string, provine, city)
                pass
        cityTuple_newsList.append(news_list)
    return cityTuple_newsList





if __name__ == '__main__':

    # city_tuple_list = [(u'北京',u'北京'),(u'安徽',u'合肥'),(u'福建',u'福州'),(u'福建',u'厦门'),(u'甘肃',u'酒泉'),
    #                (u'广东',u'广州'),(u'广东',u'深圳'),(u'广西',u'南宁'),(u'贵州',u'贵阳'),(u'海南',u'海口'),
    #                (u'河北',u'石家庄'),(u'河南',u'郑州'),(u'黑龙江',u'哈尔滨'),(u'四川',u'成都'),(u'天津',u'天津'),
    #                (u'湖北',u'武汉'),(u'湖南',u'长沙'),(u'吉林',u'长春'),(u'江苏',u'南京'),(u'云南',u'昆明'),
    #                (u'江西',u'南昌'),(u'辽宁',u'沈阳'),(u'内蒙古',u'呼和浩特'),(u'宁夏',u'银川'),(u'青海',u'西宁'),
    #                (u'山东',u'济南'),(u'山东',u'青岛'),(u'山西',u'太原'),(u'陕西',u'西安'),(u'上海',u'上海'),
    #                (u'西藏',u'拉萨'),(u'新疆',u'乌鲁木齐'),(u'浙江',u'杭州'),(u'重庆',u'重庆')]

    city_tuple_list = [(u'北京',u'北京')]

    city_news_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_xml/'
    cityTuple_newsList = city_news2json(city_news_basepath, city_tuple_list, start_date = '2017-04-06', end_date = '2017-04-06')
    print len(cityTuple_newsList[0])

