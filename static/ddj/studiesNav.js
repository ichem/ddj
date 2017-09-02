function loadNext() {
    var current = window.location.href.substr(
        window.location.href.lastIndexOf('/') + 1)
    $('#main').html('Loading the next chapter...');
    $.ajax({
        url: '/studies/call/run/next/' + current,
        timeout: 3000
    }).done(function(next) {
        window.location.href = '/studies/chapter/' + next;
    }).error(function(ev) {
        window.location.href = '/studies/chapter/' + current;
    });
}
function loadPrevious() {
    var current = window.location.href.substr(
        window.location.href.lastIndexOf('/') + 1)
    $('#main').html('Loading the previous chapter...');
    $.ajax({
        url: '/studies/call/run/previous/' + current,
        timeout: 3000
    }).done(function(previous) {
        window.location.href = '/studies/chapter/' + previous;
    }).error(function(ev) {
        window.location.href = '/studies/chapter/' + current;
    });
}
/* Keyboard navigation. */
$(window).on('keydown', function(ev) {
    if (window.hasModal) { return true; }
    if (window.location.href.includes('edit')) { return true; }
    if (ev.keyCode == 39) {
        loadNext();
    } else if (ev.keyCode == 37) {
        loadPrevious();
    }
});
/* Swipe navigation. */
$(window).on('touchstart', function(ev) {
    if (window.hasModal) { return true; }
    if (window.location.href.includes('edit')) { return true; }
    window.startX = ev.originalEvent.changedTouches[0].pageX;
}).on('touchend', function(ev) {
    if (window.hasModal) { return true; }
    if (window.location.href.includes('edit')) { return true; }
    var diff = startX - ev.originalEvent.changedTouches[0].pageX;
    var current = window.location.href.substr(
        window.location.href.lastIndexOf('/') + 1)
    if (diff > 100) {
        loadNext();
    } else if (diff < -100) {
        loadPrevious();
    }
});
