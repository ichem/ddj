import logging
from gluon import A
from gluon import DIV
from gluon import H3
from gluon import H4
from gluon import H5
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


logger = logging.getLogger('web2py')
date_format = '%A, %B %e, %Y'
index_class =  'col-xs-12 col-sm-6 col-md-4'
item_class = 'col-xs-12 col-sm-10 col-md-8'

def _thumb(row, cls, title=None):
    """ Return a column DIV thumbnail. """
    caption = DIV(
         H3(row.title),
         H4(row.subtitle),
         H5(row.published.strftime(date_format)),
         MARKMIN(row.description),
         _class='caption',
         _role='button',
         _title=title)
    anchor = A(
        caption,
        _class='ddj-thumbnail',
        _href=URL('posts', 'item', args=[row.id]))
    thumbnail = DIV(anchor, _class='thumbnail')
    return DIV(thumbnail, _class=cls)

def links(current_item, db):
    """ Return a row DIV of prev/next items. """
    thumbs = []

    # Older.
    qry = db.post.published < current_item.published
    older = db(qry).select(limitby=(0,1), orderby=~db.post.published)
    if older:
        thumbs.append(_thumb(older.first(), item_class, 'Older'))

    # Newer
    qry = db.post.published > current_item.published
    newer = db(qry).select(limitby=(0,1), orderby=db.post.published)
    if newer:
        thumbs.append(_thumb(newer.first(), item_class, 'Newer'))

    # Bootstrap.
    return DIV(
        thumbs,
        _class='row',
        _style='padding-top: 2.5em;')

def index(page_number, page_size, db):
    """ Return a row DIV of a page of items. """
    limitby = ((page_number-1)*page_size, (page_number)*page_size)
    orderby = ~db.post.published
    thumbs = []
    for row in db(db.post.id>0).select(limitby=limitby, orderby=orderby):
        thumbs.append(_thumb(row, index_class))
    if not thumbs:
        raise Exception('No such page')
    return DIV(thumbs, _class='row')

def item(row):
    """ Return a row DIV for a post item. """
    from gluon.contrib.markdown.markdown2 import markdown

    if not row:
        raise Exception('No such item')
    title = H3(row.title)
    subtitle = H4(row.subtitle)
    published = H5(row.published.strftime(date_format))
    content = XML(markdown(row.content))
    column = DIV(title, subtitle, published, content, _class=item_class)
    return DIV(column, _class='row')

def pager(page_size, db):
    """ Return a row DIV for a pager. """
    from gluon import current
    import math

    # Don't show pager if total number of posts is less than page size.
    item_count = db(db.post.id).count()
    page_count = int(math.ceil((item_count + 0.0) / page_size))
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
        left_href = URL('posts', 'page', args=[str(next_page)])
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
        right_href = URL('posts', 'index')
        right_class = 'previous'
    else:
        right_href = URL('posts', 'page', args=[str(prev_page)])
        right_class = 'previous'
    right_span = SPAN(xmlescape(u'\u2190'), **{'_aria-hidden': 'true'})
    right_anchor = A(right_span, ' Newer Posts', _href=right_href)
    right_li = LI(right_anchor, _class=right_class)

    # Together.
    ul = UL(left_li, right_li, _class='pager')
    nav = TAG.nav(ul, **{'_aria-label': '...'})
    column = DIV(nav, _class='col-sm-4')
    return DIV(column, _class='row')

def sqlform(db):
    createargs = editargs = viewargs = {
        'fields': [
            'title', 'subtitle', 'published', 'description', 'content']}
    fields = [db.post.id, db.post.published, db.post.title, db.post.subtitle]
    maxtextlengths = {'post.published': 50}
    db.post.published.represent = lambda value, row: value.strftime(date_format)
    grid = SQLFORM.grid(
        db.post,
        createargs=createargs,
        csv=False,
        editargs=editargs,
        fields=fields,
        maxtextlengths=maxtextlengths,
        orderby=~db.post.published,
        viewargs=viewargs)
    return grid
