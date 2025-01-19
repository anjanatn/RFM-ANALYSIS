import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the dataset (now .xlsx file)
df = pd.read_excel('C:/Users/user/Desktop/rfm_analysis/online_retail.xlsx', engine='openpyxl')

# Step 2: Data Cleaning
df = df.dropna(subset=['CustomerID'])
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# Step 3: Calculate RFM Metrics
reference_date = df['InvoiceDate'].max()
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',                                   # Frequency
    'TotalPrice': 'sum'                                       # Monetary
})
rfm.columns = ['Recency', 'Frequency', 'Monetary']
rfm = rfm.reset_index()

# Step 4: Score RFM Metrics
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

# Corrected Frequency Binning: Now with 4 labels
rfm['F_Score'] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4], duplicates='drop')

rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# Step 5: Customer Segmentation
def segment_customer(row):
    if row['RFM_Score'] == '555':
        return 'VIP'
    elif row['RFM_Score'][0] == '5':
        return 'Loyal'
    elif row['RFM_Score'][1] == '5':
        return 'Frequent Buyer'
    elif row['RFM_Score'][2] == '5':
        return 'Big Spender'
    else:
        return 'Others'

rfm['Segment'] = rfm.apply(segment_customer, axis=1)

# Step 6: Visualization
plt.figure(figsize=(10, 6))
sns.countplot(data=rfm, x='Segment', order=rfm['Segment'].value_counts().index)
plt.title('Customer Segments')
plt.xlabel('Segment')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

# Heatmap of RFM Scores
rfm_heatmap = rfm.pivot_table(index='R_Score', columns='F_Score', values='Monetary', aggfunc='mean')
sns.heatmap(rfm_heatmap, cmap='Blues', annot=True, fmt='.0f')
plt.title('Heatmap of RFM Scores')
plt.show()
