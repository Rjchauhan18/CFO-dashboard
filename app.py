import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="CFO Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    # Replace with your data source
    return pd.read_excel('mock_data_updated.xlsx')

data = load_data()

# Dashboard title
st.title("CFO Dashboard")
st.write("---")
# Sidebar filters
st.sidebar.header("Filter Options")
selected_month = st.sidebar.multiselect("Select Month", options=data['Month'].unique(), default=data['Month'].unique())
selected_region = st.sidebar.multiselect("Select Region", options=data['Region'].unique(), default=data['Region'].unique())
selected_type = st.sidebar.multiselect("Select Type (AP/AR)", options=data['Type'].unique(), default=data['Type'].unique())

# st.write(selected_month,selected_region,selected_type)
if len(selected_month)==0 or len(selected_region)==0 or len(selected_type)==0:
    st.warning("Please select appropriate data in sidebar")
    st.stop()
# Apply filters
filtered_data = data[
    (data['Month'].isin(selected_month)) &
    (data['Region'].isin(selected_region)) &
    (data['Type'].isin(selected_type))
]


# Summary section
total_expenses = filtered_data['Amount'].sum()
total_sales = filtered_data['Sales'].sum()
profit_or_loss = total_sales - total_expenses

if profit_or_loss > 0:
    profit_or_loss_text = "Profit"
    profit_or_loss_color = "normal"
else:
    profit_or_loss_text = "Loss"
    profit_or_loss_color = "normal"

# Detailed breakdown: AP and AR split
ap_ar_split = filtered_data.groupby('Type')['Amount'].sum()

# Display metrics in columns
col1, col2, col3,col4,col5 = st.columns(5)

with col1:
    st.metric(profit_or_loss_text,
        f"₹ {profit_or_loss:,.2f}", 
        )

with col2:
    st.metric("Total Expenses", f"₹ { total_expenses:,.2f}", delta=None)

with col3:
    st.metric("Total Sales", f"₹ {total_sales:,.2f}", delta=None)

with col4:
    if 'AP' in ap_ar_split:
        st.metric("Total AP", f"₹ {ap_ar_split['AP']:,.2f}", delta=None)
with col5:
    if 'AR' in ap_ar_split:

        st.metric("Total AR", f"₹ {ap_ar_split['AR']:,.2f}", delta=None)


# Expenses section
expense_by_category = filtered_data.groupby('Expense Category')['Amount'].sum().reset_index()
fig_expenses = px.bar(
    expense_by_category, 
    x='Expense Category', 
    y='Amount', 
    title="Total Expenses by Category", 
    text_auto=True,
    color_discrete_sequence=["#20C20E", "#33FF57", "#3357FF"]  

)

# Sales section
sales_by_region = filtered_data.groupby('Region')['Sales'].sum().reset_index()
fig_sales = px.pie(
    sales_by_region, 
    names='Region', 
    values='Sales', 
    title="Sales Distribution by Region",
    color_discrete_sequence=["#FF0000", "#20C20E", "#3357FF","#FFA500"] 

)

expense, sales = st.columns(2)

with expense:
    st.plotly_chart(fig_expenses, use_container_width=True)

with sales:
    st.plotly_chart(fig_sales, use_container_width=True)

# AP and AR Aging section
st.header("AP and AR Aging Analysis")
aging_data = filtered_data.groupby(['Type', 'Aging Bucket'])['Amount'].sum().reset_index()
fig_aging = px.bar(
    aging_data, 
    x='Aging Bucket', 
    y='Amount', 
    color='Type', 
    barmode='group', 
    color_discrete_sequence=["#FF0000", "#20C20E", "#3357FF"] 

)
st.plotly_chart(fig_aging, use_container_width=True)


# AP and AR Multiline Chart
st.header("AP and AR Trend Over Time")
time_series_data = filtered_data.groupby(['Month', 'Type'])['Amount'].sum().reset_index()

fig_multiline = px.line(
    time_series_data, 
    x='Month', 
    y='Amount', 
    color='Type', 
    markers=True,
    color_discrete_sequence=["#FF0000", "#20C20E", "#20C20E"]  

)
fig_multiline.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount (₹)",
    legend_title="Type",
    hovermode="x unified"
)
st.plotly_chart(fig_multiline, use_container_width=True)

# Footer
st.sidebar.info("Use the filters above to customize the analysis.")

st.table(data)