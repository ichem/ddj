# This Python file uses the following encoding: utf-8
""" A module to provide Unihan widget objects. """
from gluon import *


def _uh_repr(row):
    """ Return the row character as a formatted element. """
    char = SPAN(row.utf8, _class='uh-char')
    title = [row.kMandarin, row.kDefinition]
    title = [part for part in title if part]
    title = ' - '.join(title)
    attr = {
        '_class': 'uh-char-link',
        '_onclick': 'infoModal(event);',
        '_role': 'button',
        '_title': title}
    return A(char, **attr)

def info_block(row, uhdb):
    """ Transform a character row into a block containing detailed
    information about the character. """

    def do_ints(data):
        """ Return a list of int codepoints for each U+XXXX pattern found
        in string data. """
        import re

        ints = []
        if data:
            cp_pattern = r'U\+[0-9A-F]+'
            for cp in re.findall(cp_pattern, data):
                ints.append(int(cp.rsplit('+', 1)[1], 16))
        return ints

    def do_label(chars, label, label_color, box_id):
        """ Return a SPAN of the utf-8 chars and label. """
        return SPAN(
            LABEL(chars, _id=box_id, _class='uh-info-label'),
            BR(),
            LABEL(
                label, _for=box_id,
                _class='label label-%s' % label_color),
            _class='pull-left uh-labeled-chars')

    def do_spans(ints):
        """ Take a list of int codepoints and return a list of SPANs
        displaying the characters and providing links to info for each
        character. """
        links = []
        for i in ints:
            links.append(_uh_repr(uhdb.character[i]))
        return [SPAN(link) for link in links]

    def char_blocks():
        """ Return a FORM to display a character, its radical, and its
        variants in a labeled list. """

        # The character.
        blocks = []
        cid = 'uh-character-%d' % row.id
        chars = SPAN(row.utf8, _class='uh-char')
        label = '%s + %d' % (unichr(row.pRadicalID), row.pStrokes)
        blocks.append(do_label(chars, label, 'primary', cid))

        # Its radical.
        cid = 'uh-radical-%d' % row.id
        chars = [uhdb.character[row.pRadicalID].id]
        chars = do_spans(chars)
        label = 'Radical %s' % uhdb.radical[row.pRadicalID].pNumber
        blocks.append(do_label(chars, label, 'primary', cid))

        # Simplified and traditional variants.
        simplified = None
        if row.kSimplifiedVariant:
            cid = 'uh-simplified-%d' % row.id
            chars = do_ints(row.kSimplifiedVariant)
            chars = do_spans(chars)
            chars = do_label(chars, 'Simplified', 'default', cid)
            blocks.append(chars)
        traditional = None
        if row.kTraditionalVariant:
            cid = 'uh-traditional-%d' % row.id
            chars = do_ints(row.kTraditionalVariant)
            chars = do_spans(chars)
            chars = do_label(chars, 'Traditional', 'default', cid)
            blocks.append(chars)

        # Other variants.
        variants = do_ints(row.kSemanticVariant)
        variants += do_ints(row.kSpecializedSemanticVariant)
        variants += do_ints(row.kZVariant)
        variants = set(variants)
        if simplified and simplified[0] in variants:
            variants.remove(simplified[0])
        if traditional and traditional[0] in variants:
            variants.remove(traditional[0])
        if variants:
            cid = 'uh-variants-%d' % row.id
            chars = do_spans(variants)
            chars = do_label(chars, 'Variants', 'default', cid)
            blocks.append(chars)

        # The blocks in a bs3 FORM group.
        blocks = DIV(*blocks, _class='form-group')
        return FORM(blocks, _class='form-inline', _role='form')

    def char_bullets():
        """ Return a readonly SQLFORM. """
        fields = ['kMandarin', 'kDefinition']
        labels = {
            'kDefinition': 'Unihan Definition',
            'kMandarin': 'Mandarin'}
        return SQLFORM(
            uhdb.character,
            record=row,
            fields=fields,
            labels=labels,
            readonly=True,
            showid=False)

    def char_links():
        """ Return a UL of _blank links to info on the character. """
        links = []
        href = URL('library', 'search', vars={'chars': row.utf8})
        links.append(A('Search', _target='blank', _href=href))
        href = 'http://ctext.org/daoism?searchu=%s' % row.utf8
        links.append(A('CText', _target='blank', _href=href))
        href = (
            'http://www.chineseetymology.org/CharacterEtymology.aspx'
            '?characterInput=%s') % row.utf8
        links.append(A('Etymology', _target='blank', _href=href))
        href = (
            'http://www.mdbg.net/chindict/chindict.php'
            '?page=worddict&wdrst=1&wdqb=%s') % row.utf8
        links.append(A('MDBG', _target='blank', _href=href))
        if row.kBigFive:
            big5 = '%{0}%{1}'.format(
                row.kBigFive[:2], row.kBigFive[2:])
            href = 'http://zhongwen.com/cgi-bin/zipux2.cgi?b5=%s' % big5
            links.append(A('Zhongwen', _target='blank', _href=href))
        return UL(*[LI(link) for link in links], _class='list-inline')

    blocks = DIV(char_blocks(), _class='col-md-12 clearfix')
    links = DIV(char_links(), _class='col-md-12')
    bullets = DIV(char_bullets(), _class='col-md-12')
    return DIV([blocks, links, bullets], _class='row')

def pinyin_string(chars, uhdb):
    """ Return a pinyin string for the Unihan chars. """
    pinyin = u''
    chars = u' '.join(chars.decode('utf-8').split()) # Normalize whitespace.
    for char in chars:
        if char == u' ' and pinyin and not pinyin.endswith(u','):
            pinyin += u','
        else:
            codepoint = ord(char)
            row = uhdb.character[codepoint]
            if row:
                if pinyin:
                    pinyin += u' '
                if row.kMandarin:
                    pinyin += row.kMandarin.decode('utf-8')
                else:
                    pinyin += '???'
            elif pinyin and not pinyin.endswith(u','):
                pinyin += u','
    return pinyin.strip(u',')

def string_block(chars, strip, uhdb):
    """ Transform a string of characters into a block of elements. Return
    a DIVs of clickable info-block elements. """
    info = []
    chars = u' '.join(chars.decode('utf-8').split()) # Normalize whitespace.
    for char in chars:
        codepoint = ord(char)
        if char == u' ':
            info.append(char)
        elif codepoint == 9633: # Comparison with u'□' doesn't work.
            info.append(SPAN(char, _class='uh-char'))
        else:
            row = uhdb.character[codepoint]
            if row:
                info.append(_uh_repr(row))
            else:
                if strip:
                    if info and info[-1] != u' ':
                        info.append(u' ')
                else:
                    info.append(SPAN(char, _class='uh-char'))
    return DIV(info, _class='uh-block')
