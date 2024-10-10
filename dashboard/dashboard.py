import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(products_order_info):
    daily_orders_df = products_order_info.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)  
    return daily_orders_df



def create_sum_order_items_df(products_order):
    sum_order_items_df = products_order.groupby(by="product_category_name").order_id.nunique().sort_values(ascending=False).reset_index()
    return sum_order_items_df



def create_mean_products_reviews_df(products_reviews):
    mean_products_reviews_df = products_reviews.groupby("product_category_name").review_score.mean().sort_values(ascending=False).reset_index()
    mean_products_reviews_df.head(10)
    return mean_products_reviews_df



def create_top_cities_customers_df(customers):
    top_cities_customers_df = customers.groupby(by="customer_city")["customer_unique_id"].nunique().sort_values(ascending=False).reset_index()
    top_cities_customers_df = top_cities_customers_df.head(5)
    return top_cities_customers_df




def create_rfm_df(customers_order_info):
    rfm = customers_order_info.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"})
    rfm.columns = ["customer_unique_id", "max_order_purchase_timestamp", "frequency", "monetary"]
    rfm["customer_unique_id"] = rfm["customer_unique_id"].apply(lambda x: x[-5:])
    rfm["max_order_purchase_timestamp"] = rfm["max_order_purchase_timestamp"].dt.date
    recent_date = customers_order_info["order_purchase_timestamp"].dt.date.min()
    rfm["recency"] = rfm["max_order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm.drop("max_order_purchase_timestamp", axis=1, inplace=True)
    return rfm



all_df = pd.read_csv("dashboard/all_df.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])



min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 


with st.sidebar:
    st.image("dashboard/e-commerce logo.png")
    
    start_date, end_date = st.date_input(
        label='Range Time', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

st.write(f"Start Date: {start_date}")
st.write(f"End Date: {end_date}")



daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
mean_products_reviews_df = create_mean_products_reviews_df(main_df)
top_cities_customer_df = create_top_cities_customers_df(main_df)
rfm = create_rfm_df(main_df)


st.header("E-Commerce Public Dashboard")

st.subheader("Daily Orders")
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#825B32"
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)



st.subheader("Best & Worst Performing Product Category")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 15))
 
colors = ["#FFAD60", "#ECDFCC", "#ECDFCC", "#ECDFCC", "#ECDFCC"]
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=35)
ax[0].set_title("Best Performing Product", loc="center", fontsize=55)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=35)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=55)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


fig, ax = plt.subplots(figsize=(30, 15))

colors = ["#507687", "#507687", "#507687", "#8EACCD", "#8EACCD", "#8EACCD", "#8EACCD", "#8EACCD", "#8EACCD" , "#8EACCD"]
sns.barplot(
    x="review_score",
    y="product_category_name",
    data=mean_products_reviews_df.head(10),
    hue=None,
    palette=colors,
    legend=False,
    ax=ax
)

ax.set_title("Mean Review Score", loc="center", fontsize=55)
ax.set_ylabel(None)
ax.set_xlabel("Review Score", fontsize=35)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)


st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(30, 15))
colors = ["#522258", "#B692C2", "#B692C2", "#B692C2" , "#B692C2"]
sns.barplot(
    x="customer_city",
    y="customer_unique_id",
    data=top_cities_customer_df.head(5),
    hue=None,
    palette=colors,
    legend=False
)
plt.ylabel("Total Customer", fontsize=35)
plt.xlabel(None)
plt.title("Top 5 City by Total Customer", loc="center", fontsize=55)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)

st.pyplot(fig)


st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm.monetary.mean(), "USD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(40, 15))
 
colors = ["#939185", "#939185", "#939185", "#939185", "#939185"]
 
sns.barplot(y="recency", x="customer_unique_id", data=rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=55)
ax[0].tick_params(axis ='x', labelsize=30)
ax[0].tick_params(axis ='y', labelsize=30)
 
sns.barplot(y="frequency", x="customer_unique_id", data=rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=55)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].tick_params(axis='y', labelsize=30)
 
sns.barplot(y="monetary", x="customer_unique_id", data=rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=55)
ax[2].tick_params(axis='x', labelsize=30)
ax[2].tick_params(axis='y', labelsize=30)

st.pyplot(fig)


st.caption('Copyright (c) adhnilaa')
