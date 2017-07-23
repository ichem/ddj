from gluon import *


def comparison(chapter_number, db, uhdb):
    """ Return an element to compare chapters side by side. """
    from unihan import string_block

    columns = []
    qry = db.chapter.number==chapter_number
    chapters = db(qry).select(orderby=db.chapter.book)
    for chapter in chapters:

        # Chapter hanzi
        query = db.verse.chapter==chapter.id
        verse = db(query).select().first()
        hanzi = string_block(verse.hanzi, True, uhdb)
        hanzi['_class'] = '%s uh-rotate' % hanzi['_class']
        hanzi['_style'] = 'height:%dem;' % (len(hanzi) * 1.5)

        # Chapter label
        label_attr = {
            '_class': 'uh-char uh-rotate',
            '_style': 'height:4.2em'}
        a_attr = {
            '_class': 'uh-char-link',
            #'_onclick': 'infoModal(event);',
            '_role': 'button',
            '_title': chapter.book.subtitle}
        label = LABEL(A(chapter.book.title, **a_attr), **label_attr)

        # Chapter column.
        width = '2.5'
        if len(columns):
            width = '2'
        style = 'float:left; width:%sem;' % width
        columns.append(DIV([label, hanzi], _style=style))

    return SPAN(columns)

def edit_form(chapter, verse, args):
    """ Return a form to edit a DDJ chapter. """
    memdb = DAL('sqlite:memory:')
    memdb.define_table('chapter',
        Field('title'),
        Field('english', 'text'),
        Field('publish_english', 'boolean'),
        Field('hanzi', 'text'),
        Field('notes', 'text'),
        Field('publish_notes', 'boolean'))
    record = {
        'title': chapter.title,
        'publish_english': verse.publish_en,
        'english': verse.en,
        'publish_notes': verse.publish_notes,
        'notes': verse.notes,
        'hanzi': verse.hanzi}
    record_id = memdb.chapter.insert(**record)
    form = SQLFORM(memdb.chapter, record_id, showid=False)
    form.add_button('Cancel', URL(args=args))
    form.elements('.w2p_fl', replace=None)
    return form

def page(chapter, verse, poem, db, uhdb):
    """ Return a list of DDJ chapter view elements. """
    from unihan import string_block
    from unihan import pinyin_string

    title = DIV(H4(chapter.title), _class='col-md-12')
    hanzi = string_block(verse.hanzi, True, uhdb)
    hanzi['_style'] = 'padding-bottom:0.5em;'
    hanzi = DIV(hanzi, _class='col-md-12')
    pinyin = pinyin_string(verse.hanzi, uhdb)
    pinyin = DIV(P(pinyin), _class='col-md-12')
    pinyin['_style'] = 'font-style:italic;'
    english = DIV(P(verse.en), _class='col-md-12')
    link = ''
    if poem:
        link = A(
            I('Go to the published version'),
            _href=URL('poems', 'chapter', args=[chapter.number]),
            _style='color:inherit;',
            _title='Published version')
        link = DIV(link, _class='col-md-12', _style='padding-bottom:1em;')
    return [title, hanzi, pinyin, english, link]
