#coding:utf-8
import json, csv, sys, pickle, os
import conf,utils

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn import metrics

reload(sys)
sys.setdefaultencoding('utf-8')

def newsList_keywords_static(news_list):
    '''
    news_list，统计所有关键词的频次，并从大到小排序，并返回结果
    :param news_list: [{'tilte':'','keywords':[(keyword1,weight)]},{'tilte':'','keywords':[(keyword1,weight)]},]
    :return: [(keyword1,all_weight),(keyword2,all_weight)]
    '''

    keywords_score_dict = dict()

    for news_object in news_list:
        if news_object['risk_label'] == '0':
            continue

        keyword_list = news_object['keywords']
        for keyword in keyword_list:
            keywords_score_dict[keyword[0]] = keywords_score_dict.get(keyword[0], 0) + keyword[1]
    sorted_keywords = sorted(keywords_score_dict.items(), key=lambda x:x[1], reverse=True)
    return sorted_keywords

def risk_keyword_flit(risk_keyword, keyword_filt_dict, topn = 300):
    '''
    通过filt_filepath的关键词过滤掉部分有风险关键词
    :param risk_keyword: 有风险的关键词列表[(keyword, weight), (keyword2, weight)]
    :param filt_filepath: 过滤的关键词位置
    :param topn: topn的有风险关键词
    :return: risk_keyword 过滤后的topn的有风险关键词[(keyword, weight), (keyword2, weight)]
    '''
    new_risk_keyword = [key for key in risk_keyword if not key[0] in keyword_filt_dict]
    if len(new_risk_keyword) > topn:
        return new_risk_keyword[:topn]
    else:
        return new_risk_keyword
    # open('risk_keyword_filt_by_risk_free.data', 'w').write(''.join(risk_keyword))

def news_clust(news_list):
    '''
    对输入的news_list进行聚类
    :param news_list:
    :return: 聚类之后的结果{cluster_id:[(newsID, weight, content)]}
    '''
    stopword_path = 'sys/stopwords.txt'

    stopword_dict = utils.get_stop_word_dict(stopword_path)
    news_list_word_cut = [utils.word_cut_remove_stopwords(news[2], stop_word_dict=stopword_dict) for news in news_list]
    vectorizer = TfidfVectorizer(min_df=2, decode_error='ignore', sublinear_tf=True)
    feature_vector = vectorizer.fit_transform(news_list_word_cut)

    score_list = list()
    for i in range(2,len(news_list)):
        print 'k-menas k',i
        km = KMeans(n_clusters=i, init='k-means++', max_iter=100, n_init=1, )
        km.fit(feature_vector)
        # print metrics.calinski_harabaz_score(feature_vector.toarray(), km.labels_)
        print km.labels_
        score = metrics.silhouette_score(feature_vector.toarray(), km.labels_, metric='euclidean')
        score_list.append((i, score))

    sorted_score = sorted(score_list, key=lambda x:x[1], reverse=True)
    cluster_num = sorted_score[0][0]
    print 'news number:', len(news_list)
    print 'cluster number:', cluster_num

    km = KMeans(n_clusters=cluster_num, init='k-means++', max_iter=100, n_init=1, )
    km.fit(feature_vector)
    cluster_dict = dict()
    for i in range(len(km.labels_)):
        labeled_news = cluster_dict.setdefault(km.labels_[i], list())
        labeled_news.append(news_list[i])

    return cluster_dict, score_list

