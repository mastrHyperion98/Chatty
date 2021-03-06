/*
Created by Steven Smith 40057065
Created for: SOEN 287 W 2020 Concordia

scripts for controlling dashboard element and fetching messages

the script does not check for new incoming messages, but they do appear on refresh
I didnt have the time to implement it, although the backend has a function created to kinda accomodate a possible future
implementation. I didnt feel that it was necessary to meet the criteria needed for A3
 */
$(function() {
    setActiveDasboardChannel();
        $.ajax({
        type: "GET",
        //the url where you want to sent the userName and password to
        url: '/user/username',
        dataType: 'json',
        contentType: 'application/json',
        async: true,
        //json object to sent to the authentication url
        success: function (data){
            var input = $('#message_input')
            input.attr('placeholder', data['username'] + ' please input a message to send!')
        }
    });
    // print to
    // get all messages of the channel
    // if a dashboard_channel exist
    refreshDashboard();
});
/* id for container = chat
      <div class="message">
                  <span class="name">Hyperion</span>
                  <p class="message_content">Hello. How are you today is everything fine?</p>
                  <span class="time">2020-02-21 11:00</span>
              </div>
 */
function setActiveDasboardChannel(){
     var buttonList = $('#dash_channel_select');
     var button_li = buttonList.find('li');
     var channel_permalink = button_li.find('.channel_btn').attr("id");
     sessionStorage.current_dashboard_channel = channel_permalink;
     $('button.list-group-item.active').removeClass("active");
     $('#'+channel_permalink).addClass("active");
}

function changeDashboardChannel(id) {
    $('button.list-group-item.active').removeClass("active");
    $('#'+id).addClass("active");
    sessionStorage.current_dashboard_channel=id;
    refreshDashboard();
}


function sendMessage(){
    var message_content = $('#message_input').val();
    var permalink = sessionStorage.current_dashboard_channel;
    $('#message_input').val("");
    if (message_content.length > 0) {
        var data = {"content": message_content, "permalink": permalink};
        $.ajax({
            type: "POST",
            //the url where you want to sent the userName and password to
            url: '/messages/add',
            contentType: 'application/json',
            async: true,
            data: JSON.stringify(data),
            //json object to sent to the authentication url
            success: function () {
                console.log('MESSAGE POSTED');
                refreshDashboard();
            }
        });
    }
    else{
        console.log("EMPTY MESSAGE --- NOT SENT");
    }
}

function refreshDashboard(){
            $.ajax({
            type: "GET",
            //the url where you want to sent the userName and password to
            url: '/messages/all/' + sessionStorage.current_dashboard_channel,
            dataType: 'json',
            contentType: 'application/json',
            async: true,
            //json object to sent to the authentication url
            success: function (data) {
                var master = $('#chat') // our container to which we want to append our messages
                master.empty();
                // loop will be very similar to that of the table from channels
                console.log("ENTER DASHBOARD CODE")
            $.each(data, function(obj, item) {

                var $div = $('<div>');
                $div.attr("class", "message");
                $div.append("<span class='name'>"+item['username']+"</span>")
                    .append("<p class='message_content'>"+item['content']+"</p>")
                    .append("<span class='time'>"+item['sent']+"</span>");
                $div.appendTo(master);
            });
            }
        });
}