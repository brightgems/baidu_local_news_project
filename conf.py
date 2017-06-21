#coding:utf-8
import platform
DATA_BASEPATH = u'D:/baiduCityNews/'
class BaseConf():
    NEWS_BASEPATH = DATA_BASEPATH + u'news_day_xml/'
    NEWS_PROFILE_BASEPATH = DATA_BASEPATH + u'news_day_profile/'
    CITY_PROFILE_BASEPATH = DATA_BASEPATH + u'city_day_profile/'
    RISKLEVEL_BASEPATH = DATA_BASEPATH + u'risklevel_profile/'

    RESERVEDWORD = 'sys/reservedWord.txt'


    sysstr = platform.system()
    if sysstr == 'Windows':
        PATH_ENCODING = 'gbk'
    else:
        PATH_ENCODING = 'utf-8'

class SpiderConf(object):
    CITY_NEWS_URL_FILEPATH = './sys/province_list.txt'
    # BASE_PATH = '../spider_v3.2/'
    BASE_PATH = DATA_BASEPATH
    HOUR_DATA_BASEPATH = BASE_PATH + 'news_hour_xml'
    ONEDAY_DATA_BASEPATH= BASE_PATH +'news_day_xml/'

    SPIDER_HOUR_RUN_TIME = '*:00'
    SPIDER_DAY_RUN_TIME = 7




class HotwordDataConf(object):
    RISK_DATA_BASEPATH = 'E:/ypj/data_sets/baidu_hotword2016/riskdata/'
    NEWS_XML_BASEPATH = 'E:/ypj/data_sets/baidu_hotword2016/newsxml/'
    STOP_WORD_PATH = './sys/stopwords.txt'

    TRAIN_DATA_START_DATE_STRING = '2016-01-01'
    # TRAIN_DATA_START_DATE_STRING = '2016-10-16'
    TRAIN_DATA_END_DATE_STRING = '2016-10-16'

class CityPredictConf(object):

    CITY_TUPLE_LIST = [(u'北京',u'北京'),(u'安徽',u'合肥'),(u'福建',u'福州'),(u'福建',u'厦门'),(u'甘肃',u'酒泉'),
                        (u'广东',u'广州'),(u'广东',u'深圳'),(u'广西',u'南宁'),(u'贵州',u'贵阳'),(u'海南',u'海口'),
                        (u'河北',u'石家庄'),(u'河南',u'郑州'),(u'黑龙江',u'哈尔滨'),(u'四川',u'成都'),(u'天津',u'天津'),
                        (u'湖北',u'武汉'),(u'湖南',u'长沙'),(u'吉林',u'长春'),(u'江苏',u'南京'),(u'云南',u'昆明'),
                        (u'江西',u'南昌'),(u'辽宁',u'沈阳'),(u'内蒙古',u'呼和浩特'),(u'宁夏',u'银川'),(u'青海',u'西宁'),
                        (u'山东',u'济南'),(u'山东',u'青岛'),(u'山西',u'太原'),(u'陕西',u'西安'),(u'上海',u'上海'),
                        (u'西藏',u'拉萨'),(u'新疆',u'乌鲁木齐'),(u'浙江',u'杭州'),(u'重庆',u'重庆')]
    CITY_ENCODE = {u'北京':u'Beijing',u'合肥':u'Hefei',u'福州':u'Fuzhou', u'厦门':u'Xiamen',u'酒泉':u'Jiuquan',
                   u'广州':u'Guangzhou', u'深圳':u'Shenzhen', u'南宁':u'Nanning', u'贵阳':u'Guiyang',u'海口':u'Haikou',
                   u'石家庄':u'Shijiazhuang',u'郑州':u'Zhengzhou', u'哈尔滨':u'Haerbin', u'成都':u'Chengdu',u'天津':u'Tianjin',
                   u'武汉':u'Wuhan', u'长沙':u'Changsha', u'长春':u'Changchun', u'南京':u'Nanjing', u'昆明':u'Kunming',
                   u'南昌':u'Nanchang', u'沈阳':u'Shenyang', u'呼和浩特':u'Huhehaote', u'银川':u'Yinchuan', u'西宁':u'Xining',
                   u'济南':u'Jinan',u'青岛':u'Qingdao',u'太原':u'Taiyuan',u'西安':u'Xian',u'上海':u'Shanghai',
                   u'拉萨':u'Lasa',u'乌鲁木齐':u'Wulumuqi',u'杭州':u'Hangzhou',u'重庆':u'Chongqing', u'兰州':u'Lanzhou'}


class ProfileConf(object):
    cityProfile_tuple_list = [(u'北京', u'北京'), (u'安徽', u'合肥'), (u'福建', u'福州'), (u'福建', u'厦门'), (u'甘肃', u'酒泉'),
                       (u'广东', u'广州'), (u'广东', u'深圳'), (u'广西', u'南宁'), (u'贵州', u'贵阳'), (u'海南', u'海口'),
                       (u'河北', u'石家庄'), (u'河南', u'郑州'), (u'黑龙江', u'哈尔滨'), (u'四川', u'成都'), (u'天津', u'天津'),
                       (u'湖北', u'武汉'), (u'湖南', u'长沙'), (u'吉林', u'长春'), (u'江苏', u'南京'), (u'云南', u'昆明'),
                       (u'江西', u'南昌'), (u'辽宁', u'沈阳'), (u'内蒙古', u'呼和浩特'), (u'宁夏', u'银川'), (u'青海', u'西宁'),
                       (u'山东', u'济南'), (u'山东', u'青岛'), (u'山西', u'太原'), (u'陕西', u'西安'), (u'上海', u'上海'),
                       (u'西藏', u'拉萨'), (u'新疆', u'乌鲁木齐'), (u'浙江', u'杭州'), (u'重庆', u'重庆')]
    # cityProfile_tuple_list = [(u'北京', u'北京')]

class ReminderConf(object):

    city_remender_tuple_list = [(u'北京',u'北京')]
    reminde_time = 7
