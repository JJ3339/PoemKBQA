$(document).ready(function () {

    $('.loader').hide();
    // 提问部分
    $('#search-botton').click(function () {
        const question = $('#question').val().trim();

        $('#answer').addClass('d-none');

        if (!question) {
            //alert('请输入问题');
            $('#QAModal').modal()
            return;
        }

        $('.loader').show();
        // 向后端发送问题请求
        $.ajax({
            url: '/ask',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ question: question }),
            success: function (data) {
                //使用 .html() 方法渲染 HTML 内容，这样 <br> 标签才会生效
                $('.loader').hide();
                $('#answer').removeClass('d-none').html(data.answer);
            },
            error: function () {
                $('.loader').hide();
                $('#answer').removeClass('alert-success').addClass('alert-danger').html('发生错误，请稍后重试');
            }
        });
    });
    //


    // 生成知识图谱部分
    $('#generate-botton').click(function () {
        const cypherQuery = $('#query').val().trim();

        $('#graph-frame').addClass('d-none');
        if (!cypherQuery) {
            $('#GENModal').modal();
            return;
        }
        $('.loader').show();
        // 向后端发送生成图谱请求
        $.ajax({
            url: '/generate_graph',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ query: cypherQuery }),
            success: function (data) {
                if (data.graph_url) {
                    $('.loader').hide();
                    $('#graph-frame').removeClass('d-none').attr('src', data.graph_url);
                } else {
                    $('.loader').hide();
                    $('#GEN-ERROR-Modal').modal()
                    alert(data.error || '生成图谱失败');
                }
            },
            error: function () {
                alert('生成图谱时发生错误，请稍后重试');
            }
        });
    });
});
