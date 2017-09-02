import xmlrpclib


@auth.requires_login()
def index():
    """ Add a firewall rule to allow remote host access to port 22. """
    response.title = 'SSH'
    form = FORM.confirm('Add exception')
    if form.accepted:
        try:
            ufwd = xmlrpclib.ServerProxy('http://localhost:8001')
            ufwd.allow(request.env.remote_addr, 'tcp', '22')
            response.flash = 'Allowing SSH from %s' % request.env.remote_addr
        except:
            logger.exception('ufwd allow exception')
            response.flash = 'Error allowing SSH from remote address'
    return {'form': form}
