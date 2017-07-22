def app_logo():
    """ Set table of contents element. """
    attr = {
        '_class': 'navbar-brand',
        '_role': 'button'}
    if request.controller == 'studies':
        attr['_onclick'] = 'tocModal(event);'
        attr['_title'] = 'Studies'
    else:
        attr['_href'] = URL('poems', 'index')
        attr['_title'] = 'Poems'
    response.navbar_toggle = LI(A('道德經', **attr))

def app_navbar():
    """ Add links / clean up auth navbar. """
    response.auth_navbar = auth.navbar(mode='dropdown')
    menu = response.auth_navbar.element('.dropdown-menu')
    if auth.user_id:
        menu.insert(0, LI(A('SSH', _href=URL('ssh', 'index'))))
        menu.insert(0, LI('', _class='divider'))
    if request.controller != 'unihan':
        menu.insert(0, LI(A('Unihan Dump', _href=URL('unihan', 'dump'))))
    if auth.user_id and request.controller != 'studies':
        menu.insert(0, LI(A('Studies', _href=URL('studies', 'index'))))
    if request.controller != 'poems':
        menu.insert(0, LI(A('Poems', _href=URL('poems', 'index'))))
    if request.controller != 'about':
        menu.insert(0, LI(A('About', _href=URL('about', 'index'))))
    if 'Log In' in response.auth_navbar.element('.dropdown-toggle'):
        response.auth_navbar.element('.dropdown-toggle')[0] = 'Menu'

def default_study():
    """ Return a URL for the default study app chapter. """
    _, published = cache.ram('toc', lambda: studies_toc())
    if published:
        return URL('studies', 'chapter', args=[published.items()[0][0]])
    return URL('studies', 'chapter',  args=['1'])

def studies_toc():
    """ Return a tuple of dicts, both map chapter id to toc links. The first
    dict contains all chapters, the second only has published chapters. """
    from collections import OrderedDict

    def study_link(chapter):
        verse = db.verse[chapter]
        url = URL('studies', 'chapter', args=[verse.chapter.number])
        cls = 'studies-toc-link'
        lnk = '%i %s' % (verse.chapter.number, verse.chapter.title or '')
        return DIV(A(lnk, _class=cls, _href=url))

    links = OrderedDict()
    published = OrderedDict()
    for chapter in range(1, 82):
        link = study_link(chapter)
        if db.verse[chapter].publish_en:
            published[chapter] = link
        links[chapter] = link
    return links, published

app_logo()
app_navbar()
