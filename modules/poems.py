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


date_format = '%A, %B %e, %Y'
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

def chapter(row, db, uhdb):
    """ Return a row DIV for a poem chapter. """
    from unihan import pinyin_string
    from unihan import string_block

    if not row:
        raise Exception('No such poem')
    qry = ((db.verse.book==1) & (db.verse.chapter==row.chapter))
    verse = db(qry).select().first()
    title = H3(row.chapter.title)
    subtitle = H4('Chapter %i' % row.chapter.number)
    published = H5(row.published.strftime(date_format))
    stanzas = verse.en.split('\r\n\r\n')
    content = []
    for stanza in stanzas:
        content.append(P(XML(stanza.replace('\r\n', '<br />'))))
    column = DIV(title, subtitle, published, *content, _class=poem_class)
    return DIV(column, _class='row', _style='font-size:1.12em;')

def grid(db):
    createargs = editargs = viewargs = {
        'fields': [
            'chapter', 'published', 'intro_hanzi', 'intro_en']}
    fields = [
        db.poem.chapter,
        db.poem.published,
        db.poem.intro_hanzi,
        db.poem.intro_en]
    maxtextlengths = {'poem.published': 50}
    db.poem.published.represent = lambda value, row: value.strftime(date_format)
    db.poem.chapter.requires = IS_IN_SET(range(1, 82), zero=None)
    grid = SQLFORM.grid(
        db.poem,
        createargs=createargs,
        csv=False,
        editargs=editargs,
        fields=fields,
        maxtextlengths=maxtextlengths,
        orderby=~db.poem.published,
        searchable=False,
        viewargs=viewargs)
    return grid

def index(page_number, page_size, db):
    """ Return a row DIV of a page of poems. """
    limitby = ((page_number-1)*page_size, (page_number)*page_size)
    orderby = ~db.poem.published
    thumbs = []
    for row in db(db.poem.id>0).select(limitby=limitby, orderby=orderby):
        thumbs.append(_thumb(row, index_class))
    if not thumbs:
        raise Exception('No such page')
    return DIV(thumbs, _class='row')

def links(poem, db):
    """ Return a row DIV of prev/next poems. """
    thumbs = []

    # Older.
    qry = db.poem.published < poem.published
    older = db(qry).select(limitby=(0,1), orderby=~db.poem.published)
    if older:
        thumbs.append(_thumb(older.first(), poem_class, 'Older'))

    # Newer
    qry = db.poem.published > poem.published
    newer = db(qry).select(limitby=(0,1), orderby=db.poem.published)
    if newer:
        thumbs.append(_thumb(newer.first(), poem_class, 'Newer'))

    # Bootstrap.
    return DIV(
        thumbs,
        _class='row',
        _style='padding-top: 2.5em;')

def pager(page_size, db):
    """ Return a row DIV for a pager. """
    from gluon import current
    import math

    # Don't show pager if total number of poems is less than page size.
    poem_count = db(db.poem.id).count()
    page_count = int(math.ceil((poem_count + 0.0) / page_size))
    if page_count <= 1:
        return ''

    # Current page.
    if current.request.args(0):
        current_page = int(current.request.args(0))
    else:
        current_page = 1

    # Older/left.
    next_page = current_page + 1
    if next_page > page_count:
        left_href = '#'
        left_class = 'next disabled'
    else:
        left_href = URL('poems', 'page', args=[str(next_page)])
        left_class = 'next'
    left_span = SPAN(xmlescape(u'\u2192'), **{'_aria-hidden': 'true'})
    left_anchor = A('Older Posts ', left_span, _href=left_href)
    left_li = LI(left_anchor, _class=left_class)

    # Newer/right.
    prev_page = current_page - 1
    if prev_page < 1:
        right_href = '#'
        right_class = 'previous disabled'
    elif prev_page == 1:
        right_href = URL('poems', 'index')
        right_class = 'previous'
    else:
        right_href = URL('poems', 'page', args=[str(prev_page)])
        right_class = 'previous'
    right_span = SPAN(xmlescape(u'\u2190'), **{'_aria-hidden': 'true'})
    right_anchor = A(right_span, ' Newer Posts', _href=right_href)
    right_li = LI(right_anchor, _class=right_class)

    # Together.
    ul = UL(left_li, right_li, _class='pager')
    nav = TAG.nav(ul, **{'_aria-label': '...'})
    column = DIV(nav, _class='col-sm-4')
    return DIV(column, _class='row')

def study_link(row, user):
    if not user:
        return ''
    link = A(
        I('Go to the study version'),
        _href=URL('studies', 'chapter', args=[row.chapter.number]),
        _style='color:inherit;',
        _title='Study version')
    column = DIV(link, _class=poem_class)
    return DIV(column, _class='row', _style='padding-top:1em;')
