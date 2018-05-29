/**
 * Created by qingqing on 18-5-29.
 */


        //sync和pull方法
    function sync(ele){
        //获取请求路径 sync或者download
        var reqUrl = $(ele).attr('data-url');
        //获取资料库的id
        var repo_id = $(ele).attr('data-repoid');
        var sync_path = $(ele).parent().siblings('.modal-body').children('.sync_path').val();
        //如果是加密资料库，则获取输入的密码
        if($(this).parent().siblings('.modal-body').children('.sync_pass')){
            var passwd = $(ele).parent().siblings('.modal-body').children('.sync_pass').val();
        }
        console.log(reqUrl, repo_id,sync_path,passwd);
        syncAjax(reqUrl,repo_id,sync_path,passwd);

        function syncAjax(url,repo_id,sync_path,passwd){
            $.post(url,{'repo_id':repo_id, 'path': sync_path, 'passwd': passwd},function(data){
                console.log(data);
                if (data.state == 1){
                    refreshTab();
                }else {
                    alert("Failed\n" + data.res);
                }
            });
        }

    }


    //取消同步的方法
    function desync(ele){
        console.log('desync');
        var sync_path = $(ele).attr('data-syncpath');
        $.get("/desync?path="+ sync_path,function(data){
            refreshTab();
        });
    }


     function cancel(e) {
        console.log('cancle');
        var repo_id = e.getAttribute('data-repoid');
        $.get("/cancel?repoid="+ repo_id,{repoid:repo_id}, function(data){
                if(data.state == 1){
                    refreshTab();
                }
                else{
                    alert("Failed\n" + data.res)
                }

        });
    }


    function addLibrary(e) {
        alert("please wait")
    }

    function file_list(ele){
        var list = $(ele).attr('data-file');
        var option_url = "href : '"+list+"'";
        console.log(option_url);
        $(ele).parents('.table-responsive').parent().attr('data-options',option_url);
    }

