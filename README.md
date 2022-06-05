# EPS Surprise vs 3-Month Stock Price Change Analysis App

## Introduction
This App is used to analyze if beating analyst EPS estimates positively affects stocks prices for that quarter.

![alt text](./images/Screenshot%202022-06-05%20at%201.22.58%20PM.png)

By default, this app will show you the correlation using a scatter plot and heatmap of the EPS Surprise % VS the Change in 3-Month Stock Price for that quarter for the 30 DOW Tickers. 

This App allows you to filter the tickers and also remove outliers 

![alt text](./images/Screenshot%202022-06-05%20at%201.27.20%20PM.png)

For now, it supports 3 Non-Dow Tickers for analysis as well: 
![alt text](./images/Screenshot%202022-06-05%20at%201.30.11%20PM.png)

## Demo
This app has been deployed to Heroku and can be accessed at

Details of this analysis can be found in the jupyter notebook

> An Analysis of EPS Surprise Percent VS Change in Closing Price .ipynb

## Installation
After cloning the repo, you can run this on your own local machine as well. 

> Python Version 3.9.12

Create a virtual environment and install the dependencies:

`pip install -r requirements.txt`

To run this app:

`streamlit run epsVsPriceApp.py`

