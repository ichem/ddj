import xmlrpclib


@auth.requires_login()
def index():
    """ Add a firewall rule to allow remote host access to port 22. """
    response.title = 'SSH'
    form = FORM.confirm('Add exception')
    if form.accepted:
        try:
            fwd = xmlrpclib.ServerProxy('http://localhost:8001')
            fwd.allow(request.env.remote_addr)
            response.flash = 'Allowing SSH from %s' % request.env.remote_addr
        except:
            logger.exception('fwd allow exception')
            response.flash = 'Error allowing SSH from remote address'
    return {'form': form}
