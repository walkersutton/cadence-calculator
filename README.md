# Cadence Calculator

![Cadence Calculator Logo](https://i.imgur.com/XCdXTfzt.jpg)

<!-- **Read more about this project [here](https://walkercsutton.com/projects/cadence-calculator).** -->

![Cadence Data Generation](https://i.imgur.com/ThHWdmr.gif)

Cadence Calculator **generates cadence data for your fixed gear GPX activities.**

## Connect with Strava
[Automatically generate cadence data for your Strava activities](https://cadencecalculator.herokuapp.com)

## Getting Started
Should you have any problems while installing or using the tool, please open up a [new issue](https://github.com/walkersutton/cadence-calculator/issues).

## File Structure
```
.
├── Procfile                # Heroku deployment requirement
├── config.py               # environment variables
├── flaskr                  #
│   ├── __init__.py         # core Flask module
│   ├── activities.py       #
│   ├── auth.py             # authentication magic
│   ├── bike.py             #
│   ├── cadence.py          #
│   ├── gpx.py              #
│   ├── subscriptions.py    # subscription management
│   ├── tester.py           # used to verify accuracy of computed cadence values
│   ├── utils.py            #
│   ├── static              #
│   ├── templates           # HTML templates for rendering webpages
│   └── tests               #
├── lint.sh                 #
├── requirements.txt        # python dependencies
└── setup.py                #
```

### Requirement
* `Python 3` (currently on 3.8.2; probably works on other versions as well?)

## Setup
```sh
git clone https://github.com/walkersutton/cadence-calculator.git
cd cadence-calculator/
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Running
```sh
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

## Warnings
* Not all GPX files are created equally - I may've missed a few cases where your GPX file has a different construction than the ones I used for testing.
* Generated cadence data quality reflects GPS data quality.

## TODO
* investigate https://github.com/tkrajina/gpxpy
* create tests -> publish accuracy
* DISCUSS STRAVA FLOW
* DOWNLOAD
* keep an original
* delete from account
* upload with cadence
* verify everythign checks out
* delete old GPX - CAREFUL ! DELETING ACTIVITIES IS FINAL -- KUDOS AND COMMENTS ARE NOT PRESERVED ACROSS DELETIONS
