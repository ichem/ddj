import ddj
from gluon.tools import Service


_service = Service()

def call():
    session.forget()
    return _service()

def chapter():
    """ Return a dict for the chapter view. The edit form presents
    a side-by-side comparison of chapters across all versions of the DDJ
    in the library. """
    try:
        chrow = db.chapter[request.args[0]]
        vrow = db.verse[request.args[0]]
    except:
        raise HTTP(404)
    if not chrow or not vrow:
        raise HTTP(404)
    if not auth.user and not vrow.publish_en:
        raise HTTP(404)
    response.title = '道德經 %i %s' % (chrow.number, chrow.title or '')
    if len(request.args)==1:

        # Generate/cache the poem page.
        page = cache.ram(
            'ddj-%s' % request.args[0],
            lambda: ddj.page(chrow, vrow, uhdb, logger))
        if page and auth.user:

            # Put an edit button on it.
            btn = A('Edit',
                _class='btn btn-default',
                _href=URL(args=[chrow.number, 'edit']))
            btn = DIV(btn, _class='col-md-12')
            page.append(btn)
    elif auth.user and len(request.args)==2 and request.args[1]=='edit':

        # Generate/process the edit form.
        form = ddj.edit_form(chrow, vrow, request.args[:1])
        if form.process().accepted:
            chrow.update_record(title=form.vars.title)
            data = {
                'publish_en': form.vars.publish_english,
                'en': form.vars.english,
                'publish_notes': form.vars.publish_notes,
                'notes': form.vars.notes,
                'hanzi': form.vars.hanzi}
            vrow.update_record(**data)
            cache.ram('ddj-%s' % request.args[0], None)
            cache.ram('poem-%s' % request.args[0], None)
            cache.ram('toc', None)
            redirect(URL(args=request.args[:1]))

        # Generate the comparison and stick it on the page too.
        from ddj import comparison

        hanzi = comparison(request.args[0], db, uhdb)
        left = DIV(hanzi, _class='col-md-3 pull-left')
        right = DIV(form, _class='col-md-9 pull-left')
        page = [left, right]
    else:
        raise HTTP(404)
    return {'chapter': DIV(page, _class='row')}

def index():
    """ Redirect to the first published chapter. """
    if auth.user_id:
        redirect(URL('ddj', 'chapter', args=['1']))
    _, published = cache.ram('toc', lambda: toc_maps())
    if published:
        redirect(URL('ddj', 'chapter', args=[published.items()[0][0]]))

@_service.run
def next(chapter):
    """ Return the number of the next published chapter. """

    def next_candidate(i):
        return ((i - 1) + 1) % 81 + 1

    candidate = next_candidate(int(chapter))
    if auth.user:
        return candidate
    else:
        _, published = cache.ram('toc', lambda: toc_maps())
        while candidate != int(chapter):
            if candidate in published:
                return candidate
            candidate = next_candidate(candidate)
        return chapter

@_service.run
def previous(chapter):
    """ Return the number of the previous published chapter. """

    def prev_candidate(i):
        return ((i - 1) + 81 - 1) % 81 + 1

    candidate = prev_candidate(int(chapter))
    if auth.user:
        return candidate
    else:
        _, published = cache.ram('toc', lambda: toc_maps())
        while candidate != int(chapter):
            if candidate in published:
                return candidate
            candidate = prev_candidate(candidate)
        return chapter

@_service.run
def toc(chapter):
    """ Return a table of contents element. """
    links, published = cache.ram('toc', lambda: toc_maps())
    if auth.user:
        toc_map = links
    else:
        toc_map = published
    try:
        link = toc_map[int(chapter)]
        link[0]['_class'] += ' ddj-toc-current'
    except:
        pass
    return DIV(toc_map.values(), _class='ddj-toc')
