
$(function () {

    //页面层-佟丽娅

$("#wechat_app").click(function () {
    layer.open({
  type: 1,
  title: false,
  closeBtn: 0,
  area: '516px',
  skin: 'layui-layer-nobg', //没有背景色
  shadeClose: true,
  content: $('#tong')
});
})

    $.ajax({
        url:'/getData',
        method:'get',
        success:function (data) {
            clicks_web=data.clicks_web
            $("#web_clicks").attr('data-to',clicks_web)
            clicks_app=data.clicks_app
            $("#app_clicks").attr('data-to',clicks_app)
            users=data.users
            $("#users").attr('data-to',users)
            downloads=data.downloads
            $("#downloads").attr('data-to',downloads)
            app_version=data.app_version
            $("#app_version").html(app_version)
        },
        error:function () {
            alert("获取基本数据异常")
        }
    })

})

