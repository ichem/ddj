# Unihan tables.
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

# Library tables.
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
    Field('number', 'integer'))

# Post tables.
db.define_table('commentary',
    Field('title'),
    Field('published', 'datetime'),
    Field('intro', 'text'),
    Field('content', 'text'))

db.define_table('poem',
    Field('chapter', 'reference chapter'),
    Field('published', 'datetime'),
    Field('intro_hanzi'),
    Field('intro_en'))
