def page_not_found():
    response.title = 'Page not found'
    log('404')
    return {'message': response.title}
