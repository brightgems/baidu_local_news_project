#coding:utf-8
import utils

def generateKeywordProfileInMail(keyword_profile, date_string, city):
    '''
    根据凤霞关键词生成邮件中的html
    :param keyword_profile:
    :param date_string:
    :param city:
    :return:
    '''
    keyword_tables = ''
    keyword_count = 0
    for key in keyword_profile:
        # print keyword_profile
        keyword_count += 1
        # print key[0]
        keyword = key[0]
        keyword_info_dict = key[1]
        keyword_score = keyword_info_dict['socre'] #float
        news_info_tr = ''
        for cluster_news in keyword_info_dict['cluster']:
            cluster_num = cluster_news[0]
            news_in_cluster = cluster_news[1]
            for news in news_in_cluster:
                news_score = news[1]
                news_source = news[5]
                news_title = news[3]
                news_link = news[4]
                news_info_tr += "<tr>\
						<td height='30' width='5%%'><center><font size='4'>%s</font></center></td>\
						<td width='20%%'><center><font size='4'>%.4f</font></center></td>\
						<td width='15%%'><center><font size='4'>%s</font></center></td>\
						<td width='60%%'><center><font size='4'><a href = '%s' target = '_blank'>%s</a></font></center></td>\
					  </tr>"%(cluster_num, news_score, news_source, news_link, news_title)
        news_info_table = "<table width='900' align='left' border='1' cellpadding='0' cellspacing='0'>\
					  <tr>\
						<td height='30' width='5%%'><center><font size='4'><b>类号</b></font></center></td>\
						<td width='20%%'><center><font size='4'><b>关键词在新闻中得分</b></font></center></td>\
						<td width='15%%'><center><font size='4'><b>新闻来源</b></font></center></td>\
						<td width='60%%'><center><font size='4'><b>新闻标题</b></font></center></td>\
					  </tr>%s\
					  </table>"%news_info_tr
        keyword_tables += "<table width='900' align='left' border='0' >\
                      <tr><td><font><b>Top%d: &nbsp; %s（%.4f）</b></font></td></tr>\
                      <tr></tr>\
                      <tr><td>%s</td></tr>\
                      <tr></tr>\
                      <tr></tr>\
                      </table>"%(keyword_count, keyword, keyword_score, news_info_table)
    keyword_profile_table_string = "<tr><td align='center' height='50'><font size='3'><b>%s风险关键词画像（%s）</b></font></td></tr>\
                                    <tr><td>%s</td></tr>"%(city, date_string, keyword_tables)

    return keyword_profile_table_string

def generateTopicProfileInMail(topic_profile, date_string, city):
    '''
    根据风险话题生成邮件中的html
    :param topic_profile:
    :param date_string:
    :param city:
    :return:
    '''

    topic_tables = ''
    topic_count = 0
    for key in topic_profile:
        topic_count += 1

        topic= key[0]

        topic_info_dict = key[1]
        topic_score = topic_info_dict['socre'] #float
        news_info_tr = ''
        news_count = 0
        for news in topic_info_dict['news']:
            # for news in news_in_topic:
            news_count += 1
            news_score = float(news[1])
            news_source = news[5]
            news_title = news[3]
            news_link = news[4]
            news_info_tr += "<tr>\
					<td height='30' width='5%%'><center><font size='4'>%d</font></center></td>\
					<td width='20%%'><center><font size='4'>%.4f</font></center></td>\
					<td width='15%%'><center><font size='4'>%s</font></center></td>\
					<td width='60%%'><center><font size='4'><a href = '%s' target = '_blank'>%s</a></font></center></td>\
				  </tr>"%(news_count, news_score, news_source, news_link, news_title)
        news_info_table = "<table width='900' align='left' border='1' cellpadding='0' cellspacing='0'>\
					  <tr>\
						<td height='30' width='5%%'><center><font size='4'><b>编号</b></font></center></td>\
						<td width='20%%'><center><font size='4'><b>新闻在话题上概率值</b></font></center></td>\
						<td width='15%%'><center><font size='4'><b>新闻来源</b></font></center></td>\
						<td width='60%%'><center><font size='4'><b>新闻标题</b></font></center></td>\
					  </tr>%s\
					  </table>"%news_info_tr
        topic_tables += "<table width='900' align='left' border='0' >\
                      <tr><td><font><b>Top%d: &nbsp; topic%s（%.4f）</b></font></td></tr>\
                      <tr></tr>\
                      <tr><td>%s</td></tr>\
                      <tr></tr>\
                      <tr></tr>\
                      </table>"%(topic_count, topic, topic_score, news_info_table)
    keyword_profile_table_string = "<tr><td align='center' height='50'><font size='3'><b>%s风险话题画像（%s）</b></font></td></tr>\
                                    <tr><td>%s</td></tr>"%(city, date_string, topic_tables)

    return keyword_profile_table_string

