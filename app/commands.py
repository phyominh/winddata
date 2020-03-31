import os
import csv
import click
import datetime
import pytz

from flask.cli import with_appcontext

from app.models import WindData

@click.command(name="dump_data")
@click.option('--f', help='File name')
@with_appcontext
def dump_data(f):
    tz = pytz.timezone('Asia/Yangon')
    path = os.path.join(os.getcwd(), f)
    with open(path, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            date = row[0]
            direction = 0 if row[5] == '' else int(row[5])
            speed = row[6]
            date_format = '%d-%m-%y %I:%M:%S %p'
            raw_date = datetime.datetime.strptime(date, date_format)
            local_date = tz.localize(raw_date)
            utc_date = local_date.astimezone(pytz.utc)
            WindData(speed=speed, direction=direction, timestamp=utc_date).save()
