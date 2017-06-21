#coding:utf-8
import datetime, os, time, json
import smtplib, types
from email.mime.text import MIMEText

import jieba
import jieba.posseg as pseg



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

def get_yesterday_date_string():
    '''
    获取昨天日期的字符串形式 %Y-%m-%d
    :return:
    '''
    nowdate = datetime.datetime.now().date()
    yesterday_date = nowdate + datetime .timedelta(days = -1) ###昨天日期
    datetime_string = yesterday_date.strftime('%Y-%m-%d')

    return datetime_string

def post_Reminder(mail_content, to_mail):
    '''
    发邮件推送，to_mial为收件人列表
    http://www.cnblogs.com/kratos0517/p/4138910.html
    :param mail_content: utf-8编码格式
    :param to_mail: 收件人列表[]
    :return:
    '''
    #
    mail_host="smtp.sina.com"  #设置服务器
    mail_user="amss701"    #用户名
    mail_pass="18732816300"   #口令
    mail_postfix="sina.com"  #发件箱的后缀
    # mail_host="smtp.163.com"  #设置服务器
    # mail_user="hotwordversion"    #用户名
    # mail_pass="baiducas"   #口令
    # mail_postfix="163.com"  #发件箱的后缀
    ###生成要推送的微博时间
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d')

    date_string = get_yesterday_date_string()
    me="百度城市新闻推送系统"+"<"+mail_user+"@"+mail_postfix+">"###设置发信人的显示
    #msg = MIMEText(mail_content,_subtype='html',_charset='utf-8')###发信内容
    msg = MIMEText(mail_content,_subtype='html',_charset='utf-8')###发信内容
    msg['Subject'] = '城市风险排名与北京风险画像(%s)'%date_string###邮件标题
    msg['From'] = me
    msg['To'] = ",".join(to_mail) ###收件人

    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_mail, msg.as_string())
        server.close()
    except Exception, e:
        print str(e)

def get_stop_word_dict(stop_word_datapath):
    if not os.path.exists(stop_word_datapath):
        return {}
    stop_word_dict = {}.fromkeys([line.strip().decode('utf-8') for line in open(stop_word_datapath)])
    return stop_word_dict
def str2List(String_list):
    if type(String_list) == types.StringType or type(String_list) == types.UnicodeType:
        return [String_list]
    elif type(String_list) == types.ListType:
        return String_list
    else:
        raise ValueError('not String or List!')
        # print

def word_cut_remove_stopwords(text, reserved_word=None,stop_word_dict={}, word_max = 10000000000):
    '''
    对text进行切词，并使用停用词表stop_word_dict，只保留前word_max个词
    :param text: 待切词文本,可以为String也可以为List
    :param stop_word_dict: 停用词表
    :param word_max: 此数量上界
    :return: 切词之后的结果，每个词用空格分开，编码为utf-8格式
    '''
    if reserved_word:
        jieba.load_userdict(reserved_word)

    text_list = str2List(text)
    word_string_list = list()
    for text in text_list:
        seg_list = jieba.cut(text, cut_all=False)
        word_string = ''
        word_count = 0
        for seg in seg_list:  ###去停用词
            if not seg.strip(): #空字符串跳过
                continue
            if stop_word_dict.has_key(seg):
                continue
            if word_count > word_max:
                break
            word_string += seg.strip() + u' '
            word_count += 1
        word_string_list.append(word_string)

    if len(word_string_list) == 1:
        return word_string_list[0]
    else:
        return word_string_list

def generate_date_list(start_time, end_time):
    date_string_list = []

    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    while start_time <= end_time:
        date_string_list.append(start_time.strftime('%Y-%m-%d'))
        start_time += datetime.timedelta(days=1)

    return date_string_list


def generate_period_list(start_time, end_time, type = 1):
    '''
    生成不同周期中的时间,[[],[],[]]根据type的不同，list中的元素为不同维度的时间列表
    :param start_time: 总时间段开始时间
    :param end_time: 总时间段结束时间
    :param type: 0为天，1为周，2为月，其他为整体
    :return: period_list最后生成的不同时间段的list
    '''
    period_list = []
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    period = []
    while start_time <= end_time:
        if (type == 1 and start_time.weekday() == 0 and len(period) > 0) or (type == 0 and len(period) > 0) or (type == 2 and start_time.day == 1 and len(period) > 0):
            period_list.append(period)
            period = []
        period.append(start_time.strftime('%Y-%m-%d'))
        start_time += datetime.timedelta(days=1)

    period_list.append(period)
    return period_list


def generate_date_with_spans(start_time, end_time, spans_list):
    span_date_tuple_dict = {}
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')

    for span in spans_list:
        predict_date_dict = {}  # {date_to_predict: (train_start_time, train_end_time)}

        starttime_of_train_data = start_time
        endtime_of_train_data = starttime_of_train_data + datetime.timedelta(days=span - 1)
        date2predict = start_time + datetime.timedelta(days=span)

        while date2predict <= end_time:
            train_date_tuple = (starttime_of_train_data.strftime('%Y-%m-%d'), endtime_of_train_data.strftime('%Y-%m-%d'))
            predict_date_dict[date2predict.strftime('%Y-%m-%d')] = train_date_tuple

            date2predict += datetime.timedelta(days=1)
            starttime_of_train_data += datetime.timedelta(days=1)
            endtime_of_train_data += datetime.timedelta(days=1)
        span_date_tuple_dict[span] = predict_date_dict

    return span_date_tuple_dict

