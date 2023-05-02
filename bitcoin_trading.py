from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pytz
import requests
import boto3
import csv

today = datetime.now()
current_date = today.strftime("%d/%m/%y")
current_time = today.strftime("%H:%M:%S")

url = "https://api.coindesk.com/v1/bpi/currentprice.json" 
response = requests.get(url)
data = response.json()
bitcoin_price = data["bpi"]["USD"]["rate"]

bucket_name = "cluut-aws-developer-kurs-marcel-langer-04-03-2023"
file_name = "bitcoin_prices.csv"
key = "trading/" + file_name

s3 = boto3.client("s3")
try:
    s3.download_file(bucket_name, key, file_name)
except:
    print("Das Objekt existiert noch nicht!")
finally:
    with open(file_name, "a") as file:
        file.write(f"{current_date};{current_time};{bitcoin_price}\n")
        
s3.upload_file(file_name, bucket_name, key)
prices = pd.read_csv(file_name, sep=";", header=None, thousands=",")
prices.columns = ["date", "time", "price"]

prices = prices[prices.date == current_date]
prices["time"] = pd.to_datetime(prices["time"], format='%H:%M:%S').dt.strftime('%H:%M:%S')

plot_file_name = f'bitcoin_price_{current_date.replace("/","_")}.png'
sns.set_theme()
sns.set_context("paper", rc={"font.size": 4, "axes.titlesize": 10})
sns_plot = sns.lineplot(x="time", y="price", data=prices)
sns_plot.set_title(f'Bitcoin Preise vom {current_date}')
sns_plot.set_ylabel("Bitcoin Preis in $")
sns_plot.set_xticklabels(prices["time"], rotation=45, horizontalalignment='right')
sns_plot.get_figure().savefig(plot_file_name, bbox_inches='tight')
sns_plot.figure.clf()

s3.upload_file(plot_file_name, bucket_name, "trading/plots/"+ plot_file_name)


