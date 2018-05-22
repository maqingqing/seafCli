function progress(repo_id){

    var timerId = setInterval(function(){getCurrentProgress(repo_id)}, 1000);
    function setRate(download_rate, upload_rate){
        $('#upload_rate').text("upload rate: " + upload_rate);
        $('#download_rate').text("download rate: " + download_rate);
    }
    function getCurrentProgress(repo_id) {
        $.get( "/repo/progress?repo_id="+ repo_id,function(data){
            console.log(data);
            setRate(data.download_rate, data.upload_rate);

            $("[data-progressname=" + repo_id + "]").each(function(index,progressbar){

                console.log(index,$(progressbar));
                if(data.rate){
                    $(progressbar).next().text(data.rate);
                }else{
                    $(progressbar).next().text("0.0 KB/s");
                }
                if (data.state == "downloading" || data.state == "waiting for sync" || data.state == "uploading" || data.state == "checkout") {
                    $(progressbar).parent().prev().prev().text(data.state);
                    if(data.progress > 0){
                        $(progressbar).progressbar('setValue', data.progress);
                    }

                    if ($(progressbar).progressbar('getValue') == 100) {
                        clearInterval(timerId);
                        refreshTab();
                    }
                }else if (data.state == "unknown") {
                    $(progressbar).parent().prev().prev().text("unknown");
                    clearInterval(timerId);
                    $(progressbar).next().remove();
                    setRate("0.0 KB/s", "0.0 KB/s");
                }else if (data.state == "error") {
                    $(progressbar).parent().prev().prev().text("error:" + data.message);
                    clearInterval(timerId);
                    $(progressbar).next().remove();
                    setRate("0.0 KB/s", "0.0 KB/s");
                }else if (data.state == "finish" || data.state == "synchronized"){
                    refreshTab();
                    clearInterval(timerId);
                }else{
                    $(progressbar).parent().prev().prev().text(data.state);
                }
              });
         });
    }
}

function refreshTab(){
    console.log('refresh');
    var current_tab = $('#library_tabs').tabs('getSelected');
    $('#library_tabs').tabs('update',{
         tab:current_tab,
         options : {
              href : '/repo?page=' + current_tab.panel('options').title,
         }
    });
    current_tab.panel('refresh');
}



