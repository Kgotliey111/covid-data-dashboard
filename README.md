# COVID-19 Data Dashboard

A small Python script that reads daily COVID-19 numbers (5 March to 12 June 2020) and draws them as a chart: running totals on the left, new cases per day on the right.

![COVID-19 dashboard](covid_data.png)

## Getting started

You need Python 3.8+ and two libraries:

```bash
pip install pandas matplotlib
```

Put `covid.json` in the same folder as the script (the name must match exactly), then run:

```bash
python visualise_covid.py
```

The chart is saved as `covid_data.png` in the same folder.

## How it works

The data has some quirks: large numbers are stored as text with a space in them (like `"61 927"`), and one column name has a double space. The script cleans that up, then plots the totals and the daily new cases.

## What the data shows

- Confirmed cases grew from 1 to 61,927.
- The busiest day was 12 June, with 3,359 new cases.
- From 20 May, more people had recovered than were still active.

## Good to know

- File names are set inside the script, so edit `visualise_covid.py` to use other data.
- Daily deaths are loaded but not plotted yet.
