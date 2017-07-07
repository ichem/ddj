# Blog table in app db.
db.define_table('post',
    Field('content', 'text'),
    Field('description', 'text'),
    Field('published', 'datetime'),
    Field('subtitle'),
    Field('title'))