def label_8class_to_2class(id_list):
    new_id_list = []
    for id_string in id_list:
        if id_string == '8':
            new_id_list.append('0')
        else:
            new_id_list.append('1')

    return new_id_list

def risk_label_count(risk_label_list):

    label_count_dict = {}
    for label in risk_label_list:
        label_count_dict[label] = label_count_dict.get(label, 0) + 1
    return label_count_dict

def keyword_list_2_keyword_distribution(keyword_list):
    '''
    [[key1, key2, key3],[key1, key2, key3]]
    :param keyword_list:
    :return:{key1:10, key2:20}
    '''
    keyword_distribution = {}
    for keywords in keyword_list:
        for keyword in keywords:
            keyword_distribution[keyword] = keyword_distribution.get(keyword, 0) + 1

    return keyword_distribution

def risk_data_duplicate(x_list, y_list, times = 2):
    new_x_list = []
    new_y_list = []

    for i in range(len(x_list)):
        new_x_list.append(x_list[i])
        new_y_list.append(y_list[i])

        if y_list[i] == '1': #有风险数据重复
            new_x_list += [x_list[i] for j in range(times -1)]
            new_y_list += [y_list[i] for j in range(times -1)]

    return new_x_list, new_y_list


def get_values_form_dict(input_dict, input_list, value = 0):
    return [input_dict.get(key, value) for key in input_list]

def dumps_news2json(news_dict_list, json_path = './news.data', type='w'):
    '''
    讲新闻dict的list写入到本地文件中，每行为一个新闻json数据，数据中的json字段中文编码需为utf-8
    :param news_dict_list: 新闻dict的list数据
    :param json_path: 文件保存路径
    :param type: a在文件尾插入，w直接生成新文件进行写入
    :return:
    '''
    OUTPUT = open(json_path, type)

    for news_dict in news_dict_list:
        OUTPUT.write(json.dumps(news_dict, ensure_ascii=False) + '\n')

def load_reserved_word(reserved_word_path):
    if not os.path.exists(reserved_word_path):
        return {}
    reserved_word_dict = {}.fromkeys([line.rstrip().decode('utf-8') for line in open(reserved_word_path)])
    return reserved_word_dict

def wordcut4lda(text, reserved_word_path=''):
    '''
    对文本内容进行切词，为LDA准备数据，只保留n、vn、nr和保留词典里的词
    :param text:
    :param reserved_word_path:
    :return:
    '''
    if reserved_word_path:
        jieba.load_userdict(reserved_word_path)
        reservedWord = load_reserved_word(reserved_word_path)
    else:
        reservedWord = dict()

    text_list = str2List(text)
    word_string_list = list()

    for text in text_list:
        segList = pseg.cut(text)
        contentSeg = u''
        for word, flag in segList:
            if flag == 'n' or flag == 'vn' or flag == 'nr' or word in reservedWord:
                if len(word) == 1:
                    continue
                contentSeg += (u'%s ' %word)
        word_string_list.append(contentSeg[:-1])

    if len(word_string_list) == 1:
        return word_string_list[0]
    else:
        return word_string_list






if __name__ == '__main__':
    # print word_cut_remove_stopwords('我喜欢你！！！')

    # print generate_date_list(start_time = '2016-10-01', end_time='2016-10-31')

    # spans_list = range(3, 100)
    # print generate_date_with_spans('2016-08-01', '2016-10-31', spans_list)
    # label_list = ['0','0','1','0','1','0','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','0','0','1','0','1','1','0','0','0','0','0','0','0','0','1','0','0','1','0','0','0','0','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0']
    #
    # print len(label_list)
    # print risk_label_count(label_list)

    # x_list = [[0,2], [1,2], [2,2]]
    # y_list = ['1', '1', '0']
    # print risk_data_duplicate(x_list, y_list, times=2)

    # input_dict = {'1':1, '2':2}
    # input_list = ['2', '3']
    # print get_values_form_dict(input_dict, input_list, value = 0)

    # keyword_list = [['a', 'a', 'b', 'c'], ['a', 'd']]
    # keyword_distribution = keyword_list_2_keyword_distribution(keyword_list)
    # print keyword_distribution

    # news_dict_list = [{'time':'2014', 'title': '明天新闻', 'content':'新闻联播'}, {'time':'2014', 'title': '明天新闻', 'content':'新闻联播'}]
    # dumps_news2json(news_dict_list, json_path='./news.data', type='a')

    # is_List('1')
    # pass
    # print word_cut_remove_stopwords('佩雷拉雪兹神父公墓', reserved_word='sys/reservedWord.txt', stop_word_dict={}, word_max=10000000000)


    '''#测试LDA切词
    # text = '我饿了，去吃饭吧？有什么好吃的呢？不知道啊，我想吃鱼香肉丝、鱼头泡饼'
    text = ['我饿了，去吃饭吧？有什么好吃的呢？不知道啊，我想吃鱼香肉丝、鱼头泡饼',
            '我饿了，去吃饭吧？有什么好吃的呢？不知道啊，我想吃鱼香肉丝、鱼头泡饼']

    reserved_word_path = conf.BaseConf.RESERVEDWORD
    print utils.wordcut4lda(text, reserved_word_path)
    '''
    email_list = ['xunuo1991@amss.ac.cn','hebeijiayugai@126.com','yuanpengjia@amss.ac.cn']
        # email_list = ['yuanpengjia@amss.ac.cn']
    mail_content = 'hello'
    post_Reminder(mail_content, email_list)