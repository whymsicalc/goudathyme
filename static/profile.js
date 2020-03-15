$(document).ready(function(){
    $(":button").on("click", function(){
        $(".profile").toggle()
    });
    $("#edit").on("click", function(){
        let phone = $("#phone").text()
        if (phone.length === 12){
            phone = phone.slice(2, 5) + "-" + phone.slice(5, 8) + "-" + phone.slice(8, 12)
        } else {
            phone = ""
        }
        $("#fname").html('<input type="text" class="form-control" id="firstname" value="' + $("#fname").text() + '">');
        $("#lname").html('<input type="text" class="form-control" id="lastname" value="' + $("#lname").text() + '">');
        $("#email").html('<input type="text" class="form-control" id="emailadd" value="' + $("#email").text() + '">');
        $("#phone").html('<input type="tel" class="form-control" id="phonenum" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" placeholder="Phone: 123-456-789" value="' + phone + '">');
    });
    $("#update").on("click", function(){
        const formInputs = {
            'user_id': $("h3").data('user_id'),
            'fname': $("#firstname").val(),
            'lname': $("#lastname").val(),
            'email': $("#emailadd").val(),
            'phone': $("#phonenum").val()
        };
        $.post('/update-profile', formInputs, (res) => {
            $("#fname").html(res.fname);
            $("#lname").html(res.lname);
            $("#email").html(res.email);
            $("#phone").html(res.phone);
        });
    });
});