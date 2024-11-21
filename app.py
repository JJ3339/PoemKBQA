import os

from flask import Flask, request, jsonify, render_template
from QuestionClassifier import PoemQuestionClassifier
from get_answer import GetAnswer

app = Flask(__name__)

# 初始化问答系统
pqc = PoemQuestionClassifier()
ga = GetAnswer()
# 静态文件路径
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'answer': '请输入问题'})

    try:
        index, params = pqc.analysis_question(question)
        answers = ga.get_data(index, params[0])
    except IndexError:
        return jsonify({'answer': '暂时不知道答案'})
    #回答
    if answers:
        # 格式化答案（与 GUI 逻辑相同）
        if index == 0:
            result = list(set([answer['p.name'] for answer in answers]))
        elif index == 1:
            result = answers[0]['a.name']
        elif index == 2:
            result = list(set([answer['a.name'] for answer in answers]))
        elif index == 3:
            result = answers[0]['d.name']
        elif index == 4:
            lis = []
            for i in answers:
                if i not in lis:
                    lis.append(i)
            result = []
            for item in lis:
                result_str = f"《{item['p.name']}》\n\n{item['d.name']}·{item['a.name']}\n\n" + \
                             item['p.content'].replace('。', '。\n').replace('，', '，\n') + "\n" + "-" * 30 + "\n"
                result.append(result_str)
        elif index == 5:
            result = list(set([answer['t.name'] for answer in answers]))
        elif index == 6:
            lis = []
            for i in answers:
                if i not in lis:
                    lis.append(i)
            result = []
            for item in lis:
                result_str = f"出自 {item['d.name']} 的诗人 {item['a.name']} 写作的：\n《{item['p.name']}》\n\n" + \
                             "完整内容：\n" + item['p.content'].replace('。', '。\n').replace('，', '，\n') + "\n" + "-" * 30 + "\n"
                result.append(result_str)
        else:
            result = False

        if result:
            if isinstance(result, list):
                # 将列表中的每个元素连接，并在每个元素之间插入 <br> 标签
                return jsonify({'answer': "<br>".join([item.replace('\n', '<br>') for item in result])})
            else:
                # 如果是单个字符串，直接替换换行符为 <br> 标签
                return jsonify({'answer': result.replace('\n', '<br>')})
    return jsonify({'answer': '暂时不知道答案'})

@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    """
    接收自然语言查询，生成知识图谱并返回文件路径
    """
    data = request.get_json()
    natural_language_query = data.get('query', '')
    # return jsonify({'error': natural_language_query})
    if not natural_language_query:
        return jsonify({'error': '请输入有效的查询'})

    try:
        # 解析自然语言，获取索引和参数
        index, params = pqc.analysis_question(natural_language_query)

        # 根据索引和参数生成 Cypher 查询
        cypher_query = ga.generate_cypher_query(index, params[0])

        if not cypher_query:
            return jsonify({'error': '无法解析问题，请尝试重新输入'})

        # 生成知识图谱文件
        output_file = os.path.join(STATIC_DIR, "graph.html")
        ga.generate_knowledge_graph(cypher_query, output_file)

        # 返回前端可访问的图谱路径
        return jsonify({'graph_url': f'/static/graph.html'})
    except IndexError:
        return jsonify({'error': '暂时无法回答此问题，请稍后重试'})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
