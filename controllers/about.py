import os
from gluon.contrib.markdown import markdown2


def index():
    """ Return a dict for the about view. """

    def about_page():

        md_dir =  '/opt/ddj/book/markdown'
        logger.debug('Generating new about page')
        with open(os.path.join(md_dir, 'about.md')) as fd:
            about = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'copyright.md')) as fd:
            copyright = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'apology.md')) as fd:
            apology = markdown2.markdown(fd.read())
        with open(os.path.join(md_dir, 'references.md')) as fd:
            references = markdown2.markdown(fd.read())
        return {
            'about': about,
            'copyright': copyright,
            'apology': apology,
            'references': references}

    response.title = 'About the 道德經'
    return cache.ram('about', lambda: about_page())
