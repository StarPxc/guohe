
$(function () {
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
        },
        error:function () {
            alert("获取基本数据异常")
        }
    })

})