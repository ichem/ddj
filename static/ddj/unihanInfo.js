/* Keep track of modal state for nav actions. */
$('#info-modal').on('shown.bs.modal', function () {
        window.hasModal = true;
});
$('#info-modal').on('hidden.bs.modal', function () {
        window.hasModal = false;
});
function infoModal(ev) {
    var setHTML = function(html) {
        var oldHeight = $('.modal-body').height();
        $('.modal-body').html(html);
        var newHeight = $('.modal-body').height();
        $('.modal-body').height(oldHeight);
        $('.modal-body').animate({height: newHeight}, 100, function() {
            $('.modal-body').height('auto');
        });
    };
    $('.modal-title').html('Unihan ' + ev.target.innerText);
    $('.modal-body').html('Looking up ' + ev.target.innerText);
    $.ajax({
        url: '/unihan/call/run/info?char=' + ev.target.innerText,
        timeout: 3000
    }).done(function(html) {
        setHTML(html);
    }).on('error', function(ev) {
        setHTML('Error loading character data.');
    });
    $('#info-modal').modal();
}
