# Polar summary

## Introduction

Polar summary is a little tool which queries the Polar Flow internal API (not the
[Polar accesslink API](https://www.polar.com/accesslink-api/) which is not suitable for this purpose). It is partly inspired on
[polar_progress](https://github.com/ElieDeBrauwer/polar_progress) but as the latter was also not really finished it does not depend on it directly.

Fill your username, password and list of sports. It will then create a month/year sport's summary.
By default, it's the current month of the current year which is requested.
Following the arguments, you can have a year summary.

## Installation

Clone this repository, make sure the [requests](http://docs.python-requests.org/) library is availabe and you're good to go.

## Usage

To make use of this polar summary you need a configuration file:

```javascript
{
  "login": "FLOW_USERNAME",
  "password": "FLOW_PASSWORD",
  "sports": ["MOUNTAIN_BIKING", "TRAIL_RUNNING"]
}
```

And then you can invoke the tool as follows :

``` bash
$./polar_summary.py -h
usage: polar_summary.py [-h] [--config CONFIG] [--month MONTH] [--year YEAR]
                        [--whole]

Polar Flow progress summary

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  the configuration file (default: ./summary_settings.json)
  --month MONTH
  --year YEAR

### Get current month summary
$ ./polar_summary.py
+-----------------+----------+----------+-------+--------+
|      Sport      | Distance | Duration | Count | Ascent |
+-----------------+----------+----------+-------+--------+
|      HIKING     |   12.6   | 02:29:49 |   1   |  700   |
| MOUNTAIN_BIKING |   26.8   | 02:28:42 |   2   |  1130  |
|  TRAIL_RUNNING  |  92.15   | 09:14:12 |   10  |  4030  |
```

### Get specific month summary

$ ./polar_summary.py --month 2 --year 2019

### Get whole year summary

$ ./polar_summary.py --whole --year 2017
