import xmlrpclib


ufwd_url = 'http://localhost:8001'

def _oncreate(form):
    """ Call ufwd to allow a new address to access port 22. """
    try:
        ufwd = xmlrpclib.ServerProxy(ufwd_url)
        ufwd.allow(form.vars.addr, 'tcp', 22)
    except:
        logger.exception('ufwd oncreate exception')
        response.flash = 'Error allowing address'

def _ondelete(table, row_id):
    """ Call ufwd to revoke port 22 access for an address. """
    try:
        ufwd = xmlrpclib.ServerProxy(ufwd_url)
        ufwd.revoke(db[table][row_id].addr, 'tcp', 22)
    except:
        logger.exception('ufwd ondelete exception')
        response.flash = 'Error deleting address'

def _populate(fake=None):
    ufwd = xmlrpclib.ServerProxy(ufwd_url)
    rules = ufwd.rules()
    if len(rules) != db(db.ssh).count():
        db.ssh.truncate()
        for rule in rules:
            if (
                    rule['action'] == 'allow'
                    and rule['protocol'] == 'tcp'
                    and rule['dport'] == '22'):
                db.ssh.insert(addr=rule['src'])
        logger.info('Populated ssh table from ufw data')

@auth.requires_login()
def index():
    """ Manage the firewall rules that allow access to port 22. """
    if not request.args:
        try:
            _populate()
        except:
            logger.exception('ufwd populate exception')
            return {'grid': 'Firewall service error'}
    db.ssh.addr.default = request.env.remote_addr
    db.ssh.addr.requires = [IS_IPV4(), IS_NOT_IN_DB(db, 'ssh.addr')]
    grid = SQLFORM.grid(
        db.ssh,
        createargs={'labels': {'addr': 'New Address'}},
        csv=False,
        details=False,
        editable=False,
        fields=[db.ssh.addr],
        headers={'ssh.addr': 'Allowed Addresses'},
        oncreate=_oncreate,
        ondelete=_ondelete,
        searchable=False,
        sortable=False)
    return {'grid': grid}
