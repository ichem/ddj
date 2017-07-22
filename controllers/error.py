def page_not_found():
    response.title = 'Page not found'
    log('404', request.vars.requested_uri)
    return {'message': response.title}
