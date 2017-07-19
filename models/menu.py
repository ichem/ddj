def ddj_navbar():
    """ Add links to auth navbar. """
    response.auth_navbar = auth.navbar(mode='dropdown')
    menu = response.auth_navbar.element('.dropdown-menu')
    if auth.user_id:
        menu.insert(0, LI(A('SSH', _href=URL('ssh', 'index'))))
        menu.insert(0, LI('', _class='divider'))
    if request.controller != 'unihan':
        menu.insert(0, LI(A('Unihan Dump', _href=URL('unihan', 'dump'))))
    if auth.user_id:
        if (
                request.controller != 'ddj'
                or request.controller == 'ddj'
                and request.function != 'chapter'):
            href = default_chapter()
            menu.insert(0, LI(A('In Progress', _href=href)))
    if request.controller != 'poems':
        menu.insert(0, LI(A('Poems', _href=URL('poems', 'index'))))
    if request.controller != 'about':
        menu.insert(0, LI(A('About', _href=URL('about', 'index'))))
    if 'Log In' in response.auth_navbar.element('.dropdown-toggle'):
        response.auth_navbar.element('.dropdown-toggle')[0] = 'Menu'

def ddj_toc():
    """ Set table of contents element. """
    attr = {
        '_class': 'navbar-brand',
        '_role': 'button'}
    if request.controller == 'ddj':
        attr['_onclick'] = 'tocModal(event);'
        attr['_title'] = 'In Progress List'
    else:
        attr['_href'] = URL('poems', 'index')
        attr['_title'] = 'All Poems'
    response.navbar_toggle = LI(A('道德經', **attr))

def default_chapter():
    """ Return a URL for the default chapter. """
    if auth.user_id:
        return URL('ddj', 'chapter', args=['1'])
    _, published = cache.ram('toc', lambda: toc_maps())
    if published:
        return URL('ddj', 'chapter', args=[published.items()[0][0]])

def toc_maps():
    """ Return a tuple of dicts, both map chapter id to toc links. The first
    dict contains all chapters, the second only has published chapters. """
    from collections import OrderedDict

    def toc_link(chapter):
        verse = db.verse[chapter]
        url = URL('ddj', 'chapter', args=[verse.chapter.number])
        cls = 'ddj-toc-link'
        lnk = '%i %s' % (verse.chapter.number, verse.chapter.title or '')
        return DIV(A(lnk, _class=cls, _href=url))

    logger.debug('Generating new table of contents maps')
    links = OrderedDict()
    published = OrderedDict()
    for chapter in range(1, 82):
        link = toc_link(chapter)
        if db.verse[chapter].publish_en:
            published[chapter] = link
        links[chapter] = link
    return links, published

auth.settings.actions_disabled.append('request_reset_password')
auth.settings.logout_next = URL(args=request.args(0))
ddj_navbar()
ddj_toc()
