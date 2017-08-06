import studies
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
        chrow = db.chapter[request.args(0)]
        vrow = db.verse[request.args(0)]
    except:
        raise HTTP(404)
    if not chrow or not vrow:
        raise HTTP(404)
    response.title = '道德經 %i %s' % (chrow.number, chrow.title or '')
        
    # The study display.
    if len(request.args)==1:

        # Cached study page.
        page = cache.ram(
            'study-%s' % request.args[0],
            lambda: studies.page(chrow, vrow, db, uhdb))

        # Put an edit button on it. Depends on auth, do not cache.
        if page and auth.user:
            btn = A('Edit',
                _class='btn btn-default',
                _href=URL(args=[chrow.number, 'edit']))
            btn = DIV(btn, _class='col-md-12')
            page.append(btn)

    # The edit form.
    elif auth.user and len(request.args)==2 and request.args[1]=='edit':

        # Define and process the form.
        form = studies.edit_form(chrow, vrow, request.args[:1])
        if form.process().accepted:

            # Get verse data from the form.
            vdata = {
                'publish_en': form.vars.publish_english,
                'en': form.vars.english,
                'publish_notes': form.vars.publish_notes,
                'notes': form.vars.notes,
                'hanzi': form.vars.hanzi}

            # Update the published date on changes to title/en/hanzi.
            if (
                    chrow.title != form.vars.title
                    or vrow.en != form.vars.english
                    or vrow.hanzi != form.vars.hanzi):
                prow = db(db.poem.chapter==vrow.chapter).select().first()
                if prow:
                    import datetime
                    prow.update_record(published=datetime.datetime.now())
                    logger.info('Updated %s publish date', prow.chapter)

            # Update records, clear cache and go.
            chrow.update_record(title=form.vars.title)
            vrow.update_record(**vdata)
            cache.ram('study-%s' % request.args[0], None)
            cache.ram('poem-%s' % request.args[0], None)
            cache.ram('toc', None)
            redirect(URL(args=request.args[:1]))

        # Generate the comparison and stick it on the page too.
        hanzi = studies.comparison(request.args[0], db, uhdb)
        left = DIV(hanzi, _class='col-md-3 pull-left')
        right = DIV(form, _class='col-md-9 pull-left')
        page = [left, right]
    else:
        raise HTTP(404)
    return {'chapter': DIV(page, _class='row')}

def index():
    """ Redirect to the default studies chapter. """
    redirect(default_study())

@_service.run
def next(chapter):
    """ Return the number of the next published chapter. """

    def next_candidate(i):
        return ((i - 1) + 1) % 81 + 1

    candidate = next_candidate(int(chapter))
    if auth.user:
        return candidate
    else:
        _, published = cache.ram('toc', lambda: studies_toc())
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
        _, published = cache.ram('toc', lambda: studies_toc())
        while candidate != int(chapter):
            if candidate in published:
                return candidate
            candidate = prev_candidate(candidate)
        return chapter

@_service.run
def toc(chapter):
    """ Return a table of contents element. """
    links, published = cache.ram('toc', lambda: studies_toc())
    if auth.user:
        toc_map = links
    else:
        toc_map = published
    try:
        link = toc_map[int(chapter)]
        link[0]['_class'] += ' studies-toc-current'
    except:
        pass
    return DIV(toc_map.values(), _class='studies-toc')
