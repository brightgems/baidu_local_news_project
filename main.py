#coding:utf-8
import datetime

import city_risklevel_profile

import utils
import conf
import place_data_process

import json
import news_profile
import city_profile
import mail_reminder


city_tuple_list = conf.ProfileConf.cityProfile_tuple_list
news_basepath = conf.BaseConf.NEWS_BASEPATH
news_profile_basepath = conf.BaseConf.NEWS_PROFILE_BASEPATH
city_profile_basepath = conf.BaseConf.CITY_PROFILE_BASEPATH
risklevel_profile_basepath = conf.BaseConf.RISKLEVEL_BASEPATH

stop_word_path = ''
encoding = conf.BaseConf.PATH_ENCODING
reserved_word_path = conf.BaseConf.RESERVEDWORD ###用于筛选城市关键词

city_remender_tuple_list = conf.ReminderConf.city_remender_tuple_list
reminde_time = conf.ReminderConf.reminde_time

while True:
    # utils.timer(conf.SpiderConf.SPIDER_HOUR_RUN_TIME)

    nowtime = datetime.datetime.now()
    if nowtime.hour == reminde_time: ###如果是7点，则进行邮件推送
    # if nowtime.hour == 22: ###如果是7点，则进行邮件推送
        yesterday_date_string = utils.get_yesterday_date_string()
        # yesterday_date_string = '2017-06-11'

        ###step1: 对每日的新闻进行统计，并预测风险类别，计算风险水平
        sorted_city_newscount, sorted_city_risklevel = city_risklevel_profile.daily_risklevel_profile(yesterday_date_string, city_tuple_list, place_news_base_path = news_basepath, risk_level_basepath = risklevel_profile_basepath, path_encoding = encoding)

        #step2: 计算每日的新闻画像，并保存到本地
        # news_profile.daily_news_profile(city_tuple_list, news_basepath, news_profile_basepath, yesterday_date_string, reserved_word_path, path_encoding=encoding)

        #step3: 计算每日城市风险画像
        city_profile_list = city_profile.daily_city_profile(city_tuple_list, yesterday_date_string, news_profile_basepath, city_profile_basepath, path_encoding = encoding )

        #step4: 对每日风险画像进行推送
        # email_list = ['xjtang@iss.ac.cn','wgcn1314@126.com','xunuo1991@amss.ac.cn','hebeijiayugai@126.com','xiqianghust@163.com','littlebiao@outlook.com','yuanpengjia@amss.ac.cn']
        email_list = ['yuanpengjia@amss.ac.cn']
        mail_reminder.daily_reminder(email_list, yesterday_date_string, sorted_city_newscount, sorted_city_risklevel, city_remender_tuple_list, city_profile_list)