"""
    Author: Prakash S/O A Divakaran

    This streamlit app allows users to analyze and see the
    - EPS Surprise % vs 3-Month Change in Closing Price %
    by interactively selecting various tickers and executing a pipeline
    to extract, clean and transform data for analysis from yahoo finance.
"""

from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import magma
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from yahoo_fin import stock_info as si


def scatterplot(data, option):
    """
    This function performs a scatter plot of
    the processed data and filters tickers if
    option is provided.

    Args:
     data: data to plot
     option: tickers to filter data by

    Returns:
     nil
    """
    data = data[data['ticker'].isin(option)]
    index_cmap = factor_cmap(
        'ticker',
        palette=magma(len(data['ticker'].unique())),
        factors=sorted(data['ticker'].unique())
    )

    p = figure(
        height=400,
        toolbar_location=None,
        tools='hover',
        x_axis_label='EPS Surpise %',
        y_axis_label='Change in 3-Month Closing Price %',
        title="Relationship between EPS Surprise and \
         Change in 3 Month Closing Price"
        )

    p.scatter(
        'epssurprisepct',
        'close_change',
        source=data,
        size=20,
        color=index_cmap,
        legend_group='ticker'
        )
    st.bokeh_chart(p, use_container_width=True)


def clean_transform(earnings_data, price_data, i):
    """
    This function cleans, transforms and merges the earnings data and
    price data for a ticker to produce a df that contains the eps surprise %
    and 3-month change in closing price in %

    Args:
     earnings_data: earnings data for each ticker
     price_data: price data containing OHLC and volume data
     i: index of data being processed

    Returns:
     processed dataframe for ticker

    """
    df = pd.DataFrame()
    for item in earnings_data:
        try:
            startdatetime = item['startdatetime'].split('T')
            # causes exception if key(date) not present
            s1 = price_data.loc[startdatetime[0]]
            df.loc[i, 'date'] = startdatetime[0]
            df.loc[i, 'close'] = s1['close']
            df.loc[i, 'ticker'] = s1['ticker']
            df.loc[i, 'epssurprisepct'] = item['epssurprisepct']
            i += 1
        except:
            pass

    # reverse order, calculate closing % change for every quarter
    # and shift one step up.
    if 'close' in df.columns:
        df = df.iloc[::-1]
        df = df.reset_index(drop=True)
        df['close_change'] = df['close'].pct_change()*100
        df['close_change'].fillna(0, inplace=True)
        # shift up !
        df['close_change'].iloc[
            0:len(df['close_change'])-1
            ] = df['close_change'].iloc[1:]
        # setting last change to zero as we don't know future price change !
        df['close_change'].iloc[len(df['close_change'])-1] = 0

    return df, i


def get_ticker_data(tickers, from_yahoo=False):
    """
    This function get the earnings and price data for each ticker
    either from yahoo finance or from a prepared CSV file and creates
    a processed dataframe of all tickers.

    Args:
     tickers: list of tickers to extract
     from_yahoo: if to download data from yahoo_finanace

    Returns:
     processed dataframe containing all tickers

    """
    df_final = pd.DataFrame()
    i = 0
    for ticker in tickers:
        df = pd.DataFrame()
        if from_yahoo:
            earnings_data = si.get_earnings_history(ticker)
            earnings_data_pd = pd.DataFrame(earnings_data)
            earnings_data_pd.to_csv(ticker+'_earnings.csv')
            price_data = si.get_data(ticker)
            price_data_pd = pd.DataFrame(price_data)
            price_data_pd.to_csv(ticker+'_prices.csv')
        else:
            earnings_data_pd = pd.read_csv(
                './data/' + ticker + '_earnings.csv', index_col=0
                )
            earnings_data = earnings_data_pd.to_dict('records')
            price_data_pd = pd.read_csv(
                './data/' + ticker + '_prices.csv', index_col=0
                )
            price_data = price_data_pd

        df, i = clean_transform(earnings_data, price_data, i)
        df_final = pd.concat([df_final, df])
        df_final = df_final.reset_index(drop=True)

    return df_final


def heatmap(data):
    """
    This function plots a heatmap of the correlation
    between epssurprisepct and close_change

    Args:
     data: processed dataframe

    Returns:
     nil
    """
    data_corr = data[['epssurprisepct', 'close_change', ]].corr()
    fig = plt.figure(figsize=(10, 4))
    sns.heatmap(data_corr)
    st.pyplot(fig)


def create_view(data, op):
    """
    This function creates the views on streamlit using the data
    given either for the dow jones tickers or selected tickers

    Args:
     data: processed dataframe
     op: either dow or non_dow

    Returns:
     nil
    """
    checkboxIQR = st.checkbox(
        "Use Interquartile Range (Remove Outliers)"
    )
    if op == 'dow':
        option_dow = st.multiselect(
                'Drill Down',
                data['ticker'].unique().tolist(),
                data['ticker'].unique().tolist(),
        )
    else:
        option_dow = data['ticker'].unique().tolist()

    val = data[data['ticker'].isin(option_dow)]
    msg = "The pearson correlation coefficient is : " + \
        str(np.around(val.corr().loc[
            'close_change',
            'epssurprisepct'
            ] * 100, 2)) + "%"
    st.write(msg)

    col1, col2 = st.columns(2)
    with col1:
        if checkboxIQR:
            values = st.slider(
             'Select interquartile range',
             0.0, 100.0, (25.0, 75.0)
            )

            iqr = data.loc[
                data['epssurprisepct'].between(
                    data['epssurprisepct'].quantile(values[0]/100),
                    data['epssurprisepct'].quantile(values[1]/100),
                    inclusive=True
                    ),
                :
            ]
            scatterplot(iqr, option_dow)

        else:
            scatterplot(data, option_dow)
    with col2:
        st.write("DataFrame")
        st.write(data[data['ticker'].isin(option_dow)])

    st.header("Heatmap of Correlation")
    heatmap(data[data['ticker'].isin(option_dow)])


st.set_page_config(layout="wide")

st.title('EPS Surprise VS 3-Month Closing Price')
st.write(
    """FOMO (Fear of misssing out) is a phenomenon that has caused people to
    take positions in stocks before a major annoucement. One major
    annoucement that follows every quarter in the US is the earnings call
    for respective stocks.During the earnings call, one might be
    interested to know whether the company beat the analyst estimates
    for Earnings Per Share (EPS). Also, the corollary is whether
    it moves the stock price significantly for that quarter after
    the announcement.In this analysis, we are using
    the percentage change in the 3-month closing price for that quarter and
    plot it wrt to the EPS surprise percent which is the % difference between
    the estimated EPS and actual EPS for that quarter."""
)

st.markdown(
    "Simply put, **does beating analyst estimates affect stock \
    price positively in the upcoming quarter?**"
    )

# We will analyse this using the 30 DOW stocks from Yahoo Finance.")
checkBox = st.checkbox('Use DOW Tickers', True)

if checkBox:

    data = pd.read_csv(
        './data/dow_epsSurprise_vs_closing.csv',
        index_col=0
    )

    create_view(data, op='dow')

else:
    selected_stocks = st.multiselect(
     'Which ticker would you like to analyze?',
     ('MSFT', 'GOOG', 'TSLA')
    )

    if selected_stocks:
        with st.spinner('Wait for it...'):
            processed_df = get_ticker_data(
                list(selected_stocks),
                from_yahoo=False
            )
            create_view(processed_df, op='non_dow')
