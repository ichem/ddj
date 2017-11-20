@auth.requires_login()
def index():
    """ Show bans table. """
    from firewall import Blacklist

    Blacklist(db) # Inits db table.
    grid = SQLFORM.grid(
        db.bans,
        create=False,
        csv=False,
        editable=False,
        fields=[db.bans.src, db.bans.country, db.bans.timestamp],
        orderby=~db.bans.timestamp,
        searchable=False)
    return {'grid': grid}
