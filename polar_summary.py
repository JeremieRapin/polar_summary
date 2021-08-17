#!/usr/bin/env python3

"""
polar_summary.py queries flow.polar.com and reports your
progress towards this years goal.

Requires a setting file with the following contents:

{
  "login": "FLOW_USERNAME",
  "password": "FLOW_PASSWORD",
  "sports": ["MOUNTAIN_BIKING", "TRAIL_RUNNING"]
}

"""

import argparse
import datetime
import json
import re
import requests
from prettytable import PrettyTable
from math import floor
from calendar import monthrange


FLOW_URL = 'https://flow.polar.com'
FLOW_LOGIN_POST_URL = "{}/login".format(FLOW_URL)
FLOW_LOGIN_GET_URL = FLOW_LOGIN_POST_URL
FLOW_GETREPORT_URL = "{}/progress/getReportAsJson".format(FLOW_URL)

def obtain_csrf(session):
    """
    Obtain the CSRF token from the login page.
    """
    resp = session.get(FLOW_LOGIN_GET_URL)
    contents = str(resp.content)
    match = re.search(r'csrfToken" value="([a-z0-9\-]+)"', contents)
    return match.group(1)

def login(username, password):
    """
    Logs in to the Polar flow webservice and returns
    a requests session to be used for further calls.
    """
    session = requests.session()
    csrf = obtain_csrf(session)
    postdata = {
        'csrfToken': csrf,
        'email': username,
        'password': password,
        'returnURL': '/'
    }

    resp = session.post(FLOW_LOGIN_POST_URL, data=postdata)
    if resp.status_code != 200:
        resp.raise_for_status()

    return session

def query_yearly_stats(session, sports, month, year, whole):
    """
    Request Polar flow for the given sports,
    for the year and month given in arguments.
    If whole is set, it will request for the whole year.
    """

    headers = {
        "x-requested-with": "XMLHttpRequest",
    }

    params = {
        "barType":"distance",
        "group":"day",
        "report":"custom",
        "reportSubtype":"training",
        "timeFrame":"month"
    }

    if whole:
        params['from'] = "01-01-{}".format(year)
        params['to'] = "31-12-{}".format(year)
        params['timeFrame'] = 'year'
    else:
        days = monthrange(int(year), int(month))
        params['from'] = "01-" + str(month) + "-{}".format(year)
        params['to'] = str(days[1]) + "-" + str(month) +"-{}".format(year)

    results = []
    total = {
        'name' : 'Total',
        'distance': 0,
        'duration': 0,
        'count': 0,
        'ascent': 0
    }
    for sport in sports:
        params['sport'] = [sport]
        resp = session.post(FLOW_GETREPORT_URL, json=params, headers=headers)
        if resp.status_code == 500:
            print(sport  + " is unknown")
            continue
        elif resp.status_code != 200:
            resp.raise_for_status()
        else:
            distance = float(resp.json()["progressContainer"]["trainingReportSummary"]["totalDistance"] / 1000)
            duration = int(resp.json()["progressContainer"]["trainingReportSummary"]["totalDuration"] / 1000)
            count = int(resp.json()["progressContainer"]["trainingReportSummary"]["totalTrainingSessionCount"])
            ascent = int(resp.json()["progressContainer"]["trainingReportSummary"]["totalAscent"])

            total['distance'] += distance
            total['duration'] += duration
            total['count'] += count
            total['ascent'] += ascent

            results.append({
                'name': sport,
                'distance': distance,
                'duration': duration,
                'count': count,
                'ascent': ascent,
            })

    results.append(total)

    return results

def getCurrentMonth():
    return datetime.datetime.now().month

def getCurrentYear():
    return datetime.datetime.now().year

def sortByCount(elem):
    return elem["count"]

def formatDuration(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return ("{h:02d}:{m:02d}:{s:02d}".format(h=hours, m=minutes, s=seconds))


def arrayDisplay(results):
    out = PrettyTable()

    out.field_names = ["Sport", "Distance", "Duration", "Count", "Ascent"]

    for result in results:
        if result['count'] != 0:
            out.add_row(
                [
                    result["name"],
                    round(result["distance"], 2),
                    formatDuration(result["duration"]),
                    result["count"],
                    floor(result["ascent"])
                ])

    print(out)


def main():
    """
    Main entrypoint parses startup arguments.
    """
    parser = argparse.ArgumentParser(description="Polar Flow progress summary",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", dest="config", help="the configuration file",
                        type=str, default="./summary_settings.json")
    parser.add_argument("--month", default=getCurrentMonth())
    parser.add_argument("--year", default=getCurrentYear())
    parser.add_argument("--whole", default=False, action='store_true')
    args = parser.parse_args()

    with open(args.config, 'r') as settings_file:
        settings = json.load(settings_file)

    session = login(settings["login"], settings["password"])
    arrayDisplay(query_yearly_stats(session, settings["sports"], args.month, args.year, args.whole))

if __name__ == "__main__":
    main()
