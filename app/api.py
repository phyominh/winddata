import datetime
import json
import pytz

from flask import request, Blueprint, jsonify

from mongoengine.queryset.visitor import Q

from .models import WindData
from .utils import (
    datetime_object_from_url,
    get_month_range_from_url,
    get_wind_rose, get_time_series,
    get_average_wind_power_density
)

api = Blueprint('api', __name__)

@api.route('/live-data', methods=['GET'])
def get_latest_data():
    req_url = request.args.get("timestamp")
    dt_object = datetime_object_from_url(req_url)
    data = WindData.objects(timestamp=dt_object).exclude('id')
    data_json = json.loads(data.to_json())
    for i in range(0, len(data_json)):
        data_json[i]['timestamp'] = data[i]['timestamp'].isoformat() + "+00:00"
    return jsonify(data_json), 200

@api.route('/date-data', methods=['GET'])
def get_date_data():
    req_url = request.args.get("for")
    dt_object = datetime_object_from_url(req_url)
    dt_object_next_day = dt_object + datetime.timedelta(days=1)

    raw_date_data = WindData.objects(
        Q(timestamp__gte=dt_object) & Q(timestamp__lt=dt_object_next_day)
    ).exclude('id')

    total_date_data = raw_date_data.count()
    date_lst = (x["speed"] for x in raw_date_data)
    daily_mean = round(float(sum(date_lst))/total_date_data, 2)

    wind_power_density = get_average_wind_power_density(raw_date_data)

    time_series = get_time_series(raw_date_data)
    
    wind_rose = get_wind_rose(raw_date_data)

    data = {
        'mean': daily_mean,
        'wind_power_density': wind_power_density,
        'time_series': time_series,
        'wind_rose': wind_rose
    }

    return jsonify(data), 200

@api.route('/date-range-data', methods=['GET'])
def get_date_range_data():
    req_url = request.args.get("until")
    dt_object = datetime_object_from_url(req_url)
    dt_object_start_day = datetime.datetime.combine(dt_object.date(), datetime.datetime.min.time())

    raw_date_data = WindData.objects(
        Q(timestamp__gte=dt_object_start_day) & Q(timestamp__lt=dt_object)
    ).exclude('id')

    time_series = get_time_series(raw_date_data)

    data = {
        'range_data': time_series
    }

    return jsonify(data), 200

@api.route('/range-data', methods=['GET'])
def get_range_data():
    from_time = request.args.get("from")
    to_time = request.args.get("to")
    from_object = datetime_object_from_url(from_time)
    to_object = datetime_object_from_url(to_time)

    raw_range_data = WindData.objects(
        Q(timestamp__gte=from_object) & Q(timestamp__lte=to_object)
    ).exclude('id')

    total_range_data = raw_range_data.count()
    range_lst = (x["speed"] for x in raw_range_data)
    range_mean = round(float(sum(range_lst))/total_range_data, 2)

    wind_power_density = get_average_wind_power_density(raw_range_data)
    
    time_series = get_time_series(raw_range_data)

    wind_rose = get_wind_rose(raw_range_data)

    data = {
        'mean': range_mean,
        'wind_power_density': wind_power_density,
        'time_series': time_series,
        'wind_rose': wind_rose
    }

    return jsonify(data), 200
