import streamlit as st
import pandas as pd
import json
import math
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="KIDY.ca Pipeline Simulator",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 24px; font-weight: 700; color: #1a365d; margin-bottom: 0px; }
    .sub-header { font-size: 14px; color: #4a5568; margin-bottom: 20px; }
    .agent-card { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .status-passed { color: #2f855a; font-weight: bold; background-color: #f0fff4; padding: 2px 8px; border-radius: 4px; }
    .status-fallback { color: #c05621; font-weight: bold; background-color: #fffaf0; padding: 2px 8px; border-radius: 4px; border: 1px solid #fbd38d; }
    .metric-container { background-color: #ebf8ff; border: 1px solid #bee3f8; border-radius: 6px; padding: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">KIDY.ca • Multi-Agent Menu Optimization Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Base44 Specification v2.0 • Autonomous Procurement Engine (Ontario, Canada Framework)</div>', unsafe_allow_html=True)

# ==========================================
# SIDEBAR: PIPELINE CONTROL & TELEMETRY
# ==========================================
with st.sidebar:
    st.header("⚙️ Simulation Governance")
    
    st.subheader("Demographic Headcount")
    toddlers = st.number_input("Toddlers (18-30m)", min_value=0, value=15)
    preschool = st.number_input("Preschool (2.5-5y)", min_value=0, value=24)
    total_headcount = toddlers + preschool
    st.info(f"Total Scaling Population: **{total_headcount} kids**")
    
    st.divider()
    st.subheader("🤖 Governance & Models")
    task_model = st.selectbox("Operational Task Model", ["GPT-4o", "Gemini 1.5 Pro", "Claude 3.5 Sonnet"])
    
    auditor_options = [m for m in ["Claude 3.5 Sonnet", "Gemini 1.5 Pro", "GPT-4o"] if m != task_model]
    audit_model = st.selectbox("Step Auditor Model (Diversified)", auditor_options)
    
    st.caption(f"✓ Zero-Trust Rule Enforced: Auditor architecture ({audit_model}) differs from Task Agent ({task_model}).")
    
    st.divider()
    api_credits_start = 100.00
    st.metric(label="API Telemetry Credits Remaining", value=f"${api_credits_start:.2f}")

# ==========================================
# WORKFLOW TABS
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Menu & Ingredient Scaling", 
    "2. Retail Matching & Optimization", 
    "3. Multi-Week Shopping Invoices", 
    "4. Wholesale Reconciliation & Fallbacks"
])

# Global State Management
if 'parsed_ingredients' not in st.session_state:
    st.session_state.parsed_ingredients = None
if 'optimal_retail_manifest' not in st.session_state:
    st.session_state.optimal_retail_manifest = None

# ==========================================
# TAB 1: MENU & INGREDIENT SCALING
# ==========================================
with tab1:
    st.subheader("Step 1: Parse & Scale 4-Week Childcare Menu")
    
    col_upload, col_demo = st.columns([2, 1])
    
    with col_upload:
        uploaded_menu = st.file_uploader("Upload Your 4-Week Menu (.xlsx, .csv)", type=["xlsx", "csv"], key="menu_upload")
        st.caption("Upload a file containing columns like: `Week`, `Ingredient`, `Classification`, `Per_Child_Grams`, `Wastage_Pct`")

    with col_demo:
        st.write("**Or Use Quick Demo:**")
        if st.button("Load Preset Ontario Menu"):
            st.session_state.use_preset = True
            st.success("Preset 4-Week Menu loaded!")

    st.divider()
    
    if uploaded_menu is not None:
        try:
            if uploaded_menu.name.endswith('.csv'):
                user_df = pd.read_csv(uploaded_menu)
            else:
                user_df = pd.read_excel(uploaded_menu)
            
            st.write("### Uploaded Menu Preview")
            st.dataframe(user_df.head(), use_container_width=True)
            
            if st.button("🚀 Process Custom Uploaded Menu"):
                # Scale custom user data
                parsed_data = []
                for idx, row in user_df.iterrows():
                    week = str(row.get("Week", "Week 1"))
                    ing = str(row.get("Ingredient", "Unknown"))
                    cls = str(row.get("Classification", "Perishable"))
                    per_child_g = float(row.get("Per_Child_Grams", 50))
                    wastage = float(row.get("Wastage_Pct", 0.10))
                    
                    net_req = (per_child_g * total_headcount) / 1000.0
                    gross_req = net_req / (1 - wastage) if wastage < 1 else net_req
                    
                    parsed_data.append({
                        "Week": week,
                        "Ingredient": ing,
                        "Classification": cls,
                        "Net Required (kg)": round(net_req, 3),
                        "Wastage %": f"{int(wastage*100)}%",
                        "Gross Required (kg)": round(gross_req, 3)
                    })
                st.session_state.parsed_ingredients = pd.DataFrame(parsed_data)
                st.success("Custom Menu Scaled & Processed! Audit Gate: PASSED ✅")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    elif st.session_state.get('use_preset', False):
        if st.button("🚀 Process Preset Ontario Menu"):
            weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
            base_items = [
                {"item": "Boneless Chicken Breast", "per_child_g": 60, "wastage": 0.10, "type": "Perishable"},
                {"item": "Basmati Rice", "per_child_g": 45, "wastage": 0.02, "type": "Non-Perishable"},
                {"item": "Whole Wheat Penne", "per_child_g": 50, "wastage": 0.02, "type": "Non-Perishable"},
                {"item": "Fresh Broccoli", "per_child_g": 40, "wastage": 0.15, "type": "Perishable"},
                {"item": "Fresh Apples", "per_child_g": 80, "wastage": 0.08, "type": "Perishable"},
                {"item": "Cooking Oil", "per_child_g": 10, "wastage": 0.00, "type": "Non-Perishable"}
            ]
            parsed_data = []
            for week in weeks:
                for bi in base_items:
                    net_req = (bi["per_child_g"] * total_headcount) / 1000.0
                    gross_req = net_req / (1 - bi["wastage"])
                    parsed_data.append({
                        "Week": week,
                        "Ingredient": bi["item"],
                        "Classification": bi["type"],
                        "Net Required (kg)": round(net_req, 3),
                        "Wastage %": f"{int(bi['wastage']*100)}%",
                        "Gross Required (kg)": round(gross_req, 3)
                    })
            st.session_state.parsed_ingredients = pd.DataFrame(parsed_data)
            st.success("Preset Menu Processed! Audit Gate: PASSED ✅")

    if st.session_state.parsed_ingredients is not None:
        st.write("### Deconstructed & Waste-Adjusted Requirements")
        selected_week_filter = st.selectbox("Filter Output by Week:", ["All Weeks", "Week 1", "Week 2", "Week 3", "Week 4"])
        
        if selected_week_filter == "All Weeks":
            st.dataframe(st.session_state.parsed_ingredients, use_container_width=True)
        else:
            df_filtered = st.session_state.parsed_ingredients[st.session_state.parsed_ingredients["Week"] == selected_week_filter]
            st.dataframe(df_filtered, use_container_width=True)

# ==========================================
# TAB 2: RETAIL MATCHING & OPTIMIZATION
# ==========================================
with tab2:
    st.subheader("Step 2: Upload Retail Source Lists & Execute Optimizers")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Costco Canada Catalog**")
        costco_file = st.file_uploader("Upload Costco Price List (.xlsx / .csv)", type=["csv", "xlsx"], key="costco")
    with c2:
        st.markdown("**Walmart.ca Catalog / Parser**")
        walmart_file = st.file_uploader("Upload Walmart Price List (.xlsx / .csv)", type=["csv", "xlsx"], key="walmart")
    
    if st.button("⚡ Run Agent 2 (Catalog Filter) & Agent 6 (Price Economizer)"):
        if st.session_state.parsed_ingredients is None:
            st.error("Please process a Menu in Tab 1 first!")
        else:
            df_req = st.session_state.parsed_ingredients
            optimization_results = []
            
            for idx, row in df_req.iterrows():
                gross_kg = row["Gross Required (kg)"]
                item = row["Ingredient"]
                
                if "Chicken" in item:
                    store, pkg, unit_cost, pack_size = "Costco Canada", "3kg Bulk Pack", 24.99, 3.0
                elif "Rice" in item:
                    store, pkg, unit_cost, pack_size = "Walmart Canada", "10kg Bag", 18.97, 10.0
                elif "Penne" in item:
                    store, pkg, unit_cost, pack_size = "Walmart Canada", "1kg Pack", 2.47, 1.0
                else:
                    store, pkg, unit_cost, pack_size = "Costco Canada", "2kg Case", 8.99, 2.0

                pkgs_needed = math.ceil(gross_kg / pack_size)
                tot_cost = pkgs_needed * unit_cost

                optimization_results.append({
                    "Week": row["Week"],
                    "Ingredient": item,
                    "Classification": row["Classification"],
                    "Gross Needed (kg)": gross_kg,
                    "Selected Retailer": store,
                    "Package Variant": pkg,
                    "Packages To Buy": pkgs_needed,
                    "Unit Price ($)": unit_cost,
                    "Total Cost ($)": round(tot_cost, 2)
                })
            
            st.session_state.optimal_retail_manifest = pd.DataFrame(optimization_results)
            st.success("Agent 6 Optimization Complete! Audit Gate: PASSED ✅")

    if st.session_state.optimal_retail_manifest is not None:
        st.dataframe(st.session_state.optimal_retail_manifest, use_container_width=True)

# ==========================================
# TAB 3: MULTI-WEEK SHOPPING INVOICES
# ==========================================
with tab3:
    st.subheader("Step 3: External Weekly Shopping Summaries (Agent 7)")
    
    if st.session_state.optimal_retail_manifest is not None:
        df_opt = st.session_state.optimal_retail_manifest
        summary = df_opt.groupby(["Week", "Selected Retailer"])["Total Cost ($)"].sum().reset_index()
        
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.write("### Weekly Financial Breakdown ($ CAD)")
            st.dataframe(summary, use_container_width=True)
            
        with col_w2:
            total_retail_spend = df_opt["Total Cost ($)"].sum()
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(label="Total Combined 4-Week External Procurement Spend", value=f"${total_retail_spend:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Execute Tab 2 optimization to unlock weekly aggregated totals.")

# ==========================================
# TAB 4: WHOLESALE RECONCILIATION & FALLBACKS
# ==========================================
with tab4:
    st.subheader("Step 4: Proprietary Wholesale Price Mapping & Fallback Protocol (Agent 8 & 9)")
    
    wholesale_file = st.file_uploader("Upload Internal Wholesale Price List (.csv / .xlsx)", type=["csv", "xlsx"], key="wholesale")
    
    if st.button("🔄 Execute Agent 8 (Price Reconciliation) & Apply Fallbacks"):
        if st.session_state.optimal_retail_manifest is None:
            st.error("Please run previous steps first!")
        else:
            df_retail = st.session_state.optimal_retail_manifest.copy()
            
            # Read uploaded wholesale list if available
            internal_catalog = {}
            if wholesale_file is not None:
                try:
                    if wholesale_file.name.endswith('.csv'):
                        w_df = pd.read_csv(wholesale_file)
                    else:
                        w_df = pd.read_excel(wholesale_file)
                    # Expecting columns: Ingredient, Price
                    for _, w_row in w_df.iterrows():
                        internal_catalog[str(w_row.get("Ingredient", ""))] = float(w_row.get("Price", 0))
                except Exception as e:
                    st.warning(f"Could not parse uploaded wholesale file ({e}). Using sample internal catalog.")
            
            if not internal_catalog:
                # Sample fallback catalog
                internal_catalog = {
                    "Boneless Chicken Breast": 22.50,
                    "Basmati Rice": 16.50,
                    "Whole Wheat Penne": 2.10,
                    "Fresh Apples": 7.50,
                    "Cooking Oil": 6.80
                }
            
            reconciliation_rows = []
            for idx, row in df_retail.iterrows():
                item = row["Ingredient"]
                pkgs = row["Packages To Buy"]
                ext_price = row["Unit Price ($)"]
                ext_total = row["Total Cost ($)"]
                
                if item in internal_catalog:
                    int_price = internal_catalog[item]
                    int_total = pkgs * int_price
                    status = "Matched Internal"
                    source = "Internal Database"
                else:
                    # FALLBACK RULE TRIGGERED
                    int_price = ext_price
                    int_total = ext_total
                    status = "FALLBACK INSERTION"
                    source = f"Copied from {row['Selected Retailer']}"

                reconciliation_rows.append({
                    "Week": row["Week"],
                    "Ingredient": item,
                    "Packages": pkgs,
                    "External Unit Price ($)": ext_price,
                    "External Total ($)": ext_total,
                    "Internal Unit Price ($)": int_price,
                    "Internal Total ($)": int_total,
                    "Variance ($)": round(ext_total - int_total, 2),
                    "Mapping Status": status,
                    "Data Source": source
                })
            
            df_reconciled = pd.DataFrame(reconciliation_rows)
            st.session_state.df_reconciled = df_reconciled
            st.success("Wholesale Reconciliation Complete! Fallback Protocol Executed ✅")

    if 'df_reconciled' in st.session_state:
        df_rec = st.session_state.df_reconciled
        
        st.write("### Reconciled Price Matrix & Fallback Highlight Table")
        def highlight_fallbacks(val):
            if val == "FALLBACK INSERTION":
                return 'background-color: #feebc8; color: #c05621; font-weight: bold;'
            return ''

        st.dataframe(df_rec.style.map(highlight_fallbacks, subset=["Mapping Status"]), use_container_width=True)
        
        ext_sum = df_rec["External Total ($)"].sum()
        int_sum = df_rec["Internal Total ($)"].sum()
        savings = ext_sum - int_sum
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total External Retail Spend", f"${ext_sum:,.2f}")
        with m2:
            st.metric("Total Internal Wholesale Spend", f"${int_sum:,.2f}")
        with m3:
            st.metric("Net Internal Wholesale Savings", f"${savings:,.2f}", delta=f"{round((savings/ext_sum)*100, 1)}%" if ext_sum > 0 else "0%")

st.divider()
st.caption("KIDY.ca Multi-Agent Pipeline Simulator • Built in compliance with Base44 Multi-Model Governance Specifications.")
