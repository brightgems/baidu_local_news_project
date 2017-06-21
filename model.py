#coding:utf-8
from time import time
import json, os, csv
from xml.dom import minidom

from utils import *
import numpy as np
from hotword_data_process import prepare_train_data

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import chi2
from sklearn import svm
from sklearn import metrics


def X_vectorize(X_train, X_pridict):
    '''
    对训练数据和预测数据进行向量化
    :param X_train:训练数据，list形式，[一条样本，]，一条样本切词后结果，用空格分开
    :param X_pridict:需要预测的数据
    :return:向量化之后的训练数据和测试数据
    '''
    #----------------------对训练数据和测试数据进行向量化----------------------------
    vectorizer = TfidfVectorizer(min_df = 1, decode_error='ignore', sublinear_tf=True)
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_pridict_vectorized = vectorizer.transform(X_pridict)
    return X_train_vectorized, X_pridict_vectorized

def ch2_select(X_train_vectorized, y_train, X_pridict_vectorized, feature_percent=20):
    '''
    通过卡方对训练数据的特征进行选择，返回特征提取之后的向量
    :param X_train_vectorized:向量化后的X_train向量
    :param y_train:训练数据的向量List
    :param X_pridict_vectorized:向量化后的X_pridict向量
    :param feature_percent:要保留的特征比例，0-100的整数
    :return:特征选择之后的X_train_vectorized和X_pridict_vectorized向量
    '''
    ch2 = SelectPercentile(chi2, percentile=feature_percent)
    X_train_vectorized = ch2.fit_transform(X_train_vectorized, y_train)
    X_pridict_vectorized = ch2.transform(X_pridict_vectorized)

    return X_train_vectorized, X_pridict_vectorized

def train_model_pridict(X_train_vectorized, y_train, X_test_vectorized):
    '''
    练SVM模型，并预测需要预测的数据风险类别
    :param X_train_vectorized:训练数据特征向量
    :param y_train:训练舒服标签
    :param X_test_vectorized:预测数据特征向量
    :return:预测数据的预测结果
    '''
    clf = svm.LinearSVC()

    ###通过训练数据训练模型
    clf.fit(X_train_vectorized, y_train)###训练模型
    train_pred = clf.predict(X_train_vectorized)###训练训练集，计算训练集的准确率
    # print '     =====train metrics====='
    # print metrics.classification_report(y_train, train_pred)
    # print metrics.accuracy_score(y_train, train_pred)
    ###预测需要预测的数据

    test_pred = clf.predict(X_test_vectorized)
    # print '     =====test metrics====='
    # print metrics.classification_report(y_test, test_pred)
    # print metrics.accuracy_score(y_test, test_pred)
    return test_pred


def predict_acc():
    risk_basepath = './data/baidu_hotword/riskdata/'
    news_xml_basepath = './data/baidu_hotword/newsxml/'
    stop_word_path = ''
    span_predictdate_acc_dict = {}

    risk_basepath = './data/baidu_hotword/riskdata/'
    news_xml_basepath = './data/baidu_hotword/newsxml/'
    stop_word_path = './sys_data/stopwords.txt'

    start_time = '2016-08-01'
    end_time = '2016-10-31'
    date_span_list = range(3, 26)

    span_date_tuple_dict = generate_date_with_spans(start_time, end_time, date_span_list)

    for date_span in span_date_tuple_dict:
        train_date_dict = span_date_tuple_dict[date_span]
        predictdate_acc_dict = {}

        for date2predict in train_date_dict:
            train_start_date = train_date_dict[date2predict][0]
            train_end_date = train_date_dict[date2predict][1]

            train_id_list, train_label_list, train_content_list = zip(*prepare_train_data(train_start_date, train_end_date, risk_basepath, news_xml_basepath, stop_word_path))
            test_id_list, test_label_list, test_content_list = zip(*prepare_train_data(date2predict, date2predict, risk_basepath, news_xml_basepath, stop_word_path))

            y_train = label_8class_to_2class(train_label_list)
            y_test = label_8class_to_2class(test_label_list)

            ###向量化+特征选择
            X_train_vectorized, X_test_vectorized = X_vectorize(train_content_list, test_content_list)
            feature_percent = 20  # 通过卡方分布获得的特征比例
            X_train_vectorized, X_test_vectorized = ch2_select(X_train_vectorized, y_train, X_test_vectorized, feature_percent)

            y_test_predict = train_model_pridict(X_train_vectorized, y_train, X_test_vectorized)

            print '###########################span %d, date2predict %s###############################' %(date_span, date2predict)

            print metrics.classification_report(y_test, y_test_predict)
            acc = metrics.accuracy_score(y_test, y_test_predict)
            print acc

            predictdate_acc_dict[date2predict] = acc

        span_predictdate_acc_dict[date_span] = predictdate_acc_dict
    print span_predictdate_acc_dict

    csv_writer = csv.writer(file('hotword_bow_svm_acc.csv', 'wb'))

    date_list = generate_date_list(start_time, end_time)
    csv_writer.writerow([''] + date_list)
    for span in date_span_list:
        acc_list = [span]

        for date_string in date_list:
            acc_list.append(span_predictdate_acc_dict.setdefault(span, {}).setdefault(date_string, ''))

        csv_writer.writerow(acc_list)


if __name__ == '__main__':
    # risk_basepath = './data/baidu_hotword/riskdata/'
    # news_xml_basepath = './data/baidu_hotword/newsxml/'
    # stop_word_path = './sys_data/stopwords.txt'
    #
    # start_date_string = '2016-10-01'
    # end_date_string = '2016-10-09'
    # train_id_list, train_label_list, train_content_list = zip(*prepare_train_data(start_date_string, end_date_string, risk_basepath, news_xml_basepath, stop_word_path))
    # test_id_list, test_label_list, test_content_list = zip(*prepare_train_data('2016-10-10', '2016-10-10', risk_basepath, news_xml_basepath, stop_word_path))
    #
    # y_train = label_8class_to_2class(train_label_list)
    # y_test = label_8class_to_2class(test_label_list)
    #
    # ###向量化+特征选择
    # X_train_vectorized, X_test_vectorized = X_vectorize(train_content_list, test_content_list)
    # feature_percent = 20  # 通过卡方分布获得的特征比例
    # X_train_vectorized, X_test_vectorized = ch2_select(X_train_vectorized, y_train, X_test_vectorized, feature_percent)
    #
    # train_model_pridict(X_train_vectorized, y_train, X_test_vectorized, y_test)
    predict_acc()