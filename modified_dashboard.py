import pandas as pd
import streamlit as st
import datetime
from datetime import datetime 
current_time=datetime.now 
import hashlib
import os
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)


#costom css
st.markdown(
"""

 <style>
[data-testid="stSidebar"]{
    background: linear-gradient(white, #4CAF50, #FFEB3B);
   
}


[data-testid="stSidebarRadio"]{
    background-color:#061fab;
    color:white;
}
    /* Sidebar title */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: white; /* Blue for headers */
    }

    [data-testid="stSidebar"] .css-16idsys,
    /* Sidebar radio button labels */
    [data-testid="stSidebar"].element-container label {
        color: white; /* Green for navigation text */
        font-weight: bold;
    }

    [data-testid="stSidebar"].element-container label:hover {
        color: orange; /* orange on hover */
        font-weight: bold;
    }

        /* Entire page background gradient */
    .stApp {
        background: linear-gradient(to right, #FFCC00, #06ab71);
        color: black;
    }


 </style>
""",
unsafe_allow_html=True
)

if st.button("Test Save Data"):
    data = {
        "name": "Test User",
        "zone": "Mbulu",
        "product_name": "Soap",
        "quantity": 5,
        "unit_price": 2000,
        "total_earnings": 10000
    }
    supabase.table("records").insert(data).execute()
    st.success("Data saved successfully!")


