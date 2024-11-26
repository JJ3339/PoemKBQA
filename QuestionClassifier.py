import json

import jieba
import jieba.posseg as pseg
import joblib
import numpy as np

import jieba

from tokenizer import jieba_tokenizer
class PoemQuestionClassifier:
    def __init__(self):
        self.abstractMap = {}
        self.model_path = 'model/model.model'
        self.vectorizer_path = 'model/tfidf_vectorizer.joblib'
        self.poem_classification_path = 'model/poem_classification.json'
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        self.question_class = self.load_question_classification()

    def load_question_classification(self):
        with open(self.poem_classification_path, "r", encoding='utf-8') as f:
            question_classification = json.load(f)
        return question_classification

    def abstract_question(self, question):
        self.abstractMap = {}  # 重置抽象映射
        # 加载自定义字典
        jieba.load_userdict('poemData/txt/author.txt')
        jieba.load_userdict('poemData/txt/content.txt')
        jieba.load_userdict('poemData/txt/dynasty.txt')
        jieba.load_userdict('poemData/txt/poem.txt')
        jieba.load_userdict('poemData/txt/tag.txt')
        jieba.initialize()  # 强制重新初始化 jieba

        # 添加标签词语
        tag_words = ['月', '春', '夏', '秋', '冬', '花', '雪', '山', '水', '离别', '思乡', '爱情', '边塞']
        for word in tag_words:
            jieba.add_word(word, freq=9999999, tag='nz')

        print("自定义词典已加载，并已添加词语")
        # 进行分词和词性标注，设置 HMM=False
        list_word = pseg.lcut(question, HMM=False)
        abstractQuery = ''
        for item in list_word:
            word = item.word
            pos = item.flag
            print(f"词：{word}，词性：{pos}")  # 添加打印，调试用
            if 'nm' in pos:
                abstractQuery += "nm "
                self.abstractMap['nm'] = word
            elif 'nr' in pos:
                abstractQuery += "nr "
                self.abstractMap['nr'] = word
            elif 'nt' in pos:
                abstractQuery += "nt "
                self.abstractMap['nt'] = word
            elif 'nz' in pos:
                abstractQuery += "nz "
                self.abstractMap['nz'] = word
            elif 'x' in pos:
                abstractQuery += "x "
                self.abstractMap['x'] = word
            else:
                abstractQuery += word + " "
        print(f"抽象化结果：{abstractQuery}")
        print(f"抽象映射：{self.abstractMap}")
        return abstractQuery.strip()


    def query_classify(self, sentence):
        # 使用加载的向量化器进行特征提取
        X = self.vectorizer.transform([sentence])
        prediction = self.model.predict(X)[0]
        return int(prediction), self.question_class[str(prediction)]

    def query_extention(self, temp):
        params = []
        for abs_key in self.abstractMap:
            if abs_key in temp:
                params.append(self.abstractMap[abs_key])
        return params

    def analysis_question(self, question):
        abstr = self.abstract_question(question)
        index, strpatt = self.query_classify(abstr)
        print('句子对应的索引{}\t模板：{}'.format(index, strpatt))
        finalpatt = self.query_extention(strpatt)
        return index, finalpatt



if __name__ == "__main__":
    pqc = PoemQuestionClassifier()
    question = input('请输入你想查询的信息：')
    index, params = pqc.analysis_question(question)
    print(index, params)
