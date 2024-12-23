import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

orders_df = pd.read_csv("dashboard\orders_dataset.csv")
order_reviews_df = pd.read_csv('order_reviews_dataset.csv')
order_payments_df = pd.read_csv('dashboard/order_payments_dataset.csv')

merged_df = pd.merge(orders_df, order_reviews_df, on='order_id', how='left')
all_df = pd.merge(merged_df, order_payments_df, on='order_id', how='left')

all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

def create_monthly_orders_df(df):
    df = df.set_index('order_purchase_timestamp')
    monthly_orders_df = df.resample(rule='M').agg({
        'order_id': 'nunique'
    }).rename(columns={'order_id': 'order_count'}).reset_index()
    return monthly_orders_df

def create_review_score_counts(df):
    review_score_counts = df.groupby('review_score').agg({
        'review_id': 'count'
    }).rename(columns={'review_id': 'count'}).sort_values(by='count', ascending=False)
    return review_score_counts

def create_by_payment_type_df(df):
    by_payment_type = df.groupby('payment_type').agg({
        'order_id': 'count'
    }).rename(columns={'order_id': 'count'}).sort_values(by='count', ascending=False)
    return by_payment_type

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    months = pd.date_range(start=min_date, end=max_date, freq='MS')  # Bulan pertama setiap bulan
    start_month = st.select_slider(
        label='Pilih Bulan Mulai', 
        options=months.strftime('%Y-%m').tolist(),
        value=months[0].strftime('%Y-%m')
    )
    end_month = st.select_slider(
        label='Pilih Bulan Selesai',
        options=months.strftime('%Y-%m').tolist(),
        value=months[-1].strftime('%Y-%m')
    )

start_date = pd.to_datetime(start_month)
end_date = pd.to_datetime(end_month)

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= start_date) & 
    (all_df["order_purchase_timestamp"] <= end_date)
]

monthly_orders_df = create_monthly_orders_df(main_df)
review_score_counts = create_review_score_counts(main_df)
by_payment_type_df = create_by_payment_type_df(main_df)

st.header('Proyek Analisis Data: E-Commerce Public Dataset :sparkles:')

st.subheader('Monthly Orders')

total_orders = monthly_orders_df['order_count'].sum()
st.metric("Total orders", value=total_orders)

plt.figure(figsize=(10, 5))
plt.plot(monthly_orders_df['order_purchase_timestamp'], monthly_orders_df['order_count'], marker='o', linestyle='-', color='#186301')
plt.title('Tren Jumlah Order Berdasarkan Bulan Pembelian')
plt.xlabel('Bulan')
plt.ylabel('Jumlah Order')
plt.xticks(monthly_orders_df['order_purchase_timestamp'], monthly_orders_df['order_purchase_timestamp'].dt.strftime('%Y-%m'), rotation=75)
plt.tight_layout()

st.pyplot(plt)

st.subheader("Distribusi Skor Ulasan Pelanggan")

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

axes[0].bar(review_score_counts.index, review_score_counts['count'], color=['#186301', '#49a141', '#49a141', '#49a141', '#49a141'])
axes[0].set_title('Distribusi Skor Ulasan Pelanggan')
axes[0].set_xlabel('Skor Ulasan')
axes[0].set_ylabel('Jumlah Ulasan')

axes[1].pie(review_score_counts['count'], labels=review_score_counts.index, autopct='%1.1f%%', colors=['#186301', '#186301', '#49a141', '#49a141', '#49a141'])
axes[1].set_title('Persentase Ulasan Positif Berdasarkan Skor')

st.pyplot(plt)

st.subheader("Segmentasi Pelanggan Berdasarkan Metode Pembayaran")
plt.figure(figsize=(10, 5))
plt.barh(by_payment_type_df.index, by_payment_type_df['count'], color=['#186301', '#49a141', '#49a141', '#49a141', '#49a141'])
plt.title('Segmentasi Pelanggan Berdasarkan Metode Pembayaran')
plt.xlabel('Jumlah Pesanan')
plt.tight_layout()

st.pyplot(plt)
