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

# Custom CSS for executive presentation
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
    
    # Model diversification rule enforcement
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
    st.subheader("Step 1: Parse 4-Week Childcare Menu")
    
    col_input, col_preset = st.columns([2, 1])
    with col_preset:
        st.write("**Quick Demo Action:**")
        if st.button("Load Sample 4-Week Ontario Menu"):
            # Mocking 4 weeks of menus
            sample_menu = {
                "Week 1": ["Butter Chicken & Basmati Rice", "Steamed Broccoli", "Apple Slices"],
                "Week 2": ["Bolognese Pasta & Whole Wheat Penne", "Carrot Sticks", "Banana Slices"],
                "Week 3": ["Mild Beef Curry & Basmati Rice", "Steamed Peas & Corn", "Orange Slices"],
                "Week 4": ["Chicken Penne Alfredo", "Green Beans", "Pear Slices"]
            }
            st.session_state.sample_menu_loaded = sample_menu
            st.success("Sample 4-Week Menu Loaded successfully!")

    if 'sample_menu_loaded' in st.session_state:
        st.json(st.session_state.sample_menu_loaded)
        
        if st.button("🚀 Execute Agents 1 to 5 (Deconstruct & Scale)"):
            with st.spinner("Agent 1 (Deconstructor) & Agent 3 (Scaler) executing..."):
                # Mocking processing results across 4 weeks
                parsed_data = []
                
                # Mock base data calculation for week execution
                weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
                base_items = [
                    {"item": "Boneless Chicken Breast", "per_child_g": 60, "wastage": 0.10, "type": "Perishable"},
                    {"item": "Basmati Rice", "per_child_g": 45, "wastage": 0.02, "type": "Non-Perishable"},
                    {"item": "Whole Wheat Penne", "per_child_g": 50, "wastage": 0.02, "type": "Non-Perishable"},
                    {"item": "Fresh Broccoli", "per_child_g": 40, "wastage": 0.15, "type": "Perishable"},
                    {"item": "Fresh Apples", "per_child_g": 80, "wastage": 0.08, "type": "Perishable"},
                    {"item": "Cooking Oil", "per_child_g": 10, "wastage": 0.00, "type": "Non-Perishable"}
                ]
                
                for week in weeks:
                    for bi in base_items:
                        net_req = (bi["per_child_g"] * total_headcount) / 1000.0 # to kg
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
                
            st.success("Agents 1-5 Pipeline Completed! Audit Gate: PASSED ✅")

    if st.session_state.parsed_ingredients is not None:
        st.divider()
        st.write("### Deconstructed & Waste-Adjusted Requirements (All 4 Weeks)")
        
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
        st.markdown("**Walmart.ca Scraper Integrator**")
        walmart_mode = st.radio("Walmart Data Stream Mode", ["Simulate Live Walmart.ca Parser", "Upload Static Catalog"])
    
    if st.button("⚡ Run Agent 2 (Catalog Filter) & Agent 6 (Price Economizer)"):
        if st.session_state.parsed_ingredients is None:
            st.error("Please run Menu Deconstruction in Tab 1 first!")
        else:
            with st.spinner("Scraping walmart.ca & matching Costco package variants..."):
                # Mocking optimal product resolution logic
                df_req = st.session_state.parsed_ingredients
                
                # Mock resolution catalog
                optimization_results = []
                for idx, row in df_req.iterrows():
                    gross_kg = row["Gross Required (kg)"]
                    
                    if "Chicken" in row["Ingredient"]:
                        store = "Costco Canada"
                        pkg = "3kg Bulk Pack"
                        unit_cost = 24.99
                        pkgs_needed = math.ceil(gross_kg / 3.0)
                        tot_cost = pkgs_needed * unit_cost
                    elif "Rice" in row["Ingredient"]:
                        store = "Walmart Canada"
                        pkg = "10kg Bag"
                        unit_cost = 18.97
                        pkgs_needed = math.ceil(gross_kg / 10.0)
                        tot_cost = pkgs_needed * unit_cost
                    elif "Penne" in row["Ingredient"]:
                        store = "Walmart Canada"
                        pkg = "1kg Pack"
                        unit_cost = 2.47
                        pkgs_needed = math.ceil(gross_kg / 1.0)
                        tot_cost = pkgs_needed * unit_cost
                    else:
                        store = "Costco Canada"
                        pkg = "2kg Case"
                        unit_cost = 8.99
                        pkgs_needed = math.ceil(gross_kg / 2.0)
                        tot_cost = pkgs_needed * unit_cost

                    optimization_results.append({
                        "Week": row["Week"],
                        "Ingredient": row["Ingredient"],
                        "Classification": row["Classification"],
                        "Gross Needed (kg)": gross_kg,
                        "Selected Retailer": store,
                        "Package Variant": pkg,
                        "Packages To Buy": pkgs_needed,
                        "Unit Price ($)": unit_cost,
                        "Total Cost ($)": round(tot_cost, 2)
                    })
                
                st.session_state.optimal_retail_manifest = pd.DataFrame(optimization_results)
                st.success("Agent 6 Package Size Optimization Complete! Audit Gate: PASSED ✅")

    if st.session_state.optimal_retail_manifest is not None:
        st.dataframe(st.session_state.optimal_retail_manifest, use_container_width=True)

