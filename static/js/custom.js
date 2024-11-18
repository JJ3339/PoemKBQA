$(document).ready(function () {
    // 提问部分
    $('#ask-btn').click(function () {
        const question = $('#question').val().trim();

        if (!question) {
            alert('请输入问题');
            return;
        }

        // 向后端发送问题请求
        $.ajax({
            url: '/ask',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ question: question }),
            success: function (data) {
                $('#answer').removeClass('d-none').text(data.answer);
            },
            error: function () {
                $('#answer').removeClass('alert-success').addClass('alert-danger').text('发生错误，请稍后重试');
            }
        });
    });

    // 生成知识图谱部分
    $('#generate-btn').click(function () {
        const cypherQuery = $('#cypher-query').val().trim();

        if (!cypherQuery) {
            alert('请输入 Cypher 查询');
            return;
        }

        // 向后端发送生成图谱请求
        $.ajax({
            url: '/generate_graph',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ cypher_query: cypherQuery }),
            success: function (data) {
                if (data.graph_url) {
                    $('#graph-frame').removeClass('d-none').attr('src', data.graph_url);
                } else {
                    alert(data.error || '生成图谱失败');
                }
            },
            error: function () {
                alert('生成图谱时发生错误，请稍后重试');
            }
        });
    });
});
