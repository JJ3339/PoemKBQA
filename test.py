import json
import re
import jieba
import joblib

# 全局定义分词器函数
def jieba_tokenizer(text):
    return jieba.lcut(text)

def classify_query(query, model, vectorizer, label_map, classification_dict):
    # 简单规则优先分类
    if re.match(r'^带有.*的诗有哪些$', query) or re.match(r'^描写.*的诗有哪些$', query) or re.match(r'^关于.*的诗有哪些$', query):
        return 'nz 某标签的诗有哪些'  # 类别7
    # 如果不符合规则，交由模型预测
    X = vectorizer.transform([query])
    prediction = model.predict(X)[0]
    # 反向映射标签
    for label, idx in label_map.items():
        if idx == prediction:
            return classification_dict[label]
    return "未知类别"


from QuestionClassifier import PoemQuestionClassifier
from get_answer import GetAnswer

if __name__ == "__main__":
    pqc = PoemQuestionClassifier()
    ga = GetAnswer()
    while True:
        question = input('请输入你想查询的信息（输入"退出"结束）：')
        if question == '退出':
            break
        index, params = pqc.analysis_question(question)
        if not params:
            print("无法提取参数，暂时不知道答案")
            continue
        try:
            answers = ga.get_data(index, params[0])
        except IndexError:
            print("暂时不知道答案")
            continue
        print('答案:')
        if answers:
            print(answers)
        else:
            print("暂时不知道答案")
