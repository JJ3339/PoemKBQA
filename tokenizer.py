# tokenizer.py
import jieba

def jieba_tokenizer(text):
    return jieba.lcut(text)
