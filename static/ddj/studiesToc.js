/* Keep track of modal state for nav actions. */
$('#toc-modal').on('shown.bs.modal', function () {
        window.hasModal = true;
});
$('#toc-modal').on('hidden.bs.modal', function () {
        window.hasModal = false;
});
function tocModal(ev) {
    var setHTML = function(html) {
        var oldHeight = $('.modal-body').height();
        $('.modal-body').html(html);
        var newHeight = $('.modal-body').height();
        $('.modal-body').height(oldHeight);
        $('.modal-body').animate({height: newHeight}, 100, function() {
            $('.modal-body').height('auto');
        });
    };
    var current = window.location.href.substr(window.location.href.lastIndexOf('/') + 1)
    $('.modal-title').html('Chapter Studies');
    $('.modal-body').html('Looking up in-progress list');
    $.ajax({
        url: '/studies/call/run/toc/' + current,
        timeout: 3000
    }).done(function(html) {
        setHTML(html);
    }).on('error', function(ev) {
        setHTML('Error loading table of contents.');
    });
    $('#toc-modal').modal();
}
