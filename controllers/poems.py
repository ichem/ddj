import poems


_page_size = 9

def call():
    session.forget()
    return _service()

def index():
    response.title = '道德經'
    if request.args or request.vars:
        logger.error('Bad index: %s, %s', request.args, request.vars)
        raise HTTP(404)
    try:
        idx = cache.ram(
            'poems-1',
            lambda: poems.index(0, _page_size, db))
        pager = cache.ram(
            'poems_pager-1',
            lambda: poems.pager(_page_size, db))
    except:
        logger.exception('Bad index: %s', request.args(0))
        raise HTTP(404)
    return {'index': idx, 'pager': pager}

def chapter():
    try:
        row = db(db.poem.chapter==request.args(0)).select().first()
        if not row:
            raise HTTP(404)
        response.title = '道德經 Chapter %i' % row.chapter.number
        poem = cache.ram(
            'poem-%s' % request.args[0],
            lambda: poems.chapter(row, db, uhdb))
        study = ''
        if auth.user_id:
            study = A(
                'Study version',
                _href=URL('studies', 'chapter', args=[row.chapter.number]))
        links = cache.ram(
            'links-%s' % request.args[0],
            lambda: poems.links(row, db))
    except:
        logger.exception('Bad chapter: %s', request.args(0))
        raise HTTP(404)
    return {'poem': poem, 'study': study, 'links': links}

def page():
    try:
        response.title = '道德經 Page %s' % request.args(0)
        idx = cache.ram(
            'poems-%s' % request.args(0),
            poems.index(int(request.args(0)), _page_size, db))
        pager = cache.ram(
            'poem_pager-%s' % request.args(0),
            poems.pager(_page_size, db))
    except:
        logger.exception('Bad page: %s', request.args(0))
        raise HTTP(404)
    return {'index': idx, 'pager': pager}

@auth.requires_login()
def manage():
    response.title = '道德經'
    grid = poems.grid(db)
    return {'grid': grid}
