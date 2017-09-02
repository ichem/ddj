import logging
from gluon import A
from gluon import DIV
from gluon import H3
from gluon import H4
from gluon import H5
from gluon import I
from gluon import IS_IN_SET
from gluon import LI
from gluon import P
from gluon import MARKMIN
from gluon import SQLFORM
from gluon import SPAN
from gluon import TAG
from gluon import UL
from gluon import URL 
from gluon import XML
from gluon import xmlescape


date_format = '%B %Y'
index_class =  'col-xs-12 col-sm-6 col-md-4'
poem_class = 'col-xs-12 col-sm-10 col-md-8'

def _thumb(row, cls, title=None):
    """ Return a column DIV thumbnail. """
    caption = DIV(
         H3(row.chapter.title),
         H4('Chapter %i' % row.chapter.number),
         H5(row.published.strftime(date_format)),
         H3(row.intro_hanzi),
         H4(row.intro_en),
         _class='caption',
         _role='button',
         _title=title)
    anchor = A(
        caption,
        _class='ddj-thumbnail',
        _href=URL('poems', 'chapter', args=[row.chapter.number]))
    thumbnail = DIV(anchor, _class='thumbnail')
    return DIV(thumbnail, _class=cls)

def chapter(poem, db, uhdb):
    """ Return a bootstrap row for a poem row. """
    from unihan import pinyin_string
    from unihan import string_block

    if not poem:
        raise Exception('No such poem')
    qry = ((db.verse.book==1) & (db.verse.chapter==poem.chapter))
    verse = db(qry).select().first()
    title = H3(poem.chapter.title)
    subtitle = H4('Chapter %i' % poem.chapter.number)
    published = H5(poem.published.strftime(date_format))
    stanzas = verse.en.split('\r\n\r\n')
    content = []
    for stanza in stanzas:
        content.append(P(XML(stanza.replace('\r\n', '<br />'))))
    link = P(
        A(
            I('Go to the study version'),
            _href=URL('studies', 'chapter', args=[poem.chapter.number]),
            _style='color:inherit;',
            _title='Study version'),
        _style='font-size:0.9em;padding-top:1em')
    content.append(P(link))
    column = DIV(title, subtitle, published, *content, _class=poem_class)
    return DIV(
        column, _class='row',
        _style='font-size:1.12em;white-space:nowrap;')

def decache(chapter, db):
    """ Clear study chapter cache data. """
    from gluon import current

    # Decache the poem itself.
    current.cache.ram('poem-%d' % chapter, None)

    # Decache links in the next poem.
    qry = db.poem.chapter > int(chapter)
    nxt = db(qry).select(limitby=(0,1), orderby=db.poem.chapter)
    if nxt:
        current.cache.ram('links-%d' % nxt.first().chapter, None)

    # Decache links in the previous poem.
    qry = db.poem.chapter < chapter
    prev = db(qry).select(limitby=(0,1), orderby=~db.poem.chapter)
    if prev:
        current.cache.ram('links-%d' % prev.first().chapter, None)

    # Decache the page containing the poem.
    page = (chapter + 8) / 9
    current.cache.ram('poems-%d' % page, None)

def grid(db):
    """ Return an SQLFORM.grid to manage poems. """

    createargs = editargs = viewargs = {
        'fields': [
            'chapter', 'published', 'intro_hanzi', 'intro_en']}
    fields = [
        db.poem.chapter,
        db.poem.published,
        db.poem.intro_hanzi,
        db.poem.intro_en]
    maxtextlengths = {'poem.published': 50}
    onupdate = lambda form: decache(int(form.vars.chapter), db)
    db.poem.published.represent = lambda value, row: value.strftime(date_format)
    db.poem.chapter.requires = IS_IN_SET(range(1, 82), zero=None)
    grid = SQLFORM.grid(
        db.poem,
        createargs=createargs,
        csv=False,
        editargs=editargs,
        fields=fields,
        maxtextlengths=maxtextlengths,
        onupdate=onupdate,
        orderby=db.poem.chapter,
        paginate=None,
        searchable=False,
        viewargs=viewargs)
    return grid

def index(page_number, db):
    """ Return a row DIV of a page of poems. """
    if page_number >= 1 and page_number <= 9:
        low = ((page_number-1)*9)+1
        high = page_number*9
    else:
        raise Exception('No such page')
    qry = ((db.poem.chapter>=low) & (db.poem.chapter<=high))
    thumbs = []
    for row in db(qry).select(orderby=db.poem.chapter):
        thumbs.append(_thumb(row, index_class))
    return DIV(thumbs, _class='row display-flex')

def links(poem, db):
    """ Return a row DIV of prev/next poems. """
    thumbs = []

    # Next.
    qry = db.poem.chapter > poem.chapter
    nxt = db(qry).select(limitby=(0,1), orderby=db.poem.chapter)
    if not nxt:
        qry = db.poem.chapter >= 1
        nxt = db(qry).select(limitby=(0,1), orderby=db.poem.chapter)
    if nxt: 
        thumbs.append(_thumb(nxt.first(), poem_class, 'Next'))

    # Previous.
    qry = db.poem.chapter < poem.chapter
    prev = db(qry).select(limitby=(0,1), orderby=~db.poem.chapter)
    if not prev:
        qry = db.poem.chapter <= 81
        prev = db(qry).select(limitby=(0,1), orderby=~db.poem.chapter)
    if prev:
        thumbs.append(_thumb(prev.first(), poem_class, 'Previous'))

    # Bootstrap.
    return DIV(
        thumbs,
        _class='row',
        _style='padding-top: 2.5em;')

def pager(db):
    """ Return a row DIV for a pager. """
    from gluon import current

    # Previous/current/next page.
    if current.request.args(0):
        current_page = int(current.request.args(0))
    else:
        current_page = 1
    prev_page = current_page - 1
    next_page = current_page + 1

    # List of LI.
    pages = []

    # Previous/left.
    li_class = ''
    href = URL('poems', 'page', args=[str(prev_page)])
    if prev_page < 1:
        li_class = 'disabled'
        href = '#'
    elif prev_page == 1:
        href = URL('poems', 'index')
    span = SPAN(xmlescape(u'\u4e0a'), **{'_aria-hidden': 'true'})
    anchor = A(span, _href=href, **{'_aria-label': 'Previous'})
    pages.append(LI(anchor, _class=li_class, _title='Previous Page'))

    # Chapter range links.
    for page in range(1, 10):
        li_class = ''
        href = URL('poems', 'page', args=[str(page)])
        page_range = ['%d-%d' % (((page-1)*9)+1, page*9)]
        if page == 1:
            href = URL('poems', 'index')
        if page == current_page:
            li_class = 'active'
            page_range.append(SPAN('(current)', _class='sr-only'))
        anchor = A(page_range, _href=href)
        pages.append(LI(anchor, _class=li_class))

    # Next/right.
    li_class = ''
    href = URL('poems', 'page', args=[str(next_page)])
    if next_page > 9:
        li_class = 'disabled'
        href = '#'
    span = SPAN(xmlescape(u'\u4e0b'), **{'_aria-hidden': 'true'})
    anchor = A(span, _href=href, **{'_aria-label': 'Next'})
    pages.append(LI(anchor, _class=li_class, _title='Next Page'))

    # Together.
    return UL(pages, _class='pagination')
