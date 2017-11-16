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
    """ Log bad event. At least some of this should be queued. """

    db.define_table('bans',
        Field('src'),
        Field('timestamp', 'datetime', default=request.now),
        Field('urls', 'list:string'),
        Field('whois'))

    # Update db or cache with the new request.
    src = request.env.remote_addr
    logger.warning('Logging %s %s from %s', event, request_url, src)
    row = db(db.bans.src==src).select().first()
    if row:
        row.urls += (src, event, request_url)
        urls = row.urls
        row.update_record()
    else:
        urls = cache.ram('events-%s' % src, lambda: [])
        urls.append((src, event, request_url))
        urls = cache.ram('events-%s' % src, lambda: urls, 0)

    # Blacklist the IP when a threshold is reached.
    if not row and len(urls) == 4:
        import socket
        from subprocess import check_output

        # Add a db record.
        try:
            whois = check_output('whois %s' % src, shell=True)
        except:
            logger.exception('Bad whois request')
        db.bans.insert(src=src, urls=urls, whois=whois)

        # Email the admin.
        hostname = socket.gethostname()
        subject = 'Ban event on %s' % hostname
        mailer = Mail('localhost:25', 'noreply@%s' % hostname, tls=False)
        admin = db(db.auth_user).select().first()
        if admin and admin.email:
            mailer.send(admin.email, subject, whois)
            logger.info('Ban email sent to %s', admin.email)
        else:
            logger.error('Error finding app admin email address')

    # Do firewall.
    if len(urls) >= 4:
        import xmlrpclib

        try:
            fwd = xmlrpclib.ServerProxy('http://localhost:8001')
            fwd.blacklist(src)
        except:
            logger.exception('Blacklist error')

# Basic app config.
logger = zero.getLogger('app')
T.is_writable = False # No language file updates.
db = DAL('sqlite://app.db', lazy_tables=True)
cache.ram = MemcacheClient(request, ['127.0.0.1:11211'])

# Log and redirect HTTP requests to HTTPS.
if request.env.server_port == '80':
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
