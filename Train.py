import json
import os
import re
import jieba
import joblib
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# train.py
from tokenizer import jieba_tokenizer


class GenerPoemClassification:
    def __init__(self):
        self.poem_classification_path = "model/poem_classification.json"
        if not os.path.exists("model"):
            os.makedirs("model")
        if not os.path.isfile(self.poem_classification_path):
            self.save_classification()

    def save_classification(self):
        """这部分 dict 需要和训练数据顺序对应"""
        dic = {
            '0': 'nr 某人写过什么诗',
            '1': 'nm 某诗是某人写的',
            '2': 'nt 某朝代有哪些诗人',
            '3': 'nr 某诗人生活在哪个朝代',
            '4': 'nm 按诗名查询某诗内容',
            '5': 'nm 某诗描写某标签',
            '6': 'x 某诗句出自某朝代某诗人写作的某诗',
            '7': 'nz 某标签的诗有哪些'
        }
        with open(self.poem_classification_path, 'w', encoding='utf8') as f:
            json.dump(dic, f, ensure_ascii=False)
        print("分类字典已保存到 model/poem_classification.json")

class Trainer:
    def __init__(self):
        self.data_path = "./poemData/trainData"
        self.poem_classification_path = "model/poem_classification.json"
        self.vectorizer = TfidfVectorizer(tokenizer=jieba_tokenizer, ngram_range=(1,2), max_features=5000)
        self.classification_dict = self.load_classification()

    def load_classification(self):
        with open(self.poem_classification_path, "r", encoding="utf-8") as f:
            classification_dict = json.load(f)
        return classification_dict

    def load_data(self):
        X = []
        Y = []
        list_file = os.listdir(self.data_path)
        for file_name in list_file:
            file_path = os.path.join(self.data_path, file_name)
            match = re.match(r'【(\d+)】', file_name)
            if match:
                label = match.group(1)
                with open(file_path, 'r', encoding='utf-8') as fread:
                    for line in fread:
                        line = line.strip()
                        if line:
                            Y.append(label)
                            X.append(line)
        return X, Y

    def train(self):
        X, Y = self.load_data()
        print(f"训练数据加载完成，样本数量: {len(X)}")
        
        # 检查各类别的样本数量
        counter = Counter(Y)
        print(f"各类别样本数量: {counter}")

        # 转换标签为整数索引
        labels = sorted(set(Y))
        label_map = {label: idx for idx, label in enumerate(labels)}
        Y_int = [label_map[y] for y in Y]

        # 划分数据集
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y_int, test_size=0.2, random_state=42)

        # 向量化
        X_train_vect = self.vectorizer.fit_transform(X_train)
        X_test_vect = self.vectorizer.transform(X_test)
        joblib.dump(self.vectorizer, 'model/tfidf_vectorizer.joblib')
        print("TF-IDF 向量器已保存到 model/tfidf_vectorizer.joblib")

        # 训练分类器
        model = MultinomialNB()
        model.fit(X_train_vect, Y_train)
        joblib.dump(model, 'model/model.model')
        print("模型训练完成，已保存到 model/model.model")

        # 测试模型准确率
        self.evaluate(model, X_test_vect, Y_test, label_map)

    def evaluate(self, model, X_test_vect, Y_test, label_map):
        Y_pred = model.predict(X_test_vect)
        accuracy = accuracy_score(Y_test, Y_pred)
        print(f"模型在测试集上的准确率: {accuracy:.2%}")
        
        # 获取所有可能的类别编号，确保与标签一致
        labels = sorted([int(label) for label in self.classification_dict.keys()])
        target_names = [self.classification_dict[str(label)] for label in labels]
        
        print("\n每类分类结果:")
        print(classification_report(Y_test, Y_pred, labels=labels, target_names=target_names, digits=2, zero_division=0))


if __name__ == "__main__":
    gpc = GenerPoemClassification()
    t = Trainer()
    t.train()
