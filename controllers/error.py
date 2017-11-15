def page_not_found():
    response.title = 'Page not found'
    log('404', request.vars.request_url)
    return {'message': response.title}
