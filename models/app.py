""" Provide basic globals. """
import os
from gluon.contrib.memcache import MemcacheClient
from gluon.tools import Auth
from gluon.tools import Mail
import zero


def auth_buttons(form):
    """ Buttons for auth forms.  Called from view. """
    if request.args(0) == 'login':
        if 'register' not in auth.settings.actions_disabled:
            url_vars = None
            if request.vars._next:
                url_vars = {'_next': request.vars._next}
            url = URL(args='register', vars=url_vars)
            form.add_button(T('Sign Up'), url, _class='btn btn-default')
        if 'request_reset_password' not in auth.settings.actions_disabled:
            url = URL(args='request_reset_password')
            form.add_button(T('Lost Password'), url, _class='btn btn-default')

def auth_navbar():
    """ Fix response.auth_navbar.  Called from view. """
    menu = response.auth_navbar.element('.dropdown-menu')
    if menu:
        links = menu.elements('a')
        if len(links) == 1:
            response.auth_navbar = LI(links[0], _class='dropdown')

def auth_title():
    """ Page title for auth form pages. Called from view. """
    if request.args(0) == 'register':
        return T('Sign Up')
    if request.args(0) == 'login':
        return T('Log In')
    if request.args(0):
        return T(request.args(0).replace('_', ' ').title())
    return ''

def log(event, request_url):
    """ Log bannable events. """
    from abuse import Bans

    banner = Bans(db)
    banner.log(event, request_url)

# Basic app config.
logger = zero.getLogger('app')
T.is_writable = False # No language file updates.
db = DAL('sqlite://app.db', lazy_tables=True)
cache.ram = MemcacheClient(request, ['127.0.0.1:11211'])

# Log and redirect HTTP requests to HTTPS.
if request.env.server_port == '80':
    logger.info('aye')
    auth = Auth(db, controller='auth', secure=False)
    auth.define_tables(signature=True)
    log('301', request.env.request_uri)
    redirect(URL('poems', 'index', scheme='https'), 301)

# Session/auth config.
session.connect(request, response, db)
session.secure()
auth = Auth(
    db, propagate_extension='', controller='auth',
    secure=True, url_index=URL('default', 'index'))
auth.define_tables(signature=True)
if not db(db.auth_user).isempty():
    auth.settings.actions_disabled.append('register')
auth.settings.actions_disabled.append('request_reset_password')
auth.settings.login_onfail.append(lambda form: log('Failed login', '/login'))
auth.settings.logout_next = URL(args=request.args)
