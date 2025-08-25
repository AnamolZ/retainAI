import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")
st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    """
)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("### CSV Data")
    st.dataframe(data)

    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    categorical_columns = data.select_dtypes(include=['object', 'category']).columns

    st.write("### Chart Filters")

    selected_numeric = st.multiselect("Select column(s) to plot", numeric_columns, default=numeric_columns[:1])
    selected_categorical = st.selectbox("Filter by categorical column (optional)", [None] + list(categorical_columns))
    filter_value = None
    if selected_categorical:
        filter_value = st.selectbox(f"Select value for {selected_categorical}", data[selected_categorical].unique())

    filtered_data = data.copy()
    if selected_categorical and filter_value is not None:
        filtered_data = filtered_data[filtered_data[selected_categorical] == filter_value]

    if selected_numeric:
        st.write("### Chart")
        st.line_chart(filtered_data[selected_numeric])
    else:
        st.write("Select at least one numeric column to display the chart.")
