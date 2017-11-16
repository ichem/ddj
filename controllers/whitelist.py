import xmlrpclib


@auth.requires_login()
def index():
    """ Whitelist the remote that clicks the button. """
    response.title = 'Whitelist'
    form = FORM.confirm('Add exception')
    if form.accepted:
        try:
            fwd = xmlrpclib.ServerProxy('http://localhost:8001')
            fwd.add('whitelist', request.env.remote_addr)
            response.flash = 'Whitelisted %s' % request.env.remote_addr
        except:
            logger.exception('Whitelist error')
            response.flash = 'Error whitelisting address'
    return {'form': form}
