def page_not_found():
    response.title = 'Page not found'
    logger.debug(
        '404 %s from %s', request.vars.requested_uri,
        request.env.remote_addr)
    return {'message': response.title}
