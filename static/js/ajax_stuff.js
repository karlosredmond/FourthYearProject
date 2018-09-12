// for demonstration, live is https://karlredmond.pythonanywhere.com
var serverName = "https://karlredmond.pythonanywhere.com" //'http://192.168.1.33:5000'

// This Function is a timed function which polls database for latest
// entry. It updates the image and information on the Home Screen
function executeQuery() {
    $.ajax({
        url: serverName + '/update_image',
            success: function(data) {
            //alert(data.test);
                $("#latest_image").attr('src', data.test);// Change Image based on return from Flask
                $("#latest_comment").html(data.pi_location);
                $("#latest_date").html(data.date);
                $("#latest_time").html(data.time);
            }
        });
        setTimeout(executeQuery, 1000); // Keep polling Flask for database updates!!
}

// run the first time; all subsequent calls will take care of themselves
$(document).ready(function() {
    setTimeout(executeQuery, 1000);
});

// This function polls Home SecuriPi for its current state, updating the state for
// all users. This allows everyone to no, what anyone else is doing in the system ie.
// turning on a light or disarming the system
function getState(){
    //alert(document.getElementById('arm-event').checked);
    $.ajax({
        url: serverName + '/getState',
        success:function(data){
            var test = JSON.parse(data);
            if(test.armed && !document.getElementById('arm-event').checked){
                    $('#arm-event').bootstrapToggle('on');
            }
            else if(!test.armed && document.getElementById('arm-event').checked){
                    $('#arm-event').bootstrapToggle('off');
            }
            if(test.notifications && !document.getElementById('notification-event').checked){
                    $('#notification-event').bootstrapToggle('on');
            }
            else if(!test.notifications && document.getElementById('notification-event').checked){
                    $('#notification-event').bootstrapToggle('off');
            }
            if(test.light == 1 && document.getElementById('light-event').checked){
                    $('#light-event').bootstrapToggle('off');
            }
            else if(test.light == 0 && !document.getElementById('light-event').checked){
                    $('#light-event').bootstrapToggle('on');
            }
            if(test.dogs == 0 && document.getElementById('dog-event').checked){
                    $('#dog-event').bootstrapToggle('off');
            }
            else if(test.dogs == 1 && !document.getElementById('dog-event').checked){
                    $('#dog-event').bootstrapToggle('on');
            }
        }

    });
    setTimeout(getState,3000);
}

// run the first time; all subsequent calls will take care of themselves
$(document).ready(function(){
    setTimeout(getState, 3000);
})