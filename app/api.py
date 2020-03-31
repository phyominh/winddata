import datetime
import json
import pytz

from flask import request, Blueprint, jsonify

from mongoengine.queryset.visitor import Q

from .models import WindData
from .utils import (
    datetime_object_from_url,
    get_month_range_from_url, change_deg_to_cardinal,
    change_data_to_range, get_wind_rose, get_time_series,
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

@api.route('/month-data', methods=['GET'])
def get_month_data():
    from_time = request.args.get("from")
    to_time = request.args.get("to")
    from_object = datetime_object_from_url(from_time)
    to_object = datetime_object_from_url(to_time)

    raw_month_data = WindData.objects(
        Q(timestamp__gte=from_object) & Q(timestamp__lte=to_object)
    ).exclude('id')

    total_month_data = raw_month_data.count()
    month_lst = (x["speed"] for x in raw_month_data)
    monthly_mean = round(float(sum(month_lst))/total_month_data, 2)

    wind_power_density = get_average_wind_power_density(raw_month_data)
    
    time_series = get_time_series(raw_month_data)

    wind_rose = get_wind_rose(raw_month_data)

    data = {
        'mean': monthly_mean,
        'wind_power_density': wind_power_density,
        'time_series': time_series,
        'wind_rose': wind_rose
    }

    return jsonify(data), 200
