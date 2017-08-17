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

def decache(chapter, db):
    """ Clear study chapter cache data. """
    from gluon import current

    current.cache.ram('study-%d' % chapter, None)
    current.cache.ram('toc', None)

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

def page(chapter, verse, db, uhdb):
    """ Return a list of DDJ chapter view elements. """
    from unihan import string_block
    from unihan import pinyin_string

    # Formatted stanzas.
    blocks = []
    content = None
    hanzi_blocks = verse.hanzi.split('\r\n\r\n')
    en_blocks = verse.en.split('\r\n\r\n')
    if len(hanzi_blocks) and len(hanzi_blocks) == len(en_blocks):
        for block_count in range(0, len(hanzi_blocks)):
            hanzi_lines = hanzi_blocks[block_count].split('\r\n')
            en_lines = en_blocks[block_count].split('\r\n')
            if len(hanzi_lines) and len(hanzi_lines) == len(en_lines):
                for line_count in range(0, len(hanzi_lines)):
                    hanzi = string_block(hanzi_lines[line_count], True, uhdb)
                    pinyin = pinyin_string(hanzi_lines[line_count], uhdb)
                    en = en_lines[line_count]
                    block = DIV(hanzi, I(pinyin), P(en))
                    blocks.append(block)
                block['_style'] = 'padding-bottom:1em;'
            else:
                blocks = []
                break
        if blocks:
            content = DIV(blocks, _class='col-md-12')

    # Three big unformatted blocks.
    if not content:
        hanzi = string_block(verse.hanzi, True, uhdb)
        hanzi['_style'] = 'padding-bottom:0.5em;'
        blocks.append(DIV(hanzi, _class='col-md-12'))
        pinyin = pinyin_string(verse.hanzi, uhdb)
        pinyin = DIV(P(pinyin), _class='col-md-12')
        pinyin['_style'] = 'font-style:italic;'
        blocks.append(pinyin)
        blocks.append(DIV(P(verse.en), _class='col-md-12'))
        content = DIV(blocks)

    # Link to English-only version.
    link = ''
    if db(db.poem.chapter==verse.chapter).select().first():
        link = A(
            I('Go to the English version'),
            _href=URL('poems', 'chapter', args=[chapter.number]),
            _style='color:inherit;',
            _title='English version')
        link = DIV(link, _class='col-md-12', _style='padding-bottom:1em;')

    # Put it all together.
    title = DIV(H4(chapter.title), _class='col-md-12')
    return [title, content, link]
