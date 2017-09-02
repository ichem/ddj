def search():
    """ Return either a list of books that contain all chars in the chars
    var, or if a book's hanzi title is in vars, a list of all verses in the
    specified book that contain all the chars. """
    if request.vars.chars:

        # Validate the chars to search for.
        char_list = []
        for char in request.vars.chars.decode('utf-8'):
            if uhdb.character[ord(char)]:
                char_list.append(char.encode('utf-8'))
        if not char_list:
            raise HTTP(404)

        # Allow only authorized users to search ctext books.
        requested_book = request.vars.book
        if not auth.user and requested_book != '道德經':
            HTTP(404)
        if not auth.user:
            requested_book = '道德經'

        # Generate a list of verses or a list of books.
        if requested_book:

            # All verses containing the chars.
            book = db(db.book.title==requested_book).select().first()
            if not book:
                raise HTTP(404)
            response.title = 'Verses in %s containing %s'
            response.title = response.title % (book.title, ''.join(char_list))
            qry = db.verse.hanzi.contains(char_list, all=True)
            rows = db((db.verse.book==book.id)&(qry)).select(
                    orderby=db.verse.id)
            chars = ''.join(char_list).decode('utf-8')
            verses = DIV(_class='row')
            for row in rows:
                pid = 'pid-%d' % row.id
                href = URL('studies', 'chapter', args=[row.chapter.number])
                label = 'Chapter %d' % row.chapter.number
                label = A(label, _href=href, _style='color:inherit;')
                label = DIV(LABEL(label, _for=pid), _class='col-md-2')
                hanzi = []
                for char in row.hanzi.decode('utf-8'):
                    span = SPAN(char, _class='uh-char')
                    if char in chars:
                        span['_style'] = 'color:red;'
                    hanzi.append(span)
                hanzi = DIV(hanzi, _class='col-md-10', _id=pid)
                verses.append(DIV(label, hanzi, _class='row'))
            result = DIV(H4(response.title), DIV(*verses))
        else:

            # A list of links to a per-book search for the chars.
            response.title = 'Books containing %s' % ''.join(char_list)
            count = db.book.id.count()
            qry = db.verse.hanzi.contains(char_list, all=True)
            rows = db((db.book.id==db.verse.book)&(qry)).select(
                db.book.id, db.book.subtitle, db.book.title, count,
                groupby=db.book.id, orderby=db.book.id)
            links = UL()
            for row in rows:
                rvars = {'chars': ''.join(char_list), 'book': row.book.title}
                link = '%s %s' % (row.book.subtitle, row[count])
                link = A(link, _href=URL('library', 'search', vars=rvars))
                links.append(link)
            result = DIV(H4(response.title), links)
        return {'result': result}
    raise HTTP(404)
