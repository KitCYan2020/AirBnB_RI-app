import streamlit as st
import pandas as pd
import altair as alt
import scipy.stats as stats
import numpy as np


df = pd.read_csv("listings.csv")
st.set_page_config(page_title="AirBnB Dashboard", layout="wide")
st.title("AirBnB Rhode Island")


type_counts = df['host_since'].apply(type).value_counts()

# Convert the string to mm/dd/year format and get just the year from the date. Put this in a new column called "Year Joined"
df['host_since'] = pd.to_datetime(df['host_since'], format='%Y-%m-%d')

df['Year Joined'] = df['host_since'].dt.year

line_chart = (
    alt.Chart(df)
    .mark_line(color='red', point=True)
    .encode(
      x=alt.X('Year Joined:N', title='Year Joined'),
      y=alt.Y('count():Q', title='Number of Host joined'),
    ).properties(
      title='Number of Hosts Joining AirBnb in Rhode Island',
      width=500,
      height=500,
    )
)
st.altair_chart(line_chart, use_container_width=True)

min_accommodates = int(df['accommodates'].min())
max_accommodates = int(df['accommodates'].max())

selected_accommodates = st.sidebar.slider(
    "Accommodates",
    min_value=min_accommodates,
    max_value=max_accommodates,
    value=min_accommodates,
    step=1
)

# Filter the dataframe based on the number of people it can accomodate
filtered_df = df[df['accommodates'] == selected_accommodates]

# Chart Properties
chart_width  = 500
chart_height = 500
common_properties = {
    "width": chart_width,
    "height": chart_height
}

# --- Click selection on the neighborhood bars ---
# This lets a click on a bar in the neighborhoods chart drive the property type chart
neighborhood_click = alt.selection_point(
    fields=["neighbourhood_cleansed"],
    name="neighborhood_select",
    empty=True,   # when nothing is clicked, treat as "all selected"
)

# Top neighborhoods (now clickable)
neighborhoods_chart = (
    alt.Chart(filtered_df)
    .transform_aggregate(
        neighborhood_count="count()",
        groupby=["neighbourhood_cleansed"]
    )
    .transform_window(
        rank="rank(neighborhood_count)",
        sort=[alt.SortField("neighborhood_count", order="descending")]
    )
    .transform_filter(
        alt.datum.rank <= 15
    )
    .mark_bar()
    .encode(
        y=alt.Y(
            "neighbourhood_cleansed:N",
            sort="-x",
            title="Neighborhood"
        ),
        x=alt.X(
            "neighborhood_count:Q",
            title="Property Count"
        ),
        color=alt.condition(
            neighborhood_click,
            alt.value("steelblue"),
            alt.value("lightgray")
        ),
        tooltip=[
            alt.Tooltip("neighbourhood_cleansed:N", title="Neighborhood"),
            alt.Tooltip("neighborhood_count:Q", title="Property Count")
        ]
    )
    .add_params(neighborhood_click)
    .properties(
        title=f"Top 15 Neighborhoods (Accommodates: {selected_accommodates})",
        **common_properties
    )
)

# Property type breakdown, filtered by whichever neighborhood is clicked
property_type_chart = (
    alt.Chart(filtered_df)
    .transform_filter(neighborhood_click)
    .transform_aggregate(
        property_count="count()",
        groupby=["room_type"]
    )
    .transform_window(
        rank="rank(property_count)",
        sort=[alt.SortField("property_count", order="descending")]
    )
    .transform_filter(
        alt.datum.rank <= 10
    )
    .mark_bar(color="blue")
    .encode(
        y=alt.Y("room_type:N", sort="-x", title="Property Type"),
        x=alt.X("property_count:Q", title="Number of Listings"),
        tooltip=["room_type:N", "property_count:Q"]
    )
    .properties(
        title="Property Types (click a neighborhood to see available listings)",
        **common_properties
    )
)

# Display charts - neighborhoods first since it's now the "driver" chart
chart = alt.hconcat(neighborhoods_chart, property_type_chart)
st.altair_chart(chart, use_container_width=True)