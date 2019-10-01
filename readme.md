# igclib

## Get started

```{shell}
git clone https://github.com/teobouvard/igclib.git
cd igclib
pip3 install virutalenv
python3 -m venv venv
source venv/bin/activate
pip3 install wheel
pip3 install -r requirements.txt
python3 igclib/main.py
```

## Data collection

To fetch the IGC tracks, run `python3 crawlers/crawler_tracks.py`  
To fetch the tasks, run `python3 crawlers/crawler_tasks.py`

## Todo

### Library

* add other features to ```pilot_features()```
* write native code for distance calculation

### Data collection

* parallellize requests when fetching data
* merge tasks and tracks

## Requirements

* Python 3.6 or higher