# Cadence Calculator

![Cadence Calculator Logo](https://i.imgur.com/XCdXTfzt.jpg)

<!-- **Read more about this project [here](https://walkercsutton.com/projects/cadence-calculator).** -->

![Cadence Data Generation](https://i.imgur.com/ThHWdmr.gif)

Cadence Calculator **generates cadence data for your fixed gear GPX activities.**

## Connect with Strava
[Automatically generate cadence data for your Strava activities](https://cadencecalculator.herokuapp.com)

## Getting Started
Should you have any problems while installing or using the tool, please open up a [new issue](https://github.com/walkersutton/cadence-calculator/issues).

### Requirement
* `Python 3` (currently on 3.8.2; probably works on other versions as well?)

## Setup
1. `git clone https://github.com/walkersutton/cadence-calculator.git`
2. `cd cadence-calculator/`
3. `python3 -m venv venv`
4. `source venv/bin/activate`
5. `pip install -e .`
<!--6. `python3 -m pip install -r requirements.txt` - not sure if this is required anymore-->
6. `flask run` 


## Usage
1. Download your activity as a GPX file. [tutorial](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#:~:text=Export%20an%20Activity%20as%20a%20GPX%20file&text=Navigate%20to%20one%20of%20your,gpx%22.)
2. TODO
- DISCUSS STRAVA FLOW
- DOWNLOAD
- keep an original
- delete from account
- upload with cadence
- verify everythign checks out
- delete old GPX - CAREFUL ! DELETING ACTIVITIES IS FINAL -- KUDOS AND COMMENTS ARE NOT PRESERVED ACROSS DELETIONS

## File Structure
TODO
```
├── LICENSE
├── README.md
├── requirements.txt     # python dependencies
├── calculator.py         # cadence computation logic
├── main.py               # adds cadence values to a cadence-less GPX file
├── tester.py             # used to verify accuracy of computed cadence values
└── utils.py
```

## Warnings
* Not all GPX files are created equally - I may've missed a few cases where your GPX file has a different construction than the ones I used for testing.
* Generated cadence data quality reflects GPS data quality.

## TODO
* investigate https://github.com/tkrajina/gpxpy
* create tests -> publish accuracy
