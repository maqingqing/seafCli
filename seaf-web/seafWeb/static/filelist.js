/**
 * Created by qingqing on 18-5-29.
 */

$(function(){
    console.log($('#uploadbtn'));
    function fileChange(e){
        $("#fileTypeError").html('');
        var fileName = $('#file_upload').val();　　　　　　　　　　　　　　　　　　//获得文件名称
        alert(fileName);
        var repo_id = e.getAttribute('data-repoid');
        var current_dir = e.getAttribute('data-dir');

        $.get("/repo/file_list/upload",{'repo_id': repo_id, 'path': current_dir},function(data){
               if(data.state == 1){
                    console.log(data.url);
                    var formData = new FormData($('#uploadForm')[0]);
                    formData.append("filename", fileName);
                    formData.append("parent_dir", current_dir);
                    $.ajax({
                        url: data.url,　　　　　　　　　　//上传地址
                        type: 'POST',
                        cache: false,　　
                        data: formData,　　　　　　　　　　　　　//表单数据
                        processData: false,
                        contentType: false,
                        xhr: function(){ //这是关键 获取原生的xhr对象 做以前做的所有事情
                            var xhr = jQuery.ajaxSettings.xhr();
                            xhr.upload.onloadstart = function(){//上传开始执行方法
                                ot = new Date().getTime();   //设置上传开始时间
                                oloaded = 0;//设置上传开始时，以上传的文件大小为0
                            };
                            if(xhr.upload){
                                xhr.upload.onprogress = progressFunction;
                            }

                            return xhr;
                        }

                    }).done(function(resp) {
                         window.parent.location.reload(true)
                    }).fail(function(err) {
                        alert('无法连接服务器！')
                    });
               }
        })
    }
    //处理上传文件
    $('#file_upload').change(function(){
        fileChange($('#file_upload')[0]);
    });
    $('#uploadbtn').click(function(){
        $('#file_upload').click();
    });

     function progressFunction(evt) {

             //var progressBar = document.getElementById("progressBar");
             //var percentageDiv = document.getElementById("percentage");
             // event.total是需要传输的总字节，event.loaded是已经传输的字节。如果event.lengthComputable不为真，则event.total等于0
             if (evt.lengthComputable) {//
                 var percentComplete = Math.round(evt.loaded / evt.total * 100);
                 $("#processBar").css('width', percentComplete+'%');
                 $("#processBar").children('span').text(percentComplete+'%');
                 if(percentComplete == 100){
                    $("#processBar").css('width', "100%");
                    time.html('');
                    return;
                 }

             }

            var time = $("#time");
            var nt = new Date().getTime();//获取当前时间

            var pertime = (nt-ot)/1000; //计算出上次调用该方法时到现在的时间差，单位为s
            ot = new Date().getTime(); //重新赋值时间，用于下次计算

            var perload = evt.loaded - oloaded; //计算该分段上传的文件大小，单位b
            oloaded = evt.loaded;//重新赋值已上传文件大小，用以下次计算

            //上传速度计算
            var speed = perload/pertime;//单位b/s
            var bspeed = speed;
            var units = 'b/s';//单位名称
            if(speed/1024>1){
                speed = speed/1024;
                units = 'k/s';
            }
            if(speed/1024>1){
                speed = speed/1024;
                units = 'M/s';
            }
            speed = speed.toFixed(1);
            //剩余时间
            var resttime = ((evt.total-evt.loaded)/bspeed).toFixed(1);
            time.html('速度：'+speed+units+'剩余时间：'+resttime+'s');
               if(bspeed==0)
                time.html('上传已取消');
        }


    function get_upload_link(repo_id,current_dir){

        $.get("/repo/file_list/upload",{'repo_id': repo_id, 'path': current_dir},function(data){
               if(data.state == 1){
                    console.log(data.url);
                    return data.url;
               }
        })


    }


    function download(e){

        $.get("/repo/file_list/download",{'repo_id': e.getAttribute('data-repoid'), 'file_name': e.getAttribute('data-filename'),
                                            'file_type': e.getAttribute('data-filetype')},function(data){
               if(data.state == 1){
                    var $eleForm = $("<form method='get'></form>");
                    $eleForm.attr("action",data.download_url);
                    $(document.body).append($eleForm);
                    //提交表单，实现下载
                    $eleForm.submit();
               }
        })


    }
    //处理下载
    $('.downLoad').click(function(){
        download($(this)[0]);
    });

    function deleteFile(e){

        var delete_url = "/repo/file_list/download?" + "repo_id=" + e.getAttribute('data-repoid')
                        + "&file_name=" + e.getAttribute('data-filename') + "&file_type=" + e.getAttribute('data-filetype');
        $.ajax({
              url: delete_url,
              type: 'DELETE',
              success: function (res) {
                 window.parent.location.reload(true);
            }

         });

    }
    //处理删除文件
    $('.delete').click(function(){
        deleteFile($(this)[0]);
    });


    function file_list(e) {
        $.get("/repo/file_list?repo_id=" + e.getAttribute('data-repoid'), function(data){

        });
    }


    function dirChange(e){
       var count = 0;
       var files = e.files;
       var len = files.length;

       var repo_id = e.getAttribute('data-repoid');
       var current_dir = e.getAttribute('data-dir');

       if (files.length > 1000){
            alert("子文件太多，不支持上传");
            return;
       }


       for (var i = 0; i < files.length; i++) {

           (function(i) {
               var filename = files[i].name;
               var file_source = files[i];
               var relative_path = files[i].webkitRelativePath;
               var relative = relative_path.slice(0,relative_path.lastIndexOf(filename));
               $.get("/repo/file_list/upload",{'repo_id': repo_id, 'path': current_dir},function(data){
                    if(data.state == 1){
                        console.log(data.url);
                        var formData = new FormData();
                        formData.append("relative_path", relative);
                        formData.append("parent_dir", current_dir);
                        formData.append("file", file_source, filename);
                        console.log(relative);
                        $.ajax({
                            url: data.url,　　　　　　　　　　//上传地址
                            type: 'POST',
                            cache: false,　　
                            data: formData,　　　　　　　　　　　　　//表单数据
                            processData: false,
                            contentType: false,
                            xhr: function(){ //这是关键 获取原生的xhr对象 做以前做的所有事情
                                var xhr = jQuery.ajaxSettings.xhr();
                                xhr.upload.onloadstart = function(){//上传开始执行方法
                                    ot = new Date().getTime();   //设置上传开始时间
                                    oloaded = 0;//设置上传开始时，以上传的文件大小为0
                                };
                                if(xhr.upload){
                                    xhr.upload.onprogress = progressFunction;
                                }

                                return xhr;
                            }

                        }).done(function(resp) {
                            count++;
                            if(count == len){
                                window.parent.location.reload(true);
                            }
                        }).fail(function(err) {
                            //alert('无法连接服务器！')
                        });
                   }

               })
           })(i);
       }
    }

    //处理上传目录
    $('#dir_upload').change(function(){
        dirChange($('#dir_upload')[0]);
    });
    $('#dirUpload').click(function(){
        $('#dir_upload').click();
    });
});