# ==========================================
# TAB 3: MULTI-WEEK SHOPPING INVOICES
# ==========================================
with tab3:
    st.subheader("Step 3: External Weekly Shopping Summaries (Agent 7)")
    
    if st.session_state.optimal_retail_manifest is not None:
        df_opt = st.session_state.optimal_retail_manifest
        
        # Group by Week and Retailer
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
    
    st.write("Upload your internal commercial wholesale price catalog to compare against external retail selections.")
    wholesale_file = st.file_uploader("Upload Internal Wholesale Price List (.csv / .xlsx)", type=["csv", "xlsx"], key="wholesale")
    
    if st.button("🔄 Execute Agent 8 (Price Reconciliation) & Apply Fallbacks"):
        if st.session_state.optimal_retail_manifest is None:
            st.error("Please run the previous pipeline steps first!")
        else:
            with st.spinner("Mapping external items against internal catalog & evaluating fallbacks..."):
                df_retail = st.session_state.optimal_retail_manifest.copy()
                
                # Mocking internal database lookup:
                # Let's intentionally omit "Fresh Broccoli" to trigger the Agent 8 Fallback Rule
                internal_catalog = {
                    "Boneless Chicken Breast": 22.50, # Wholesale price
                    "Basmati Rice": 16.50,
                    "Whole Wheat Penne": 2.10,
                    "Fresh Apples": 7.50,
                    "Cooking Oil": 6.80
                    # Fresh Broccoli is missing!
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
                st.success("Wholesale Reconciliation Complete! Fallback Protocol Executed successfully ✅")

    if 'df_reconciled' in st.session_state:
        df_rec = st.session_state.df_reconciled
        
        # Highlight fallbacks
        st.write("### Reconciled Price Matrix & Fallback Highlight Table")
        
        # Displaying with color coding for fallbacks
        def highlight_fallbacks(val):
            if val == "FALLBACK INSERTION":
                return 'background-color: #feebc8; color: #c05621; font-weight: bold;'
            return ''

        st.dataframe(df_rec.style.map(highlight_fallbacks, subset=["Mapping Status"]), use_container_width=True)
        
        # Summary variance calculation
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
            st.metric("Net Internal Wholesale Savings", f"${savings:,.2f}", delta=f"{round((savings/ext_sum)*100, 1)}%")

# Footer
st.divider()
st.caption("KIDY.ca Multi-Agent Pipeline Simulator • Built in compliance with Base44 Multi-Model Governance Specifications.")
