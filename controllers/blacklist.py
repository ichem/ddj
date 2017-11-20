@auth.requires_login()
def index():
    """ Show blacklist table. """
    from firewall import Blacklist

    response.title = 'Blacklist'
    Blacklist(db) # Inits db table.
    fields=[
        db.black.src,
        db.black.org,
        db.black.country,
        db.black.timestamp]
    grid = SQLFORM.grid(
        db.black,
        create=False,
        csv=False,
        editable=False,
        fields=fields,
        orderby=~db.black.timestamp,
        searchable=False)
    return {'grid': grid}
