def page_not_found():
    parts = request.vars.requested_uri.split('/')
    if len(parts) > 3 and parts[2] == 'ddj':
        redirect(ddj_chapter())
    response.title = 'Page not found'
    logger.info(
        '404 %s from %s', request.vars.requested_uri,
        request.env.remote_addr)
    return {'message': response.title}