def htmlGenerator(date, sorted_city_newscount, sorted_city_risklevel, cityProfile_tuple_list, city_profile_list):
    table_content = "<tr><td height='30' width='5%'><center><font size='4'><b>序号</b></font></center></td><td width='20%'><center><font size='4'><b>城市</b></font></center></td><td width='30%'><center><font size='4'><b>新闻数量</b></font></center></td><td width='20%'><center><font size='4'><b>城市</b></font></center></td><td width='30%'><center><font size='4'><b>风险水平</b></font></center></td></tr>"

    if not len(sorted_city_risklevel) == len(sorted_city_newscount):
        mail_content = "error!\r\nsorted_city_newscount len:%d\r\n:sorted_city_risklevel:%d"%(len(sorted_city_newscount), len(sorted_city_risklevel))
        return mail_content
    for i in range(len(sorted_city_newscount)):
        table_content += "<tr><td height='30' width='5%%'><center><font size='4'><b>%d</b></font></center></td>" \
                         "<td width='20%%'><center><font size='4'>%s</font></center></td>" \
                         "<td width='30%%'><center><font size='4'>%d</font></center></td>" \
                         "<td width='20%%'><center><font size='4'>%s</font></center></td>" \
                         "<td width='30%%'><center><font size='4'>%f</font></center></td></tr>"%(i,sorted_city_newscount[i][0].encode('utf-8'),sorted_city_newscount[i][1],sorted_city_risklevel[i][0].encode('utf-8'),sorted_city_risklevel[i][1])

    profile_table_content = ''

    # print len(city_profile_list)
    # print len(cityProfile_tuple_list)
    for i in range(len(cityProfile_tuple_list)):#每个城市

        # print '#'*20
        # print i
        # print cityProfile_tuple_list
        # print cityProfile_tuple_list[i]

        city = cityProfile_tuple_list[i][1].encode('utf-8')

        keyword_profile = city_profile_list[i][0]
        topic_profile = city_profile_list[i][1]
        profile_table_content += generateKeywordProfileInMail(keyword_profile, date, city)
        profile_table_content += generateTopicProfileInMail(topic_profile, date, city)

    # print profile_table_content

    mail_content = "<html><body><table width='600' align='left' border='0' cellpadding='0' cellspacing='0'>" \
              "<tr><td align='center' height='50'><font size='3'><b>百度城市新闻数量及风险水平（%s）</b></font></td></tr>" \
              "<tr><td><table width='900' align='left' border='1' cellpadding='0' cellspacing='0'>%s</table></tr>%s</table></body></html>"%(date,table_content, profile_table_content)


    return mail_content

def daily_reminder(email_list, yesterday_date_string, sorted_city_newscount, sorted_city_risklevel, city_remender_tuple_list, city_profile_list):
    '''将每天的的风险画像进行推送'''
    print '===============开始邮件推送=================='
    mail_content = htmlGenerator(yesterday_date_string, sorted_city_newscount, sorted_city_risklevel, city_remender_tuple_list, city_profile_list)
    utils.post_Reminder(mail_content, email_list)
    print 'done!'
    print '===============邮件推送完成=================='
