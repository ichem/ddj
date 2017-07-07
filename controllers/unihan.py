from gluon.tools import Service


_service = Service()

def call():
    session.forget()
    return _service()

def dump():
    """ Return a form to transform pasted text to clickable chars. """
    response.title = 'Unihan Dump'
    attr = {
        '_class': 'nav navbar-nav',
        '_title': response.title}
    response.logo = LI(A(response.title, **attr))
    chars = DIV()
    pinyin = DIV()
    if auth.user_id:
        requires = IS_NOT_EMPTY()
    else:
        requires = [IS_NOT_EMPTY(), IS_LENGTH(maxsize=150)]
    form = SQLFORM.factory(
            Field('hanzi_text', 'text', requires=requires),
            Field('strip', 'boolean'))
    if form.process(keepvalues=True, onsuccess=None).accepted:
        from unihan import string_block

        try:
            chars, pinyin = string_block(
                form.vars.hanzi_text, form.vars.strip, uhdb)
        except:
            logger.exception("Error processing characters: %s" % request.vars)
            chars = DIV('Error processing characters')
    return {'chars': chars, 'pinyin': pinyin, 'form': form}

@_service.run
def info(char):
    """ A service to return character info as a block of HTML. """
    from unihan import char_info

    try:
        char_id = ord(char.decode('utf-8'))
        row = uhdb.character[char_id]
        return char_info(row, uhdb)
    except:
        logger.exception("No such character: %s" % char)
    return DIV('Error looking up character info')
