def index():
    """ Return a dict for the about view. """

    def about_page():
        import os
        from gluon.contrib.markdown import markdown2

        md_dir =  '/opt/ddj/book/markdown'
        page = {}
        with open(os.path.join(md_dir, 'about.md')) as fd:
            page['about'] = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'apology.md')) as fd:
            page['apology'] = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'appresources.md')) as fd:
            page['resources'] = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'copyright.md')) as fd:
            page['copyright'] = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'references.md')) as fd:
            page['references'] = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'contact.md')) as fd:
            page['contact'] = markdown2.markdown(fd.read())
        return page

    response.title = 'About the 道德經'
    return cache.ram('about', lambda: about_page())
