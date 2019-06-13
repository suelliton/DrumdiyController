from peewee import *
db = SqliteDatabase("database.db")
class Channel(Model):
    name = CharField()
    type = IntegerField()
    pin = IntegerField()
    note = IntegerField()
    threshold = IntegerField()
    scan = IntegerField()
    mask = IntegerField()
    retrigger = IntegerField()
    gain = IntegerField()
    curve = IntegerField()
    curveform = IntegerField()
    xtalk = IntegerField()
    xtalkgroup = IntegerField()
    image = CharField()
    x = FloatField()
    y = FloatField()
    width = FloatField()
    height = FloatField()
    selected = BooleanField()
    active = BooleanField()

    class Meta:
        database = db
db.create_tables([Channel])
