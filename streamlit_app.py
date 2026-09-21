import math
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.title("Data App Assignment, on October 6th")

st.write("### Input Data and Examples")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum(numeric_only=True))
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the dataframe index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(
    df.groupby("Category", as_index=False).sum(numeric_only=True),
    x="Category",
    y="Sales",
    color="#04f",
)

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# We create a working copy/view for time aggregation so main df keeps Order_Date column for filtering later
df_time = df.set_index("Order_Date")
sales_by_month = (
    df_time.filter(items=["Sales"]).groupby(pd.Grouper(freq="M")).sum()
)

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

st.write("## Your additions")

# (1) Add a drop down for Category
st.write(
    "### (1) add a drop down for Category"
    " (https://docs.streamlit.io/library/api-reference/widgets/st.selectbox)"
)
categories = df["Category"].unique()
selected_category = st.selectbox("Select a Category", categories)

# (2) Add a multi-select for Sub_Category in the selected Category
st.write(
    "### (2) add a multi-select for Sub_Category *in the selected Category (1)*"
    " (https://docs.streamlit.io/library/api-reference/widgets/st.multiselect)"
)
sub_categories = df[df["Category"] == selected_category][
    "Sub_Category"
].unique()
selected_sub_categories = st.multiselect(
    "Select Sub-Categories", sub_categories
)

# Filter dataframe based on selections
if selected_sub_categories:
  filtered_df = df[
      (df["Category"] == selected_category)
      & (df["Sub_Category"].isin(selected_sub_categories))
  ]
else:
  filtered_df = df[df["Category"] == selected_category]

# (3) Show a line chart of sales for the selected items
st.write(
    f"### Sales Over Time for: {selected_category} -> {selected_sub_categories}"
)
if not filtered_df.empty:
  filtered_time_df = filtered_df.set_index("Order_Date")
  filtered_sales_by_month = (
      filtered_time_df.filter(items=["Sales"])
      .groupby(pd.Grouper(freq="M"))
      .sum()
  )
  st.line_chart(filtered_sales_by_month, y="Sales")
else:
  st.warning("Please select at least one Sub-Category.")

# (4) & (5) Show three metrics with delta on profit margin
st.write("### Performance Metrics")

if not filtered_df.empty:
  # Calculate overall dataset metrics for comparison (Step 5 delta baseline)
  total_sales_all = df["Sales"].sum()
  total_profit_all = df["Profit"].sum()
  overall_avg_profit_margin = (
      (total_profit_all / total_sales_all) * 100
      if total_sales_all > 0
      else 0
  )

  # Calculate metrics for selected items
  total_sales_sel = filtered_df["Sales"].sum()
  total_profit_sel = filtered_df["Profit"].sum()
  selected_profit_margin = (
      (total_profit_sel / total_sales_sel) * 100 if total_sales_sel > 0 else 0
  )

  # Delta: difference between selected profit margin and overall average profit margin
  margin_delta = selected_profit_margin - overall_avg_profit_margin

  # Display the three metrics in columns
  col1, col2, col3 = st.columns(3)
  col1.metric("Total Sales", f"${total_sales_sel:,.2f}")
  col2.metric("Total Profit", f"${total_profit_sel:,.2f}")
  col3.metric(
      "Overall Profit Margin (%)",
      f"{selected_profit_margin:.2f}%",
      delta=f"{margin_delta:.2f}% vs Overall Avg",
  )
else:
  st.info("Select sub-categories above to view metrics.")
