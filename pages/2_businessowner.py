elif role == "Business Owner":
        #Donors sidebar
        menu_business_owner = st.sidebar.radio("Business Owner Links", [
            "🏠 Business Owner Dashboard.",
            "📤 Pakia bidhaa/Import(Excel).",
            "📋 List ya Bidhaa Ulizosajili.",
            "👥 Assign Shopkeepers.",
            "Angalia duka",
            "Sajili Duka",
            "Matumizi"
        ])

        # Add more donor-related content
        # You can add content or visuals for the donor reports here
        # Example donor data

        if menu_business_owner == "🏠 Business Owner Dashboard.":
            st.subheader("🏠 Business Owner Dashboard")
      
        # Start csv/excell upload

        elif menu_business_owner=="📤 Pakia bidhaa/Import(Excel).":
             st.subheader("📤 Pakia Bidhaa kwa Excel (Bulk Import)")
             st.write("Pakia file la Excel lenye bidhaa zako zote.")
             
             # 1. File Uploader
             uploaded_file = st.file_uploader("Chagua file la Excel (.xlsx)", type=["xlsx"])
             
             if uploaded_file is not None:
                 try:
                     # 2. Read the Excel file
                     df = pd.read_excel(uploaded_file)
                     
                     st.write("Hakiki data zako hapa chini:")
                     st.dataframe(df.head()) # Show first 5 rows to the user
             
                     if st.button("Anza Kupakia Sasa (Start Upload)"):
                         # 3. Add the Owner's ID to every row automatically
                         # This ensures the items belong to this specific Business Owner
                         df['user_id'] = st.session_state.user_id
                         
                         # 4. Convert the DataFrame to a list of dictionaries for Supabase
                         data_to_insert = df.to_dict(orient="records")
                         
                         # 5. Execute the Bulk Insert
                         conn.table("inventory_items").insert(data_to_insert).execute()
                         
                         st.success(f"Hongera! Bidhaa {len(data_to_insert)} zimeingizwa kwenye kanzidata yako.")
                         st.rerun()
             
                 except Exception as e:
                     st.error(f"Kuna tatizo kwenye file lako: {e}")

        # End of csv/excell items uploads

        
        # startsView registerd 
        elif menu_business_owner == "📋 List ya Bidhaa Ulizosajili.":
             st.subheader("📋 Orodha ya Bidhaa Zako (Your Item Catalog)")
             
             if "user_id" in st.session_state:
                 try:
                     # 1. FETCH data for the logged-in user
                     res = conn.table("inventory_items").select("*").eq("user_id", st.session_state.user_id).execute()
                     
                     if res.data:
                         df_items = pd.DataFrame(res.data)
                         
                         # Professional Summary Metrics
                         m1, m2 = st.columns(2)
                         m1.metric("Total Items", len(df_items))
                         inventory_value = (df_items['buying_price'] * df_items['current_stock']).sum()
                         m2.metric("Inventory Value", f"Tsh {inventory_value:,.0f}")
         
                         # Display Table
                         st.dataframe(
                             df_items[["item_name", "category", "buying_price", "selling_price", "current_stock", "unit_measure"]], 
                             use_container_width=True, 
                             hide_index=True
                         )
         
                         # --- 2. UPDATE & DELETE LOGIC ---
                         st.divider()
                         st.markdown("### 🛠️ Manage Selected Item")
                         
                         # Dropdown to select which item to modify
                         selected_name = st.selectbox("Chagua bidhaa kurekebisha au kufuta", df_items["item_name"].tolist())
                         
                         # Fetch specific data for the selected item using its index
                         item_data = df_items[df_items["item_name"] == selected_name].iloc[0]
         
                         col_a, col_b = st.columns(2)
                         
                         # UPDATE SECTION
                         with col_a:
                             with st.expander(f"✏️ Update Prices for {selected_name}"):
                                 with st.form("up_form"):
                                     up_buy = st.number_input("New Buy Price", value=float(item_data['buying_price']), step=100.0)
                                     up_sell = st.number_input("New Sell Price", value=float(item_data['selling_price']), step=100.0)
                                     
                                     if st.form_submit_button("Hifadhi Marekebisho"):
                                         conn.table("inventory_items")\
                                             .update({"buying_price": up_buy, "selling_price": up_sell})\
                                             .eq("id", item_data['id'])\
                                             .execute()
                                         st.success("Marekebisho yamefanikiwa!")
                                         st.rerun()
                         
                         # DELETE SECTION
                         #with col_b:
                             #st.write("Danger Zone/Kuwa Makini Hapa")
                             #if st.button(f"🗑️ Delete {selected_name}"):
                                 # Direct delete based on unique ID
                                 #try:
                                     #conn.table("inventory_items").delete().eq("id", item_data['id']).execute()
                                     #st.success(f"{selected_name} imefutwa!")
                                     #st.rerun()
                                 #except Exception as e:
                                     #st.error(f"Futa imeshindikana: {e}")
                                     
                     else:
                         st.info("Bado hujaasajili bidhaa yoyote.")
                 except Exception as e:
                     st.error(f"Database Error: {e}")
             else:
                 st.warning("Tafadhali ingia (Login) kwanza.")

        # End view registerd
     

        # Start shopkeeper assignment
        elif menu_business_owner == "👥 Assign Shopkeepers.":
             st.subheader("🏢 Business & Shop Management")
         
             # LOGIC 1: Verify the Business exists for this owner
             biz_res = conn.table("businesses").select("id, business_name").eq("owner_id", st.session_state.user_id).execute()
         
             if not biz_res.data:
                 # If no business, they MUST create one first
                 st.warning("Hatua ya 1: Sajili Biashara yako kwanza.")
                 with st.form("create_biz"):
                     biz_name = st.text_input("Jina la Biashara (e.g. ASE Group)")
                     if st.form_submit_button("Sajili Biashara"):
                         try:
                             conn.table("businesses").insert({
                                 "owner_id": st.session_state.user_id,
                                 "business_name": biz_name
                             }).execute()
                             st.success("Biashara imesajiliwa!")
                             st.rerun()
                         except Exception as e:
                             st.error(f"Error: {e}")
             else:
                 # LOGIC 2: Business exists, now manage Shops and Assignments
                 business_id = biz_res.data[0]['id']
                 st.info(f"Biashara: **{biz_res.data[0]['business_name']}**")
         
                 # PART A: Create a Shop
                 with st.expander("➕ Ongeza Duka (Add Shop)"):
                     with st.form("create_shop"):
                         shop_name = st.text_input("Jina la Duka (e.g. Shop A)")
                         loc = st.text_input("Mahali")
                         if st.form_submit_button("Hifadhi Duka"):
                             try:
                                 conn.table("shops").insert({
                                     "business_id": business_id,
                                     "owner_id": st.session_state.user_id,
                                     "shop_name": shop_name,
                                     "location": loc
                                 }).execute()
                                 st.success("Duka limeundwa!")
                                 st.rerun()
                             except Exception as e:
                                 st.error(f"Error: {e}")
         
                 # PART B: Assign Shopkeeper (Only if shops exist)
                 st.divider()
                 shops_res = conn.table("shops").select("id, shop_name").eq("owner_id", st.session_state.user_id).execute()
                 
                 if shops_res.data:
                     st.subheader("Assign Shopkeeper")
                     shop_options = {s['shop_name']: s['id'] for s in shops_res.data}
                     
                     with st.form("assign_sk"):
                         sel_shop = st.selectbox("Chagua Duka", list(shop_options.keys()))
                         sk_email = st.text_input("Email ya Shopkeeper").lower().strip()
                         if st.form_submit_button("Panga Shopkeeper"):
                             try:
                                 conn.table("shop_assignments").insert({
                                     "shop_id": shop_options[sel_shop],
                                     "shopkeeper_email": sk_email
                                 }).execute()
                                 st.success(f"Umezipangia {sk_email} duka la {sel_shop}")
                             except Exception as e:
                                 st.error(f"Error: {e}")
                 else:
                     st.info("Ongeza duka kwanza ili upange wafanyakazi.")
         
        # End Assign shopkeeper 
        
        elif menu_business_owner == "Angalia duka":
            st.subheader("All Community Production Entries")
            try:
                prod_df = pd.read_csv("production_records.csv")
                st.dataframe(prod_df)
            except FileNotFoundError:
                st.warning("No production records found.")
            data = {
            'Village': ['Hydom', 'Dongobesh', 'Mbulu'],
            'Farmers': [5, 20, 15],
            'Acres': [10, 50, 30],
            'Yield (kg)': [500, 1750, 1000]
            }

            df = pd.DataFrame(data)
            #Displaying a pie chart for total yield
            st.subheader('Total Yield (kg)')
            #fig, ax = plt.subplots()
            #ax.pie(df['Yield (kg)'], labels=df['Village'], autopct='%1.1f%%')
            #st.pyplot(fig)
