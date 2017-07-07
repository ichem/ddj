# Unihan tables in sqlite db.
uhdb = DAL('sqlite:///opt/ddj/unihan10.sqlite', lazy_tables=True)
uhdb.define_table('character', # ID is the character's codepoint int.
    Field('codepoint'), # String encoding the codepoint, 'U+XXXX'.
    Field('kBigFive'),
    Field('kDefaultSortKey', 'integer'),
    Field('kDefinition'),
    Field('kFrequency'),
    Field('kGradeLevel'),
    Field('kMandarin'),
    Field('kRSUnicode'),
    Field('kSemanticVariant'),
    Field('kSimplifiedVariant'),
    Field('kSpecializedSemanticVariant'),
    Field('kTraditionalVariant'),
    Field('kZVariant'),
    Field('pRadicalID', 'integer'), # Radical's codepoint int.
    Field('pStrokes', 'integer'),
    Field('utf8'),
    migrate=False)
uhdb.define_table('radical', # ID is radical character's codepoint int.
    Field('pCharacter'),
    Field('pIdeograph'),
    Field('pNumber'),
    Field('pSimplified', 'boolean'),
    Field('utf8'),
    migrate=False)

# Library tables in app db.
db.define_table('book',
    Field('title'),
    Field('subtitle'))
db.define_table('chapter',
    Field('book', 'reference book'),
    Field('title'),
    Field('number', 'integer'))
db.define_table('verse',
    Field('book', 'reference book'),
    Field('chapter', 'reference chapter'),
    Field('en', 'text'),
    Field('hanzi', 'text'),
    Field('notes', 'text'),
    Field('number', 'integer'),
    Field('publish_en', 'boolean'),
    Field('publish_notes', 'boolean'))

# Blog table in app db.
db.define_table('post',
    Field('content', 'text'),
    Field('description', 'text'),
    Field('published', 'datetime'),
    Field('subtitle'),
    Field('title'))

# Server admin table.
db.define_table(
    'server_admin',
    Field('auth_user', 'reference auth_user'),
    Field('receive_ban_notifications', 'boolean'))

# Offender table.
db.define_table(
    'auth_offender',
    Field('attempts', 'integer'),
    Field('auth_users', 'list:reference auth_user'),
    Field('banned', 'boolean'),
    Field('last_attempt', 'datetime'),
    Field('remote_addr'))

# SSH access table.
db.define_table('ssh', Field('addr'))