def keywordProfile(news_list, topn=10):

    risk_keyword_count = 0 ###风险新闻数量

    keyword_filt_dict = utils.get_stop_word_dict('./sys/keyword.filt')
    ###step1:获取前20的keywords
    sorted_keywords = newsList_keywords_static(news_list)
    risk_keyword = risk_keyword_flit(sorted_keywords, keyword_filt_dict, topn = topn)

    risk_keyword_dict = {key[0]:key[1] for key in risk_keyword}
    ###step2:统计关键词下风险新闻：
    keyword_newsList = dict() ###{keyword:[(newsID,weight,content), (newsID,weight,content)]}
    for news_json in news_list:
        newsID = news_json['id']
        keyword_list = news_json['keywords']

        if news_json['risk_label'] == '0':
            continue
        risk_keyword_count += 1
        for keyword in keyword_list:
            if keyword[0] in risk_keyword_dict:
                newsList = keyword_newsList.setdefault(keyword[0], list())
                # print newsID
                if news_json['content']:
                    content = (news_json['title'] + u' ' +  news_json['content'])
                else:
                    content = (news_json['title'] + u' ' +  news_json['title'])

                newsList.append([newsID, keyword[1], content, news_json['title'], news_json['news_link'], news_json['source']])

    ###step3：对关键词词下新闻进行聚类
    keyword_string = ''
    keyword_info_list = list()
    for key in risk_keyword:
        keyword = key[0]
        keyword_score = key[1]/risk_keyword_count
        keyword_info_dict = dict()
        keyword_info_dict['socre'] = keyword_score

        keyword_string += keyword + ' '

        news_list = keyword_newsList[keyword]
        # print news_list
        # print len(news_list)
        if len(news_list) >2:
            clustered_news, score_list = news_clust(news_list)
            sorted_cluster = sorted(clustered_news.items(), key=lambda x:len(x[1]), reverse=True)
        else:
            sorted_cluster = [['0', news_list]]
        keyword_info_dict['cluster'] = sorted_cluster

        keyword_info_list.append((keyword, keyword_info_dict))

    print 'keywords: %s' %keyword_string
    return keyword_info_list

def topic_score_sorted(news_list, topn = 10):

    topic_score = dict()
    risk_keyword_count = 0
    for news_json in news_list:
        newsID = news_json['id']
        if news_json['risk_label'] == '0':
            continue

        risk_keyword_count += 1
        topic_vec = news_json['topic']
        for i in range(len(topic_vec)):
            topic_score[i] = topic_score.get(i, 0) + float(topic_vec[i])

    topic_score = {k:v/risk_keyword_count for k,v in topic_score.items()}

    sorted_topic_score = sorted(topic_score.items(), key= lambda x:x[1], reverse=True)

    return sorted_topic_score[:topn]

def topicProfile(news_list, topn = 5, topic_news_num = 2):


     ###step1:获取前10的topic
    sorted_topics = topic_score_sorted(news_list, topn = topn)

    sorted_topics_dict = {key[0]:key[1] for key in sorted_topics}
    ###step2:统计话题下风险新闻：
    topic_newsList = dict() ###{topic:[(newsID,weight,content), (newsID,weight,content)]}
    for news_json in news_list:
        newsID = news_json['id']
        topic_vec = news_json['topic']

        if news_json['risk_label'] == '0':
            continue
        # print topic_vec
        for i in range(len(topic_vec)):
            if i in sorted_topics_dict:
                newsList = topic_newsList.setdefault(i, list())
                # print newsID
                if news_json['content']:
                    content = (news_json['title'] + u' ' +  news_json['content'])
                else:
                    content = (news_json['title'] + u' ' +  news_json['title'])

                newsList.append([newsID, float(topic_vec[i]), content, news_json['title'], news_json['news_link'], news_json['source']])
    #
    ###step3：提取话题下得分最高的2个新闻
    topic_info_list = list()
    topic_string = ''
    for key in sorted_topics:
        topic = key[0]

        keyword_info_dict = dict()
        keyword_info_dict['socre'] = key[1]

        topic_string += '%d '%topic

        news_list = topic_newsList[topic]
        sorted_news_list = sorted(news_list, key=lambda x:x[1], reverse=True)
        keyword_info_dict['news'] = sorted_news_list[:topic_news_num]

        topic_info_list.append((topic, keyword_info_dict))
    print 'topics: %s' %topic_string
    return topic_info_list

