$(document).ready(function(){

    target = $('.messages');
    refresh(target);

    $('form#add-message').submit(function(){
        $.post('/start');
        $(this).children('#message').val('').focus();
        refresh(target);
        return false;
    });

    setInterval(function(){
        refresh(target);
    }, 2000);
})