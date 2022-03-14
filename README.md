# Cadence Calculator

![Cadence Calculator Logo](https://i.imgur.com/XCdXTfzt.jpg)

<!-- **Read more about this project [here](https://walkercsutton.com/projects/cadence-calculator/todo).** -->

![Cadence Data Generation](https://i.imgur.com/ThHWdmr.gif)

Cadence Calculator **generates cadence data for your fixed gear GPX activities.**

## Connect with Strava
[Automatically generate cadence data for your Strava activities](https://cadecalc.app)

## Getting Started
Should you have any problems while installing or using the tool, please open up a [new issue](https://github.com/walkersutton/cadence-calculator/issues).

### Requirement
* `Python 3`

## Setup
```sh
git clone https://github.com/walkersutton/cadence-calculator.git
cd cadence-calculator/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
```sh
flask run -h 0.0.0.0 -p 5000  # debug logging turned on - not a production server
OR
heroku local
Open http://127.0.0.1:5000 in a browser.
```

## Feature Requests
* Add support for more data streams (power, temperature, etc.)
* Store gear ratios

## TODO
* investigate https://github.com/tkrajina/gpxpy
* create tests -> publish accuracy
* keep an original
* delete from account
* upload with cadence
* verify everythign checks out
* delete old GPX - CAREFUL ! DELETING ACTIVITIES IS FINAL -- KUDOS AND COMMENTS ARE NOT PRESERVED ACROSS DELETIONS

## Warnings
* Not all GPX files are created equally - I may've missed a few cases where your GPX file has a different construction than the ones I used for testing.
* Generated cadence data quality reflects GPS data quality.

<!-- 
running with db
i removed an instances/ folder in root with a sql file file
$ flask init-db
$ flask run

$ pip install '.[test]'
$ pytest

Run with coverage report::

$ coverage run -m pytest
$ coverage report
$ coverage html  # open htmlcov/index.html in a browser -->