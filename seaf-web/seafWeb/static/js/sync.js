/**
 * Created by qingqing on 18-5-18.
 */
function sync(e){
    console.log('sync');
        var sync_path = prompt("请输入路径:");
        var passwd;
        if(e.encrypt){
            passwd = prompt("请输入密码:");
        }
        $.post("/sync",{'repo_id':e.getAttribute('data-repoid'), 'path': sync_path, 'passwd': passwd},function(data){
            if (data.state == 1){
                $.messager.alert('提示', sync_path + "正在于" + e.getAttribute('data-reponame') +"绑定同步", 'info', function() {
                    //window.parent.location.reload(true);
                    refreshTab()
                });
            }else if(data.state == -1){
                passwd = prompt("请输入密码:");
                $.post("/sync",{'repo_id':e.getAttribute('data-repoid'), 'path': sync_path, 'passwd': passwd},function(data){
                    if(data.state == 1){
                        $.messager.alert('提示', sync_path + "正在于" + e.getAttribute('data-reponame') +"绑定同步", 'info', function() {
                            //window.parent.location.reload(true);
                            refreshTab();
                        });
                    }else {
                        alert("Failed\n" + data.res);
                    }});
            }else {
                alert("Failed\n" + data.res);
            }
        });
    }


    function desync(e) {
    console.log('desync');
        sync_path = e.getAttribute('data-syncpath');
        $.get("/desync?path="+ sync_path,function(data){
                $.messager.alert('提示', sync_path + "已解除同步", 'info', function() {
                        //window.parent.location.reload(true);
                        refreshTab();
                    });
        });
    }

     function cancel(e) {
        repo_id = e.getAttribute('data-repoid')
        $.get("/cancel?repoid="+ repo_id,function(data){
                if(data.state == 1){
                    $.messager.alert('提示',  "已取消同步", 'info', function() {
                        //window.parent.location.reload(true);
                        refreshTab();
                    });
                }
                else{
                    alert("Failed\n" + data.res)
                }

        });
    }


    function addLibrary(e) {
        alert("please wait")
    }


    function download(e) {
        var download_dir = prompt("请输入路径:");
        var passwd;

        $.post("/repo/download",{'repo_id':e.getAttribute('data-repoid'), 'download_dir': download_dir, 'passwd': passwd},function(data){
            if (data.state == 1){
                 $.messager.alert('提示', "资料库正在下载在" + download_dir +",并绑定同步", 'info', function() {
                        //window.parent.location.reload(true);
                        refreshTab();
                });
            }else if(data.state == -1){
                passwd = prompt("请输入密码:");
                $.post("/repo/download",{'repo_id':e.getAttribute('data-repoid'), 'download_dir': download_dir, 'passwd': passwd},function(data){
                    if (data.state == 1){
                        $.messager.alert('提示', "资料库正在下载在" + download_dir +",并绑定同步", 'info', function() {
                            //window.parent.location.reload(true);
                            refreshTab();
                        });
                    }else {
                        alert("Failed\n" + data.res);
                    }});
            }else {
                alert("Failed\n" + data.res);
            }
        });
    }