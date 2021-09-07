# Cadence Calculator App

<!-- **Read more about this project [here](https://walkercsutton.com/projects/cadence-calculator).** -->

![Cadence Calculator Logo](https://i.imgur.com/XCdXTfzt.jpg)

Should you have any problems while installing or using this app, please open up a [new issue](https://github.com/walkersutton/cadence-calculator-app/issues).

### Requirement
* `Python 3` (currently on 3.8.2; probably works on other versions as well?)

## Setup
1. `git clone https://github.com/walkersutton/cadence-calculator-app.git`
2. `cd cadence-calculator-app/`
3. `python3 -m venv venv`
4. `source venv/bin/activate`
5. `python3 -m pip install -r requirements.txt`

## Running
1. `export FLASK_APP=app`
2. `export FLASK_ENV=development`
3. `flask run`

## File Structure
```
├── AWSCLIV2.pkg        # AWS CLI buildpack for Heroku (might not need)
├── Procfile            # Heroku deployment requirement
├── README.md
├── activities.py       # TODO
├── app.py              # core Flask module
├── auth.py             # authentication magic
├── config.py           # environment variables
├── requirements.txt    # Python dependencies
├── static
│   ├── css
│   │   └── styles.css
│   └── fonts
│       ├── Lato
│       │   └─ *
│       └── Raleway
│           └─ *
├── templates           # HTML templates for rendering webpages
│   ├── auth.html
│   ├── base.html
│   └── index.html
├── tests
│   ├── run_tests.sh
│   ├── test_activities.py
│   ├── test_auth.py
│   ├── test_endpoints.py
│   ├── test_subscriptions.py
│   └── test_webhooks.py
├── subscriptions.py    # subscription management
└── webhooks.py         # webhook event handling
```
