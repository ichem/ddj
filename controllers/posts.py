import posts
from gluon.tools import Service


_page_size = 9
_service = Service()

def call():
    session.forget()
    return _service()

def index():
    response.title = '道德經'
    if request.args or request.vars:
        logger.error('Bad index: %s, %s', request.args, request.vars)
        raise HTTP(404)
    return {
        'index': posts.index(0, _page_size, db),
        'pager': posts.pager(_page_size, db)}

def item():
    try:
        row = db.post[request.args(0)]
        response.title = '道德經 %s' % row.title
        item_row = posts.item(row)
        links_row = posts.links(row, db)
    except:
        logger.exception('Bad post item: %s', request.args(0))
        raise HTTP(404)
    return {
        'item': item_row,
        'links': links_row}

def page():
    try:
        response.title = '道德經 Page %s' % request.args(0)
        xml = posts.index(int(request.args(0)), _page_size, db)
    except:
        logger.exception('Bad page: %s', request.args(0))
        raise HTTP(404)
    return {
        'index': xml,
        'pager': posts.pager(_page_size, db)}

@auth.requires_login()
def sqlform():
    response.title = '道德經'
    grid = posts.sqlform(db)
    return {'grid': grid}

@_service.run
def next(chapter):
    pass

@_service.run
def previous(chapter):
    pass
