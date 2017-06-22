#coding:utf-8
import urllib2,urllib
import sys,os
import datetime,time
from bs4 import BeautifulSoup
from xml.dom import minidom
import xml.etree.ElementTree as ET
from readability.readability import Document
import html2text
import socket

import conf


socket.setdefaulttimeout(5)  ###网页超时报错
reload(sys)
sys.setdefaultencoding('utf-8')
###-------------------------------------------
#与3.0区别：
# 3.1：抓取网页换成了RSS网页
# 3.2：每天新闻汇总时，剔除与前5天重复的新闻
# 将信息写入xml文件函数write2xml与hotword_project保持一致，xml文件中节点标签发生变化
###-------------------------------------------

###通过url获得新闻正文
def get_news_content(news_link):
    try:
        html = urllib.urlopen(news_link).read()
    except: ###请求超时，返回空网页
        return ''
    readable_article = Document(html).summary()
    content = html2text.html2text(readable_article)
    while 1:
        i = content.find('!')
        j= content.find(')',content.find('!'))
        if i == -1 or j == -1:
            break
        content = content.replace(content[i:j+1],'')
    return content.encode('utf-8').replace('\n','').replace(' ','').replace('  ','').replace('　　','').replace('[','').replace(']','')

#伪装成浏览器访问
def browGetHtml (url):
    req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept':'text/html;q=0.9,*/*;q=0.8' ,
    'Accept-Charset':'ISO-8859-1,utf-8,gbk;q=0.7,*;q=0.3' ,
#     'Accept-Encoding':'gzip',
    'Connection':'close',
    'Referer':None
    }
    req_timeout = 5
    request = urllib2 .Request(url,None,req_header)
    response = urllib2 .urlopen(request,None,req_timeout)
    html_content = response .read()
    return html_content


def get_update_news(url, begin_time = '2016-04-27 16:06'):
    '''
    根据“最新北京新闻”获取一定时间之后的新闻列表
    此版本中没有使用此函数，如果抓取最近新闻则使用此函数
    :param url:“最新北京新闻”的网址
    :param begin_time:获取此时间之后的所有新闻
    :return:更新的新闻列表[{},{}]
    '''

    htmlContent = browGetHtml(url)

    update_list = []                        #更新新闻列表
    soup = BeautifulSoup(htmlContent)
    #print soup
    newsAll = soup.find('td',valign='top')
    newsList = newsAll.findAll('div', class_='p2')
    for oneNews in newsList:
        info_dict = {}
        newsTitle = oneNews.find('a')
        title = newsTitle.text
        news_link = newsTitle['href']

        sourceInfo = oneNews.find('font')
        infoList = sourceInfo.text.split()
        source = infoList[0]
        now_time = datetime.datetime.now()
        if len(infoList) == 2 :
            news_time = '%s %s'%(now_time.strftime('%Y-%m-%d') ,infoList[1])
        elif len(infoList) == 3:
            news_time = '%s-%s %s'%(now_time.year, infoList[1], infoList[2])
        info_dict['news_time'], info_dict['news_link'], info_dict['title'], info_dict['source'] = news_time, news_link, title.encode('utf-8'), source.encode('utf-8')

        if datetime.datetime.strptime(news_time, '%Y-%m-%d %H:%M') >= datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M'):
            update_list.append(info_dict)

    return update_list


def get_update_news_rss(url):
    '''
    根据百度新闻的rss部分获取新闻
    :param url:RSS的网址
    :return:更新的新闻列表[{},{}]
    '''

    htmlContent = browGetHtml(url)
    update_list = []                        #更新新闻列表

    soup = BeautifulSoup(htmlContent.decode('utf-8'),'html.parser')
    newsList = soup.findAll('item')
    for oneNews in newsList:
        info_dict = {}
        newsTitle = oneNews.find('title')
        title = newsTitle.text.replace('&lt;','')
        news_link = oneNews.find('link').text

        source = oneNews.find('source').text
        news_time_temp = oneNews.find('pubdate').text
        news_time = datetime .datetime.strptime(news_time_temp,'%Y-%m-%dT%H:%M:%S.000Z') + datetime.timedelta(hours=8)
        news_time = news_time.strftime('%Y-%m-%d %H:%M:%S')
        info_dict['news_time'], info_dict['news_link'], info_dict['title'], info_dict['source'] = news_time, news_link, title.encode('utf-8'), source.encode('utf-8')
        update_list.append(info_dict)
    return update_list


def write2xml(filePath, hotword_list,date_flag = True,date_string = '%Y-%m-%d-%H-%M' ,num_flag = True, total_flag = True):
    '''
    将hotword_list中的信息保存到本地xml文件中
    :param filePath:xml文件路径
    :param hotword_list:需要保存的列表信息，列表中元素为字典格式
    :param date_flag:是否在xml文件中保存日期信息
    :param date_string:如果需要保存日期信息，日期的具体信息
    :param num_flag:是否需要保存信息总数
    :param total_flag:字典中的信息直接保存在根节点下，还是保存在Total节点下
    :return:
    '''
    doc = minidom.Document()
    root = doc.createElement('Rankings')
    doc.appendChild(root)
    ###如果写入时间信息
    if date_flag:
        nowtime = datetime.datetime.now()
        nowtime = nowtime.strftime(date_string)
        time_info_list = nowtime.split('-')
        time_tag_info = date_string.split('-')
        time_tag_dict = {'%Y':'Year','%m':'Month','%d':'Day','%H':'Hour','%M':'Minute'}
        for i in range(len(time_info_list)):
            time_info = doc.createElement(time_tag_dict[time_tag_info[i]])
            time_info_text = doc.createTextNode(time_info_list[i])
            time_info.appendChild(time_info_text)
            root.appendChild(time_info)
    ###如果写入时间信息
    if num_flag:
        num_info = doc.createElement('number')
        num_info_text = doc.createTextNode(str(len(hotword_list)))
        num_info.appendChild(num_info_text)
        root.appendChild(num_info)

    if total_flag:
        total = doc.createElement('Total')
        root.appendChild(total)
    for one_hotword in hotword_list:
        item = doc.createElement('item')
        for info in one_hotword:###one_hotword为字典格式
            info_child = doc.createElement(info)
            info_child_text = doc.createTextNode(str(one_hotword[info]))
            info_child.appendChild(info_child_text)
            item.appendChild(info_child)
        if total_flag:
            total.appendChild(item)
        else:
            root.appendChild(item)
    f = file(filePath, 'w')
    doc.writexml(f, '', '   ', '\n', 'utf-8')
    f.close()


def read_link(filepath):
    '''
    读取本地文件中的数据，获取各个地区的url
    :param filepath:本地文件路径
    :return:{'url'：省份}，其中url中可以获得城市信息
    '''
    province_dict = {}
    content = open(filepath,'r')
    for line in content:
        link = line.split()[0]
        province_name = line.split()[1].strip()
        province_dict[link] = province_name
    return province_dict


def timer(the_time = '*:28'):
    '''
    定时器，定时至某个固定时间 hh:mm
    :param the_time:需要休眠至的时间，如果hh为*，则为每小时运行，否则为每天运行一次
    :return:None
    '''
    now_time = datetime.datetime.now()
    the_hour = the_time.split(':')[0]
    the_minute = int(the_time.split(':')[1])
    if  the_hour== '*': ###每小时运行
        run_time = now_time.replace(minute=the_minute,second=0)
        if not run_time > now_time: ###已经过了本小时的运行时间，则下小时运行
            run_time += datetime .timedelta(hours = 1)
        sleep_time = (run_time - now_time).seconds
        print('距离下次运行还有%ss'%sleep_time)
        #time.sleep (sleep_time)
    else: ###每天固定时间
        the_hour = int(the_hour)
        run_time = now_time.replace(hour=the_hour, minute=the_minute,second=0)
        if not run_time > now_time: ###已经过了本小时的运行时间，则明天运行
            run_time += datetime .timedelta(days = 1)
        sleep_time = (run_time - now_time).seconds
        print('距离下次运行还有%ss'%sleep_time)
    time.sleep (sleep_time)


def get_update_list(url,the_time, province, hourBasePath, encoding = 'gbk',news_type = 'rss'):
    '''
    获得某个城市的新闻，如果新闻数量多于1，则将新闻结果保存到本地
    :param url:要抓取的
    :param the_time:
    :param province:当前url所属省份
    :param news_type:通过哪个网页抓取新闻，rss或latest_news(最新新闻)
    :return:
    '''
    now_time = datetime.datetime.now()
    print '现在时间：%s'%now_time.strftime('%Y-%m-%d %H:%M:%S')
    ###获取城市名
    city_name = url.split('&name=')[1].split('&')[0]
    city_name = urllib.unquote(city_name)
    print'开始下载【%s】相关新闻：'%city_name.decode('gbk').encode('utf-8')
    ###新闻更新时间设置
    begin_time = now_time  + datetime .timedelta(hours = -1)
    minute = int(the_time.split(':')[1])
    begin_time = begin_time.replace(minute = minute, second= 0)
    begin_time = begin_time.strftime('%Y-%m-%d %H:%M')
    ###开始尝试抓取网页
    for i in range(10):###尝试5次，如果
        try:
            if news_type == 'latest_news':
                update_news = get_update_news(url,begin_time) ### 最新北京新闻下载
            elif  news_type == 'rss':
                url = url.replace('pn=1','tn=rss')
                update_news = get_update_news_rss(url)  ###通过RSS部分下载北京新闻
            print '...%s下载成功' % now_time.strftime('%Y-%m-%d %H:%M:%S')
            break
        except:
            print '...%s下载失败'%now_time.strftime('%Y-%m-%d %H:%M:%S')
            update_news = []
            continue
    if len(update_news) > 0:
        ###今天日期，用于目录名
        date_time = begin_time.split()[0]
        basepath = (u'%s/%s/%s/%s/'%(hourBasePath, province, city_name.decode('gbk'), date_time)).encode(encoding)
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        # filepath = basepath + begin_time.replace(' ','_').split(':')[0] + '.xml'###2017-04-07修改之前
        temp_time_string = now_time.strftime('%Y-%m-%d %H:%M')#修改之后
        filepath = basepath + temp_time_string.replace(' ','_').split(':')[0] + '.xml'#修改之后

        print '\t更新新闻数：%s'%len(update_news)
        write2xml(filepath, update_news, date_flag = False ,num_flag = False, total_flag = False)


def get_news_fliter_dict(day_xml_path, province, city, datetime_string, day_len = 5):
    '''
    获得datetime_string之前的day_len天所有的新闻
    :param day_xml_path: 每天新闻汇总路径
    :param province:要读取的省份信息
    :param city:城市信息
    :param datetime_string:这个时间之前5天的数据进行汇总
    :param day_len:需要的时间跨度
    :return:5天的所有新闻汇总结果dict.{link:True, }
    '''
    news_link_dict = {}
    temp_date = datetime.datetime.strptime(datetime_string, '%Y-%m-%d')
    for i in range(day_len):
        temp_date += datetime.timedelta(days=-1)
        temp_date_string = temp_date.strftime('%Y-%m-%d')
        city_oneday_Path = '%s/%s/%s/%s.xml'%(day_xml_path, province, city, temp_date_string)
        if not os.path.exists(city_oneday_Path):
            continue
        print city_oneday_Path
        try:
            tree=ET .parse(city_oneday_Path)
        except:
            continue
        root = tree .getroot()

        news_list = root .find('news_list')
        if not news_list:
            news_list = root .find('Total')

        all_news = news_list.getchildren()
        for news in all_news:
            link = news.find('news_link').text
            if not news_link_dict.has_key(link):
                news_link_dict[link] = True
    return news_link_dict


def get_oneday_news_content(basePath ,savePath, news_fliter_dict = {}):
    '''
    对basePath中的xml据进行汇总（根据news_link进行去重），并获取对应的新闻正文
    :param basePath:合并的新闻数据xml列表
    :param savePath:汇总之后的新闻存储位置,savePath需为.xml结尾
    :param news_fliter_dict:如果news_fliter_dict包含新闻链接，则今天保留此链接
    :return:None
    '''
    link_dict = {}
    one_day_news_list = [] ###用于保存每天所有的新闻数据，每条新闻数据{'news_link': ,'news_time': ,'source': ,'title': ,'content':}
    for fileName in os.listdir(basePath):
        filePath = basePath + fileName
        try:
            ET .parse(filePath)
        except:
            continue
        tree=ET .parse(filePath)
        root = tree .getroot()
        allNews = root .getchildren()
        allNews = list(reversed(allNews))
        for news in allNews:
            print ' '*5 + news.find('title').text.encode('utf-8')
            news_info = {}
            news_link = news.find('news_link').text
            if link_dict.has_key(news_link):
                continue
            elif news_fliter_dict.has_key(news_link): ###如果前几天新闻中包含此新闻链接，则跳过
                continue
            else:
                link_dict[news_link] = 1
                try:
                    news_content = get_news_content(news_link)
                except:
                    news_content = ''
                news_info['news_content'] = news_content
                for key in news.getchildren():
                    news_info[key.tag] = key.text
            one_day_news_list.append(news_info)
    if one_day_news_list:
        write2xml(savePath, one_day_news_list,date_flag = False, num_flag = True, total_flag = True)


def get_all_province_news_content(datetime_string, hourBasePath = './news_hour_xml',saveBasePath= './news_day_xml/', encoding = 'gbk'):
    '''
    对本地所有省份在datetime_string这天的新闻按城市进行汇总，并保存到news_day_xml文件中
    :param datetime_string:需要汇总的新闻日期
    :param hourBasePath:每小时新闻文件所在路径
    :param saveBasePath:每天汇总之后的新闻呢要保存的问价位置
    :return:
    '''
    for province in os.listdir(hourBasePath):
        # print province.decode('gbk').encode('utf-8')
        for city in os.listdir(hourBasePath + '/' +province):
            # print city.decode('gbk').encode('utf-8')
            city_oneday_basePath = '%s/%s/%s/%s/'%(hourBasePath, province, city, datetime_string)
            if not os.path.exists(city_oneday_basePath):
                continue  ###当天新闻没有更新的话，则跳过
            ###获取datetime_string之前五天的所有新闻链接数据，作为今天新闻过滤用
            news_fliter_dict = get_news_fliter_dict(saveBasePath, province, city, datetime_string, day_len = 5)

            if not os.path.exists('%s/%s/%s'%(saveBasePath, province, city)):
                os.makedirs('%s/%s/%s'%(saveBasePath, province, city))

            city_oneday_saveBasePath = '%s/%s/%s/%s.xml'%(saveBasePath, province, city, datetime_string)
            #print city_oneday_basePath.decode('gbk').encode('utf-8')
            print city_oneday_saveBasePath
            if not os.path.exists( '%s/%s/%s'%(saveBasePath, province, city)):
                os.makedirs('%s/%s/%s'%(saveBasePath, province, city))
            print len(news_fliter_dict)
            get_oneday_news_content(city_oneday_basePath ,city_oneday_saveBasePath, news_fliter_dict)


if __name__ == '__main__':
    hourBasePath = conf.SpiderConf.HOUR_DATA_BASEPATH
    dayBasePath = conf.SpiderConf.ONEDAY_DATA_BASEPATH

    encoding = conf.BaseConf.PATH_ENCODING

    filpath = conf.SpiderConf.CITY_NEWS_URL_FILEPATH
    province_dict = read_link(filpath)
    while True:
        ###现在时间
        the_time = '*:21'
        timer(the_time)###定时到整点运行

        for link in province_dict:
            province = province_dict[link].split(',')[0]
            get_update_list(link, the_time, province.decode('utf-8'), hourBasePath, encoding, news_type = 'rss')
            print '*****'*8
        print '#####'*8
        nowtime = datetime.datetime.now()
        if nowtime.hour == 9: ###如果是0点，则对昨天的新闻进行汇总
            nowdate = datetime.datetime.now().date()
            yesterday_date = nowdate + datetime .timedelta(days = -1) ###昨天日期
            datetime_string = yesterday_date.strftime('%Y-%m-%d')
            get_all_province_news_content(datetime_string, hourBasePath = hourBasePath, saveBasePath = dayBasePath, encoding = encoding)