@auth.requires_login()
def index():
    """ Show bans table. """
    db.define_table('bans',
        Field('src'),
        Field('timestamp', 'datetime', default=request.now),
        Field('urls', 'list:string'),
        Field('whois'))
    grid = SQLFORM.grid(
        db.bans,
        create=False,
        csv=False,
        editable=False,
        fields=[db.bans.src, db.bans.timestamp],
        orderby=~db.bans.timestamp,
        searchable=False)
    return {'grid': grid}
