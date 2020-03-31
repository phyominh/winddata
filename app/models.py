from flask_mongoengine import MongoEngine

db = MongoEngine()

class WindData(db.Document):
    speed = db.DecimalField(precision=1)
    direction = db.IntField(min_value=0, max_value=360)
    timestamp = db.DateTimeField()
