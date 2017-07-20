""" Provide basic globals. """
import logging
import os
import rsyslog
from gluon.contrib.memcache import MemcacheClient
from gluon.tools import Auth
from gluon.tools import Mail


def add_server_admin(form):
    """ Callback to add the logged-in user as a server admin. """
    if not db(db.auth_user).isempty():
        data = {
            'auth_user': auth.user.id,
            'receive_ban_notifications': True}
        db['server_admin'].insert(**data)
        logger.info('Added %s as initial server admin', auth.user.email)

def auth_buttons(form):
    """ Buttons for auth forms. """
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
    """ Set response.auth_navbar.  Called from the layout. """

    # Navbar might have been defined elsewhere
    if not response.auth_navbar:
        response.auth_navbar = auth.navbar(mode='dropdown')

    # Fix orphaned link.
    menu = response.auth_navbar.element('.dropdown-menu')
    if menu:
        links = menu.elements('a')
        if len(links) == 1:
            response.auth_navbar = LI(links[0], _class='dropdown')

def auth_title():
    """ Page title for auth form pages. """
    if request.args(0) == 'register':
        return T('Sign Up')
    if request.args(0) == 'login':
        return T('Log In')
    if request.args(0):
        return T(request.args(0).replace('_', ' ').title())
    return ''

def ban_event(event_type):
    """ Callback to ban excessive auth events. """
    addr = request.env.remote_addr
    email = request.post_vars.email
    auth_user = db(db.auth_user.email == email).select().first()
    logger.warning('Ban event %s from %s %s', event_type, addr, email)
    offender = db(db.auth_offender.remote_addr == addr).select().first()
    if offender:
        offender.attempts = offender.attempts + 1
        if offender.attempts > 5:
            offender.banned = True
        offender.last_attempt = request.now
        if auth_user and auth_user not in offender.auth_users:
            offender.auth_users.append(auth_user)
        offender.update_record()
        if offender.banned:
            run_ban_hooks(offender)
    else:
        auth_users = []
        if auth_user:
            auth_users.append(auth_user)
        data = {
            'attempts': 1,
            'auth_users': auth_users,
            'banned': False,
            'last_attempt': request.now,
            'remote_addr': addr}
        db['auth_offender'].insert(**data)

def ban_remote_addr(offender):
    """ Ban the offending IP address from the server. """
    import xmlrpclib

    url = 'http://localhost:8001'
    server = xmlrpclib.ServerProxy(url)
    server.ban(offender.remote_addr)
    for admin in db().select(db.server_admin.ALL):
        if admin.receive_ban_notifications:
            # TODO Send an email.
            pass

def run_ban_hooks(offender):
    """ Run all hooks in the ban_hooks list """
    for hook in ban_hooks:
        hook(offender)

# App config.
ban_hooks = [ban_remote_addr]
T.is_writable = False # No language file updates.
logger = rsyslog.getLogger('app', logging.INFO)
db = DAL('sqlite://app.db', lazy_tables=True)
cache.ram = MemcacheClient(request, ['127.0.0.1:11211'])
session.connect(request, response, db)
session.secure()
auth = Auth(
    db, propagate_extension='', controller='auth',
    secure=True, url_index=URL('default', 'index'))
auth.settings.actions_disabled.append('request_reset_password')
auth.settings.login_onfail.append(lambda form: ban_event('failed login'))
auth.settings.reset_password_onvalidation.append(
    lambda form: ban_event('password reset'))
auth.settings.register_onaccept.append(add_server_admin)
auth.define_tables(signature=True)
if not db(db.auth_user).isempty():
    auth.settings.actions_disabled.append('register')
mail = Mail('localhost:25', 'noreply@%s' % request.env.server_name, tls=False)
auth.settings.mailer = mail
auth.settings.logout_next = URL(args=request.args(0))
