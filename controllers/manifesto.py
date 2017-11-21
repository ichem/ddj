def index():
    """ Return a dict for the about view. """

    def manifesto_page():
        import os
        from gluon.contrib.markdown import markdown2

        md_dir =  '/opt/ddj/book/markdown'
        page = {}
        with open(os.path.join(md_dir, 'manifesto.md')) as fd:
            page['manifesto'] = markdown2.markdown(fd.read())
        return page

    response.title = '道德經 Manifesto'
    return cache.ram('manifesto_page', lambda: manifesto_page())