def city_profile(news_list, topn = 5, topic_news_num = 2):
    '''
    对一个城市一段时间内的news_list进行画像
    '''
    keyword_profile = keywordProfile(news_list, topn=10)
    topic_profile = topicProfile(news_list, topn = topn, topic_news_num = topic_news_num)

    return (keyword_profile, topic_profile)

def save_city_profile(city_tuple, keyword_profile, topic_profile, date_string, save_basepath, encoding = 'gbk'):
    # for i in range(len(city_tuple_list)):
    province = city_tuple[0]
    city = city_tuple[1]

    city_path = (u'%s/%s/%s'%(save_basepath, province, city)).encode(encoding)
    if not os.path.exists(city_path):
        os.makedirs(city_path)

    keyword_profile_path = (u'%s/%s/%s/%s.keywordProfile'%(save_basepath, province, city, date_string)).encode(encoding)
    open(keyword_profile_path, 'w').write(json.dumps(keyword_profile, indent=4, ensure_ascii=False))

    topic_profile_path = (u'%s/%s/%s/%s.topicProfile'%(save_basepath, province, city, date_string)).encode(encoding)
    open(topic_profile_path, 'w').write(json.dumps(topic_profile, indent=4, ensure_ascii=False))

def daily_city_profile(cityProfile_tuple_list, date_string, news_profile_basepath, city_profile_basepath, path_encoding = 'gbk'):
    print '=============开始城市画像====================='
    city_profile_list = list()
    for i in range(len(cityProfile_tuple_list)):
        province = cityProfile_tuple_list[i][0]
        city = cityProfile_tuple_list[i][1]
        print 'province, city: %s, %s'%(province, city)
        news_profile_path = news_profile_basepath + province + u'/' + city + u'/' + date_string + '.newsProfile'
        # print news_profile_path

        news_list = [json.loads(line.strip())  for line in open(news_profile_path.encode(path_encoding))]

        keyword_profile, topic_profile = city_profile(news_list, topn = 5, topic_news_num = 2)
        save_city_profile(cityProfile_tuple_list[i], keyword_profile, topic_profile, date_string = date_string,save_basepath = city_profile_basepath, encoding = path_encoding)

        city_profile_list.append((keyword_profile, topic_profile))

    return city_profile_list

if __name__ == '__main__':
    '''
    reserved_word_path = conf.BaseConf.RESERVEDWORD
    city_tuple_list = [(u'北京',u'北京')]
    city_news_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_xml/'

    cityTuple_newsList = period_cityTuple_news_profile(city_tuple_list, city_news_basepath, start_date = '2017-04-06', end_date = '2017-04-06',  model_basepath = './model', topn = 10, reserved_word_path = reserved_word_path)
    '''
    '''
    newsProfilePath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_profile/重庆/重庆/2017-06-02.newsProfile'.encode('gbk')
    news_list = [json.loads(line.strip()) for line in open(newsProfilePath, 'r')]

    keyword_profile = keywordProfile(news_list)
    open('temp.data', 'w').write(json.dumps(keyword_profile, indent=4, ensure_ascii=False))
    topic_profile = topicProfile(news_list)
    open('temp2.data', 'w').write(json.dumps(topic_profile, indent=4, ensure_ascii=False))
    city_tuple_list = [(u'重庆',u'重庆')]
    save_city_profile(city_tuple_list[0], keyword_profile, topic_profile, date_string = '2017-06-02',save_basepath=u'E:/ypj/running_spider/baidu_spider/spider_v3.2/city_day_profile/')
    '''

    ###测试daily_city_profile
    cityProfile_tuple_list = [(u'北京', u'北京')]
    date_string = '2017-06-16'
    news_profile_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/news_day_profile/'
    city_profile_basepath = u'E:/ypj/running_spider/baidu_spider/spider_v3.2/city_day_profile/'

    daily_city_profile(cityProfile_tuple_list, date_string, news_profile_basepath, city_profile_basepath )


