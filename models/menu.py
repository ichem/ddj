def app_logo():
    """ Set table of contents element. """
    attr = {
        '_class': 'navbar-brand',
        '_role': 'button'}
    if request.controller == 'studies':
        attr['_onclick'] = 'tocModal(event);'
        attr['_title'] = 'Chapter Studies'
    elif request.controller == 'poems' and request.function == 'chapter':
        page = (int(request.args(0)) + 8) / 9
        if page == 1:
            attr['_href'] = URL('poems', 'index')
            attr['_title'] = 'Poems'
        else:
            attr['_href'] = URL('poems', 'page', args=[str(page)])
            attr['_title'] = 'Poems page %d' % page
    else:
        attr['_href'] = URL('poems', 'index')
        attr['_title'] = 'Poems'
    response.navbar_toggle = LI(A('道德經', **attr))

def app_navbar():
    """ Add links / clean up auth navbar. """
    response.auth_navbar = auth.navbar(mode='dropdown')
    menu = response.auth_navbar.element('.dropdown-menu')
    if auth.user_id:
        menu.insert(0, LI(A('Whitelist', _href=URL('whitelist', 'index'))))
        menu.insert(0, LI(A('Blacklist', _href=URL('blacklist', 'index'))))
        menu.insert(0, LI('', _class='divider'))
    if request.controller != 'unihan':
        menu.insert(0, LI(A('Unihan Dump', _href=URL('unihan', 'dump'))))
    if request.controller != 'studies':
        menu.insert(0, LI(A('Studies', _href=URL('studies', 'index'))))
    if auth.user_id:
        menu.insert(0, LI(A('Manage Poems', _href=URL('poems', 'manage'))))
    if request.controller != 'poems':
        menu.insert(0, LI(A('Poems', _href=URL('poems', 'index'))))
    if request.controller != 'about':
        menu.insert(0, LI(A('About', _href=URL('about', 'index'))))
    if 'Log In' in response.auth_navbar.element('.dropdown-toggle'):
        response.auth_navbar.element('.dropdown-toggle')[0] = 'Menu'

def default_study():
    """ Return a URL for the default study app chapter. """
    public, private = cache.ram('toc', lambda: studies_toc())
    if auth.user:
        toc_map = private
    else:
        toc_map = public
    if toc_map:
        return URL('studies', 'chapter', args=[toc_map.items()[0][0]])
    return URL('poems', 'index')

def studies_toc():
    """ Return a tuple of ordered dicts that map chapter id to toc links.
    The first dict contains chapters that don't have an associated English
    poem, the second dict contains chapters that do. """
    from collections import OrderedDict

    def study_link(chapter):
        verse = db.verse[chapter]
        url = URL('studies', 'chapter', args=[verse.chapter.number])
        cls = 'studies-toc-link'
        lnk = '%i %s' % (verse.chapter.number, verse.chapter.title or '')
        return DIV(A(lnk, _class=cls, _href=url))

    public = OrderedDict()
    private = OrderedDict()
    for poem in db(db.poem).select(orderby=db.poem.chapter):
        link = study_link(poem.chapter)
        public[int(poem.chapter)] = link
    for chapter in range(1, 82):
        link = study_link(chapter)
        private[int(chapter)] = link
    return public, private

app_logo()
app_navbar()
