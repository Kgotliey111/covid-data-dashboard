import json
import pandas as pd
import matplotlib.pyplot as plt

data = pd.DataFrame(json.load(open("covid.json")))
data.columns = data.columns.str.split().str.join(" ")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")
data = data.apply(lambda c: c.astype(str).str.replace(" ", "").astype(int))

fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
data[["Total Confirmed Cases", "Active Cases", "Total Recovered", "Total Deaths"]].plot(ax=a, title="Cumulative")
b.bar(data.index, data["Daily Confirmed Cases"])
b.set_title("Daily new cases")
fig.autofmt_xdate() # this here will tilts the date labels so they don’t overlap.
plt.savefig("covid_data.png")# here i saved the graph as a png file in the current directory.
