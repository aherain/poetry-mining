# -*- coding: utf-8 -*-
import multiprocessing
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn import manifold

from matplotlib.font_manager import FontProperties

font = FontProperties(fname=r"/usr/local/share/fonts/simhei.ttf", size=14)

# mpl.rcParams['font.sans-serif'] = ['AR PL UMing CN']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 显示负号


class Analyzer(object):
    """
    authors: 作者列表
    tfidf_word_vector: 用tf-idf为标准得到的词向量
    w2v_word_vector: 用word2vector得到的词向量
    w2v_model: 用word2vector得到的model

    tfidf_word_vector_tsne: 降维后的词向量
    """

    def __init__(self, cut_result, saved_dir):
        target_file_path = os.path.join(saved_dir, 'analyze_result.pkl')
        if os.path.exists(target_file_path) and os.path.exists(target_file_path):
            print('load analyzed result.')
            # with open(target_file_path, 'rb') as f:
            #     self.authors = pickle.load(f)
        else:
            print('begin analyzing cut result...')
            # self.authors, self.tfidf_word_vector = self._author_word_vector(cut_result.author_poetry_dict)
            self.w2v_model, self.w2v_word_vector = self._word2vec(cut_result.author_poetry_dict)
            # self.word_vector_tsne = self.tsne()
            # with open(target_file_path, 'wb') as f:
            #     pickle.dump(result, f)

    @staticmethod
    def _author_word_vector(author_poetry_dict):
        """解析每个作者的词向量"""
        authors = list(author_poetry_dict.keys())
        poetry = list(author_poetry_dict.values())
        vectorizer = CountVectorizer(min_df=1)
        word_matrix = vectorizer.fit_transform(poetry).toarray()
        transformer = TfidfTransformer()
        tfidf_word_vector = transformer.fit_transform(word_matrix).toarray()
        return authors, tfidf_word_vector

    @staticmethod
    def _word2vec(author_poetry_dict):
        dimension = 400
        authors = list(author_poetry_dict.keys())
        poetry = list(author_poetry_dict.values())
        with open("cut_poetry", 'w') as f:
            f.write("\n".join(poetry))
        model = Word2Vec(LineSentence("cut_poetry"), size=dimension, min_count=5, workers=multiprocessing.cpu_count())
        word_vector = []
        for i, author in enumerate(authors):
            vec = np.zeros(dimension)
            words = poetry[i].split()
            count = 0
            for word in words:
                word = word.strip()
                try:
                    vec += model[word]
                    count += 1
                except KeyError:  # 有的词语不满足min_count则不会被记录在词表中
                    pass
            word_vector.append([v / count for v in vec])

        return model, word_vector

    @staticmethod
    def tsne(word_vector):
        t_sne = manifold.TSNE(n_components=2, init='pca', random_state=0)
        word_vector_tsne = t_sne.fit_transform(word_vector)
        return word_vector_tsne

    def find_similar_poet(self, poet_name):
        """
        通过词向量寻找最相似的诗人
        :param: poet: 需要寻找的诗人名称
        :return:最匹配的诗人
        """
        poet_index = self.authors.index(poet_name)
        x = self.tfidf_word_vector[poet_index]
        min_angle = np.pi
        min_index = 0
        for i, author in enumerate(self.authors):
            if i == poet_index:
                continue
            y = self.tfidf_word_vector[i]
            cos = x.dot(y) / (np.sqrt(x.dot(x)) * np.sqrt(y.dot(y)))
            angle = np.arccos(cos)
            if min_angle > angle:
                min_angle = angle
                min_index = i
        return self.authors[min_index]


def plot_vectors(X, target):
    """绘制结果"""
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)

    plt.figure()
    for i in range(X.shape[0]):
        plt.text(X[i, 0], X[i, 1], target[i],
                 # color=plt.cm.Set1(y[i] / 10.),
                 fontdict={'weight': 'bold', 'size': 8}
                 , fontproperties=font
                 )