import datetime
import dateutil
import json
import pytz
import urllib

CARDINAL_NAMES = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")

def datetime_object_from_url(url):
    safe_dt = urllib.parse.unquote(url)
    dt_object = dateutil.parser.parse(safe_dt)
    return dt_object.astimezone(pytz.utc)

def get_month_range_from_url(url):
    safe_dt = urllib.parse.unquote(url)
    dt_object = dateutil.parser.parse(safe_dt)
    date = dt_object.date()
    first_date = date + dateutil.relativedelta.relativedelta(day=1)
    last_date = date + dateutil.relativedelta.relativedelta(day=1, months=+1, days=-1)
    firt_dt = datetime.datetime.combine(first_date, datetime.datetime.min.time())
    last_dt = datetime.datetime.combine(last_date, datetime.datetime.max.time())
    first = firt_dt.astimezone(pytz.utc)
    last = last_dt.astimezone(pytz.utc)
    return first, last


def _change_deg_to_cardinal(data):
    if (data["direction"] > 348.75 and data["direction"] <= 360) or (data["direction"] >= 0 and data["direction"] <11.25):
        return "N"
    elif (data["direction"] > 11.25 and data["direction"] < 33.75):
        return "NNE"
    elif (data["direction"] > 33.75 and data["direction"] < 56.25):
        return "NE"
    elif (data["direction"] > 56.25 and data["direction"] < 78.75):
        return "ENE"
    elif (data["direction"] > 78.75 and data["direction"] < 101.25):
        return "E"
    elif (data["direction"] > 101.25 and data["direction"] < 123.75):
        return "ESE"
    elif (data["direction"] > 123.75 and data["direction"] < 146.25):
        return "SE"
    elif (data["direction"] > 146.25 and data["direction"] < 168.75):
        return "SSE"
    elif (data["direction"] > 168.75 and data["direction"] < 191.25):
        return "S"
    elif (data["direction"] > 191.25 and data["direction"] < 213.75):
        return "SSW"
    elif (data["direction"] > 213.25 and data["direction"] < 236.75):
        return "SW"
    elif (data["direction"] > 236.25 and data["direction"] < 258.75):
        return "WSW"
    elif (data["direction"] > 258.25 and data["direction"] < 281.75):
        return "W"
    elif (data["direction"] > 281.25 and data["direction"] < 303.75):
        return "WNW"
    elif (data["direction"] > 303.75 and data["direction"] < 326.25):
        return "NW"
    elif (data["direction"] > 326.25 and data["direction"] < 348.75):
        return "NNW"

def _change_data_to_range(data, range_lst, unit):
    for (lower, upper) in range_lst:
        if isinstance(data["speed"], str):
            break
        if (upper != None) and (data["speed"] >= lower and data["speed"] < upper):
            return str(lower) + " - " + str(upper) + " " + unit
        elif upper == None:
            return "> " + str(lower) + " " + unit

def get_average_wind_power_density(data):
    # air density at sea level and 15 degree celsius
    total = data.count()
    raw_data = json.loads(data.to_json())
    rho = 1.225
    cubic_speed = (x["speed"]**3 for x in raw_data)
    value = 0.5*rho*(sum(cubic_speed)/total)
    return round(value, 2)

def get_time_series(data):
    tz = pytz.timezone('Asia/Yangon')

    date_data = []
    for d in data:
        temp = {}
        temp["speed"] = float(d["speed"])
        t = tz.fromutc(d["timestamp"]).isoformat() + "+00:00"
        dt = datetime_object_from_url(t)
        temp["timestamp"] = int(dt.astimezone(tz).timestamp()) * 1000
        date_data.append(temp)

    time_series = []
    for d in date_data:
        speed = d["speed"]
        time = d["timestamp"]
        time_series.append([time, speed])
    return time_series

# def get_wind_rose(data):
#     raw_wind_rose = json.loads(data.to_json())

#     min_data = min((x["speed"] for x in raw_wind_rose))
#     max_data = max((x["speed"] for x in raw_wind_rose))
#     range_data = round((max_data - min_data)/6 , 2)

#     range_lst = []
#     lower = min_data
#     for i in range(0, 6):
#         if i == 5:
#             range_lst.append((lower, None))
#         else:
#             upper = lower + range_data
#             upper = round(upper, 2)
#             range_lst.append((lower, upper))
#             lower = upper

#     for i in range(0, len(raw_wind_rose)):
#         del raw_wind_rose[i]['timestamp']
#         _change_deg_to_cardinal(raw_wind_rose[i])
#         _change_data_to_range(raw_wind_rose[i], range_lst, "m/s")

#     for i in range(0, len(range_lst)):
#         if range_lst[i][1] != None:
#             range_lst[i] = str(range_lst[i][0]) + " - " + str(range_lst[i][1]) + " m/s"
#         else:
#             range_lst[i] = "> " + str(range_lst[i][0]) + " m/s"

#     wind_rose = []
#     total = len(raw_wind_rose)

#     for speed in range_lst:
#         template = {
#         "name" : "",
#         "data" : [
#                 ["N", 0],
#                 ["NNE", 0],
#                 ["NE", 0],
#                 ["ENE", 0],
#                 ["E", 0],
#                 ["ESE", 0],
#                 ["SE", 0],
#                 ["SSE", 0],
#                 ["S", 0],
#                 ["SSW", 0],
#                 ["SW", 0],
#                 ["WSW", 0],
#                 ["W", 0],
#                 ["WNW", 0],
#                 ["NW", 0],
#                 ["NNW", 0]
#             ]
#         }
#         template["name"] = speed
#         for d in template["data"]:
#             d[1] = round(
#                 sum(1 for x in raw_wind_rose
#                     if (x["direction"] == d[0] and x["speed"] == speed
#                 )
#             )/total*100, 2)
#         wind_rose.append(template)
#     return wind_rose


# This function is for chart.js datasets
def get_wind_rose(data):
    raw_wind_rose = json.loads(data.to_json())
    total = len(raw_wind_rose)

    min_data = min((x["speed"] for x in raw_wind_rose))
    max_data = max((x["speed"] for x in raw_wind_rose))
    range_data = round((max_data - min_data)/6 , 2)

    range_lst = []
    lower = min_data
    for i in range(0, 6):
        if i == 5:
            range_lst.append((lower, None))
        else:
            upper = lower + range_data
            upper = round(upper, 2)
            range_lst.append((lower, upper))
            lower = upper

    range_str = ["{} - {} m/s".format(x,y) if y is not None else "> {} m/s".format(x) for x,y in range_lst]
    datasets = [[0]*len(CARDINAL_NAMES) for _ in range(len(range_str))]

    for i in range(0, total):
        direction = _change_deg_to_cardinal(raw_wind_rose[i])
        speed = _change_data_to_range(raw_wind_rose[i], range_lst, "m/s")
        datasets[range_str.index(speed)][CARDINAL_NAMES.index(direction)] += 1

        if i == total - 1:
            datasets[range_str.index(speed)][CARDINAL_NAMES.index(direction)] = round(
                datasets[range_str.index(speed)][CARDINAL_NAMES.index(direction)] / total*100,
                2)

    wind_rose = {"datasets": datasets, "labels": range_str}
    return wind_rose
