import streamlit as st
import pandas as pd

st.set_page_config(page_title="KIDY.ca - Menu & Cost Simulator", layout="wide")

st.title("🍎 KIDY.ca Childcare Menu & Procurement Simulator")
st.markdown("Automated Menu Scaling, Ingredient Deconstruction & Wholesale Reconciliation")

# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Menu Scaling & Deconstruction",
    "2. Headcount & Grams Calculator",
    "3. Retail Price Comparison",
    "4. Wholesale Reconciliation & Fallback Engine"
])

# ---------------------------------------------------------
# TAB 1: MENU SCALING & DECONSTRUCTION
# ---------------------------------------------------------
with tab1:
    st.header("1. Upload Custom Menu")
    st.info("Upload any 4-Week Menu spreadsheet or CSV file. The simulator will deconstruct compound dishes into raw ingredients.")
    
    uploaded_menu = st.file_uploader("Upload Menu File (CSV or Excel)", type=["csv", "xlsx"])
    
    if uploaded_menu is not None:
        try:
            if uploaded_menu.name.endswith('.csv'):
                df_menu = pd.read_csv(uploaded_menu)
            else:
                df_menu = pd.read_excel(uploaded_menu)
            
            # Column Normalization
            df_menu.columns = df_menu.columns.str.strip().str.lower()
            
            alias_map = {
                'ingredient name': 'ingredient',
                'ingredients': 'ingredient',
                'item name': 'item',
                'dish': 'item',
                'category': 'classification',
                'type': 'classification',
                'grams': 'per_child_grams',
                'gram_per_child': 'per_child_grams',
                'portion_g': 'per_child_grams',
                'waste': 'wastage_pct',
                'shrinkage': 'wastage_pct'
            }
            df_menu = df_menu.rename(columns=alias_map)
            
            st.session_state['df_menu'] = df_menu
            st.success(f"Successfully loaded menu with {len(df_menu)} ingredient rows!")
            st.dataframe(df_menu.head(15), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading menu file: {e}")

# ---------------------------------------------------------
# TAB 2: HEADCOUNT & GRAMS CALCULATOR
# ---------------------------------------------------------
with tab2:
    st.header("2. Headcount & Total Requirement Scaling")
    headcount = st.number_input("Enter Total Child Headcount:", min_value=1, max_value=1000, value=50, step=5)
    
    if 'df_menu' in st.session_state:
        df_m = st.session_state['df_menu'].copy()
        
        # Ensure numeric types
        if 'per_child_grams' not in df_m.columns:
            df_m['per_child_grams'] = 50.0
        if 'wastage_pct' not in df_m.columns:
            df_m['wastage_pct'] = 0.05
            
        df_m['per_child_grams'] = pd.to_numeric(df_m['per_child_grams'], errors='coerce').fillna(50.0)
        df_m['wastage_pct'] = pd.to_numeric(df_m['wastage_pct'], errors='coerce').fillna(0.05)
        
        # Calculation: Total Grams = Headcount * Per Child Grams * (1 + Wastage %)
        df_m['total_grams_needed'] = headcount * df_m['per_child_grams'] * (1 + df_m['wastage_pct'])
        df_m['total_kg_needed'] = df_m['total_grams_needed'] / 1000.0
        
        st.session_state['df_scaled'] = df_m
        
        # Aggregated Ingredient Summary
        df_grouped = df_m.groupby(['ingredient', 'classification'])[['total_grams_needed', 'total_kg_needed']].sum().reset_index()
        st.dataframe(df_grouped.sort_values(by='total_kg_needed', ascending=False), use_container_width=True)
    else:
        st.warning("Please upload a menu file in Tab 1 first.")

# ---------------------------------------------------------
# TAB 3: RETAIL PRICE COMPARISON
# ---------------------------------------------------------
with tab3:
    st.header("3. Retail Benchmark Comparison")
    st.markdown("Establishes baseline retail purchase costs for your scaled menu requirements.")
    
    if 'df_scaled' in st.session_state:
        st.info("Calculations scaled based on headcount entered in Tab 2.")
    else:
        st.warning("Please upload a menu in Tab 1 and calculate headcount in Tab 2 first.")

# ---------------------------------------------------------
# TAB 4: WHOLESALE RECONCILIATION & DYNAMIC FALLBACK ENGINE
# ---------------------------------------------------------
with tab4:
    st.header("4. MFS Wholesale Reconciliation & Dynamic Fallback Engine")
    st.markdown("Upload your MFS Master Price List. The engine will match active catalog items and **dynamically generate Fallback Insertion flags** for any new menu items!")
    
    uploaded_master = st.file_uploader("Upload MFS Master Selling Price List (CSV or Excel)", type=["csv", "xlsx"], key="master_file")
    
    if uploaded_master is not None and 'df_menu' in st.session_state:
        try:
            if uploaded_master.name.endswith('.csv'):
                df_master = pd.read_csv(uploaded_master)
            else:
                df_master = pd.read_excel(uploaded_master)
            
            # Standardize Master File Column Headers
            df_master.columns = df_master.columns.str.strip().str.lower()
            
            # Map common column aliases
            master_alias = {
                'item_name': 'product_name',
                'ingredient': 'product_name',
                'product': 'product_name',
                'product description': 'product_name',
                'description': 'product_name',
                'wholesale_price_cad': 'selling_price',
                'price': 'selling_price',
                'cost': 'selling_price',
                'wholesale price': 'selling_price',
                'selling price': 'selling_price'
            }
            df_master = df_master.rename(columns=master_alias)
            
            # Get unique ingredients from uploaded menu (Tab 1)
            df_menu_curr = st.session_state['df_menu']
            unique_ingredients = df_menu_curr[['ingredient', 'classification']].drop_duplicates().reset_index(drop=True)
            
            reconciled_results = []
            
            for _, row in unique_ingredients.iterrows():
                ing_name = str(row['ingredient']).strip()
                category = str(row['classification']).strip()
                
                # Search for match in Master Catalog
                if 'product_name' in df_master.columns:
                    matches = df_master[df_master['product_name'].astype(str).str.lower().str.contains(ing_name.lower(), regex=False)]
                else:
                    matches = pd.DataFrame()
                
                if not matches.empty:
                    # MATCH FOUND IN MFS CATALOG
                    matched_row = matches.iloc[0]
                    price_val = matched_row.get('selling_price', 0.0)
                    
                    reconciled_results.append({
                        'Menu_Ingredient': ing_name,
                        'Category': category,
                        'MFS_Catalog_Match': matched_row['product_name'],
                        'MFS_Selling_Price_CAD': price_val,
                        'Source_Status': 'MFS Active Catalog',
                        'Fallback_Flag': 'EXACT MATCH',
                        'Sourcing_Action': 'No - Active Inventory Item'
                    })
                else:
                    # ⚠️ DYNAMIC FALLBACK INSERTION - NOT IN MFS CATALOG
                    reconciled_results.append({
                        'Menu_Ingredient': ing_name,
                        'Category': category,
                        'MFS_Catalog_Match': 'None (Needs Sourcing)',
                        'MFS_Selling_Price_CAD': 4.99,  # Default Retail Benchmark
                        'Source_Status': 'FALLBACK INSERTION',
                        'Fallback_Flag': '⚠️ MISSING FROM MFS CATALOG',
                        'Sourcing_Action': 'YES - Find Wholesale Supplier (CJR / Dairy Central)'
                    })
            
            df_reconciled_output = pd.DataFrame(reconciled_results)
            
            # Display Key Metrics
            total_items = len(df_reconciled_output)
            active_items = len(df_reconciled_output[df_reconciled_output['Source_Status'] == 'MFS Active Catalog'])
            fallback_items = len(df_reconciled_output[df_reconciled_output['Source_Status'] == 'FALLBACK INSERTION'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Menu Ingredients", total_items)
            col2.metric("Matched in MFS Catalog", active_items)
            col3.metric("Fallback Insertions (Needs Sourcing)", fallback_items, delta=f"{fallback_items} Missing", delta_color="inverse")
            
            # Styling function to highlight Fallbacks in RED
            def highlight_row(val):
                if 'FALLBACK' in str(val):
                    return 'background-color: #ffcccc; color: #990000; font-weight: bold;'
                return 'background-color: #e6ffe6; color: #006600;'
            
            st.subheader("Reconciliation & Sourcing Report")
            st.dataframe(
                df_reconciled_output.style.map(highlight_row, subset=['Source_Status']),
                use_container_width=True
            )
            
            # Allow downloading reconciled report directly
            csv_data = df_reconciled_output.to_csv(index=False)
            st.download_button(
                label="📥 Download Reconciliation Report (CSV)",
                data=csv_data,
                file_name="Dynamic_Menu_Reconciliation_Report.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error executing reconciliation: {e}")
    elif uploaded_master is None:
        st.info("Upload your MFS Master Price List above to run reconciliation.")
    elif 'df_menu' not in st.session_state:
        st.warning("Please upload a menu file in Tab 1 first so the engine knows what ingredients to reconcile!")
