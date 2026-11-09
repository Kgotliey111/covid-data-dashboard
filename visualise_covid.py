import json
import pandas as pd
import matplotlib.pyplot as plt

covid_df = pd.DataFrame(json.load(open("covid.json")))
covid_df.columns = covid_df.columns.str.split().str.join(" ")
covid_df["Date"] = pd.to_datetime(covid_df["Date"])
covid_df = covid_df.set_index("Date")
covid_df = covid_df.apply(lambda column: column.astype(str).str.replace(" ", "").astype(int))

figure, (cumulative_ax, daily_ax) = plt.subplots(1, 2, figsize=(13, 5))
covid_df[["Total Confirmed Cases", "Active Cases", "Total Recovered", "Total Deaths"]].plot(ax=cumulative_ax, title="Cumulative")
daily_ax.bar(covid_df.index, covid_df["Daily Confirmed Cases"])
daily_ax.set_title("Daily new cases")
figure.autofmt_xdate() 
plt.savefig("covid_data.png")
