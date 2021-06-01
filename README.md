# Cadence Calculator

<!-- **Read more about this project [here](https://walkercsutton.com/projects/cadence-calculator).** -->

<!-- [![Github All Releases](https://img.shields.io/github/downloads/walkersutton/cadence-calculator/total.svg)]() -->

Cadence Calculator is a tool for fixed gear riders that allows users to **add cadence data to your Strava/GPX activities.**

![Cadence Calculator](https://i.imgur.com/xoy5skH.png)

## Installation
Should you have any problems while installing or using the tool, please open up a [new issue](https://github.com/walkersutton/cadence-calculator/issues).
#### Basic
1. Download [this file](https://github.com/walkersutton/cadence-calculator/issues)
2. TODO
2. TODO
2. TODO

#### Advanced
1. ```git clone https://github.com/walkersutton/cadence-calculator.git```
2. ```cd cadence-calculator/```
3. ```pip install requirements.txt```
4. ```python main.py```
5. Follow the script's instructions

## Usage
#### Basic
1. Download your activity as a GPX file. [tutorial](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#:~:text=Export%20an%20Activity%20as%20a%20GPX%20file&text=Navigate%20to%20one%20of%20your,gpx%22.)
2. TODO
2. TODO
2. TODO
		DISCUSS STRAVA FLOW - DOWNLOAD, keep an original, delete from account, upload with cadence - verify everythign checks out - delete old GPX - CAREFUL ! DELETING ACTIVITIES IS FINAL -- KUDOS AND COMMENTS ARE NOT PRESERVED ACROSS DELETIONS


#### Advanced
1. Download your activity as a GPX file. [tutorial](https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#:~:text=Export%20an%20Activity%20as%20a%20GPX%20file&text=Navigate%20to%20one%20of%20your,gpx%22.)
2. ```dsadf```
2. TODO
2. TODO
2. TODO
		DISCUSS STRAVA FLOW - DOWNLOAD, keep an original, delete from account, upload with cadence - verify everythign checks out - delete old GPX - CAREFUL ! DELETING ACTIVITIES IS FINAL -- KUDOS AND COMMENTS ARE NOT PRESERVED ACROSS DELETIONS

## File Structure
```
├── LICENSE
├── README.md
├── requirements.text     # python dependencies
├── calculator.py         # cadence computation logic
├── main.py               # adds cadence values to a cadence-less GPX file
├── tester.py             # used to verify accuracy of computed cadence values
└── utils.py
```

## Caveats
If you encounter any complications, please open up a [new issue](https://github.com/walkersutton/cadence-calculator/issues).
* Developed and tested with ```Python 3.7.4```
* Not all GPX files are created equally - I may've missed a few cases where your GPX file has a different construction than the ones I used for testing.
* Generated cadence data quality reflects GPS data quality.

## Potential Improvements
I may try adding more functionality to Cadence Calculator in the future. Feel free to open a [pull request](https://github.com/walkersutton/cadence-calculator/pulls) if you'd like to help out. If you have any suggestions, you can open a pull request modifying the README, or send me a message me on [Twitter](https://twitter.com/walkercsutton).
* add support for Strava activity IDs
* automate adding cadence to newly completed activities
