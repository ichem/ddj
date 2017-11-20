import xmlrpclib


@auth.requires_login()
def index():
    """ Whitelist the remote that clicks the button. """
    response.title = 'Whitelist'
    form = FORM.confirm('Add exception')
    if form.accepted:
        from firewall import Whitelist

        whitelist = Whitelist()
        whitelist.add(request.env.remote_addr)
    return {'form': form}
