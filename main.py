# import libraries
import streamlit as st
import pandas as pd
import altair as alt

# set wide app layout
st.set_page_config(layout='wide')

# load Superstore data
df = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQMqC_6fkaH6oZweJDIIYFDdE9o3P3G1hB0OKLzkGGf0pB-FjWJoAMoYca2iXV2ID5dE7hoklCSx6hE/pub?gid=0&single=true&output=csv')

# preprocess data
df['order_date'] = pd.to_datetime(df['order_date'])
df['ship_date'] = pd.to_datetime(df['ship_date'])
df['order_year'] = df['order_date'].dt.year

# print dataframe
# st.dataframe(df)

CURR_YEAR = max(df['order_date'].dt.year)
PREV_YEAR = CURR_YEAR - 1

# app title
st.title("Superstore Dashboard")

# Compute yearly total sales, banyaknya order, banyaknya kosumen, profit %
data = pd.pivot_table(
    data=df,
    index='order_year',
    aggfunc={
        'sales':'sum',
        'profit':'sum',
        'order_id':pd.Series.nunique,
        'customer_id':pd.Series.nunique
    }
).reset_index()

data['pct_profit'] = 100.0 * data['profit'] / data['sales']

# st.dataframe(data)

# First Section
st.header("Performance vs Previous Year")

# create 4 columns to show metrics
mx_sales, mx_order, mx_customer, mx_pct_profit = st.columns(4)

def format_big_number(num):
    if num >= 1e6:
        return f"{num / 1e6:.2f} Mio"
    elif num >= 1e3:
        return f"{num / 1e3:.2f} K"
    else:
        return f"{num:.2f}"

def format_int_number(num):
    return '{:,}'.format(num)

with mx_sales:
    curr_sales = data.loc[data['order_year']==CURR_YEAR, 'sales'].values[0]
    prev_sales = data.loc[data['order_year']==PREV_YEAR, 'sales'].values[0]
    sales_diff_pct = 100.0 * (curr_sales - prev_sales) / prev_sales
    st.metric("Sales", value=format_big_number(curr_sales), delta=f'{sales_diff_pct:.2f}%')

with mx_order:
    curr_order = data.loc[data['order_year']==CURR_YEAR, 'order_id'].values[0]
    prev_order = data.loc[data['order_year']==PREV_YEAR, 'order_id'].values[0]
    order_diff_pct = 100.0 * (curr_order - prev_order) / prev_order
    st.metric("Number of Order", value=format_int_number(curr_order), delta=f'{order_diff_pct:.2f}%')

with mx_customer:
    curr_customer = data.loc[data['order_year']==CURR_YEAR, 'customer_id'].values[0]
    prev_customer = data.loc[data['order_year']==PREV_YEAR, 'customer_id'].values[0]
    customer_diff_pct = 100.0 * (curr_customer - prev_customer) / prev_customer
    st.metric("Number of Customer", value=format_int_number(curr_customer), delta=f'{customer_diff_pct:.2f}%')

with mx_pct_profit:
    curr_pct_profit = data.loc[data['order_year']==CURR_YEAR, 'pct_profit'].values[0]
    prev_pct_profit = data.loc[data['order_year']==PREV_YEAR, 'pct_profit'].values[0]
    pct_profit_diff_pct = 100.0 * (curr_pct_profit - prev_pct_profit) / prev_pct_profit
    st.metric("Profit %", value=f'{curr_pct_profit:.2f}%', delta=f'{pct_profit_diff_pct:.2f}%')


# Second Section
st.header("Sales Trend")

freq = st.selectbox("Freq", ['Daily','Monthly'])

timeUnit = {
    'Daily':'yearmonthdate',
    'Monthly':'yearmonth'
}

# Line plot of sales
sales_line = alt.Chart(df[df['order_year']==CURR_YEAR]).mark_line().encode(
    alt.X('order_date', title='Order Date', timeUnit=timeUnit[freq]),
    alt.Y('sales', title='Sales', aggregate='sum')
)

st.altair_chart(sales_line,use_container_width=True)


# Third Section: Sales performance by category for each segment
st.header("Category Sales Performance by Segment")

# bar chart
bar_chart = alt.Chart(df[df['order_year']==CURR_YEAR]).mark_bar().encode(
    column='category:N',
    y='sum(sales):Q',
    color='segment:N',
    x='segment:N'
).properties(width=350,height=220)

st.altair_chart(bar_chart)

# Fourth Section: Profit vs Sales correlation
st.header("Sales vs Profit Correlation")

# create 3 columns with width ratio of 1:2:1
# only use the middle one
_, midcol, _ = st.columns([1, 2, 1])

with midcol:
    scatter = alt.Chart(df[(df['order_year']==CURR_YEAR)&(df['sales']<6000)]).mark_point().encode(
        x='sales:Q',
        y='profit:Q',
        color='region:N',
    )
    st.altair_chart(scatter, use_container_width=True)
