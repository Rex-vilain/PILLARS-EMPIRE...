import streamlit as st
import pandas as pd
import os
from datetime import date
from io import BytesIO

#Constants
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ITEMS = [
    "TUSKER", "PILISNER", "TUSKER MALT", "TUSKER LITE", "GUINESS KUBWA",
    "GUINESS SMALL", "BALOZICAN", "WHITE CAP", "BALOZI", "SMIRNOFF ICE",
    "SAVANNAH", "SNAPP", "TUSKER CIDER", "KINGFISHER", "ALLSOPPS",
    "G.K CAN", "T.LITE CAN", "GUARANA", "REDBULL", "RICHOT ½",
    "RICHOT ¼", "VICEROY ½", "VICEROY ¼", "VODKA½", "VODKA¼",
    "KENYACANE ¾", "KENYACANE ½", "KENYACANE ¼", "GILBEYS ½", "GILBEYS ¼",
    "V&A 750ml", "CHROME", "TRIPLE ACE", "BLACK AND WHITE", "KIBAO½",
    "KIBAO¼", "HUNTERS ½", "HUNTERS ¼", "CAPTAIN MORGAN", "KONYAGI",
    "V&A", "COUNTY", "BEST 750ml", "WATER 1L", "WATER½",
    "LEMONADE", "CAPRICE", "FAXE", "C.MORGAN", "VAT 69",
    "SODA300ML", "SODA500ML", "BLACK AND WHITE", "BEST", "CHROME 750ml",
    "MANGO", "TRUST", "PUNCH", "VODKA 750ml", "KONYAGI 500ml",
    "GILBEYS 750ml"
]

#Helper functions to load and save CSVs
def get_filepath(date_str, section):
    return os.path.join(DATA_DIR, f"{section}_{date_str}.csv")

def load_section_df(date_str, section, default_df):
    path = get_filepath(date_str, section)
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return default_df
    else:
        return default_df

def save_section_df(date_str, section, df):
    path = get_filepath(date_str, section)
    df.to_csv(path, index=False)

def load_money_val(date_str, key):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return float(f.read())
            except ValueError:
                return 0.0
    return 0.0

def save_money_val(date_str, key, val):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    with open(path, "w") as f:
        f.write(str(val))

def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

#Streamlit setup
st.set_page_config(page_title="PILLARS EMPIRE", layout="wide")
st.title("PILLARS EMPIRE - Bar & Accommodation Management")

#Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose Mode", ["Data Entry", "View Past Reports"])

if app_mode == "Data Entry":
    record_date = st.date_input("Select Date", value=date.today())
    date_str = record_date.strftime("%Y-%m-%d")

    # --- STOCK MANAGEMENT ---
    st.header("Stock Management")
    default_stock_df = pd.DataFrame({
        "Item": ITEMS,
        "Opening Stock": [0]*len(ITEMS),
        "Purchases": [0]*len(ITEMS),
        "Closing Stock": [0]*len(ITEMS),
        "Selling Price": [0.0]*len(ITEMS)
    })
    stock_df = load_section_df(date_str, "stock", default_stock_df)

    edited_stock_df = st.data_editor(
        stock_df,
        num_rows="dynamic",
        use_container_width=True,
        key="stock_editor"
    )

    edited_stock_df["Sales"] = (
        edited_stock_df["Opening Stock"] + edited_stock_df["Purchases"] - edited_stock_df["Closing Stock"]
    )
    edited_stock_df["Amount"] = (
        edited_stock_df["Sales"] * edited_stock_df["Selling Price"]
    )
    st.dataframe(edited_stock_df)

    if st.button("Save Stock Data"):
        save_section_df(date_str, "stock", edited_stock_df.drop(columns=["Sales", "Amount"]))
        st.success("Stock data saved!")

    # --- ACCOMMODATION DATA ---
    st.header("Accommodation Data")
    default_accom_df = pd.DataFrame({
        "Room Number": ["" for _ in range(10)],
        "1st Floor Rooms": ["" for _ in range(10)],
        "Ground Floor Rooms": ["" for _ in range(10)],
        "Money Lendered": [0.0 for _ in range(10)],
        "Payment Method": ["" for _ in range(10)],
    })
    accom_df = load_section_df(date_str, "accommodation", default_accom_df)

    edited_accom_df = st.data_editor(accom_df, num_rows="dynamic", use_container_width=True)

    total_first_floor = edited_accom_df["1st Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
    total_ground_floor = edited_accom_df["Ground Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
    total_lendered = edited_accom_df["Money Lendered"].sum()

    st.markdown(f"Total 1st Floor Rooms Used: {total_first_floor}")
    st.markdown(f"Total Ground Floor Rooms Used: {total_ground_floor}")
    st.markdown(f"Total Money Lendered: KES {total_lendered:,.2f}")

    if st.button("Save Accommodation Data"):
        save_section_df(date_str, "accommodation", edited_accom_df)
        st.success("Accommodation data saved!")

    # --- EXPENSES ---
    st.header("Expenses")
    default_expenses_df = pd.DataFrame({
        "Description": ["" for _ in range(10)],
        "Amount": [0.0 for _ in range(10)],
    })
    expenses_df = load_section_df(date_str, "expenses", default_expenses_df)

    edited_expenses_df = st.data_editor(expenses_df, num_rows="dynamic", use_container_width=True)
    total_expenses = edited_expenses_df["Amount"].sum()
    st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")

    if st.button("Save Expenses Data"):
        save_section_df(date_str, "expenses", edited_expenses_df)
        st.success("Expenses data saved!")

    # --- MONEY TRANSACTIONS ---
    st.header("Money Transactions")

    money_paid = load_money_val(date_str, "money_paid")
    money_invested = load_money_val(date_str, "money_invested")

    money_paid_input = st.number_input("Money Paid to Boss", min_value=0.0, value=money_paid, step=1.0)
    money_invested_input = st.number_input("Money Invested (e.g., from Chama)", min_value=0.0, value=money_invested, step=1.0)

    if st.button("Save Money Transactions"):
        save_money_val(date_str, "money_paid", money_paid_input)
        save_money_val(date_str, "money_invested", money_invested_input)
        st.success("Money transactions saved!")

    # --- SUMMARY ---
    st.header("Summary")
    total_sales_amount = edited_stock_df["Amount"].sum()
    profit = total_sales_amount - total_expenses - money_paid_input

    st.markdown(f"Total Sales Amount: KES {total_sales_amount:,.2f}")
    st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")
    st.markdown(f"Money Paid to Boss: KES {money_paid_input:,.2f}")
    st.markdown(f"Money Invested: KES {money_invested_input:,.2f}")
    st.markdown(f"Profit: KES {profit:,.2f}")

elif app_mode == "View Past Reports":
    st.header("View Past Reports")

    # List all dates with saved data (looking at stock files)
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("stock_") and f.endswith(".csv")]
    saved_dates = sorted([f[6:-4] for f in files], reverse=True)

    if saved_dates:
        selected_date = st.selectbox("Select date to view report", saved_dates)
        if selected_date:
            stock = load_section_df(selected_date, "stock", pd.DataFrame())
            accom = load_section_df(selected_date, "accommodation", pd.DataFrame())
            expenses = load_section_df(selected_date, "expenses", pd.DataFrame())
            money_paid = load_money_val(selected_date, "money_paid")
            money_invested = load_money_val(selected_date, "money_invested")

            st.subheader("Stock Sheet")
            if not stock.empty:
                st.dataframe(stock)
            else:
                st.info("No stock data available for this date.")

            st.subheader("Accommodation Data")
            if not accom.empty:
                st.dataframe(accom)
            else:
                st.info("No accommodation data available for this date.")

            st.subheader("Expenses")
            if not expenses.empty:
                st.dataframe(expenses)
            else:
                st.info("No expenses data available for this date.")

            st.subheader("Money Transactions")
            st.markdown(f"Money Paid to Boss: KES {money_paid:,.2f}")
            st.markdown(f"Money Invested: KES {money_invested:,.2f}")

            # Export to Excel button
            if st.button("Download Full Report as Excel"):
                dfs = {
                    "Stock": stock,
                    "Accommodation": accom,
                    "Expenses": expenses,
                    "Money Transactions": pd.DataFrame({
                        "Money Paid to Boss": [money_paid],
                        "Money Invested": [money_invested]
                    })
                }
                excel_data = to_excel(dfs)
                st.download_button(
        label="Download Excel",
                    data=excel_data,
                    file_name=f"Pillars_Empire_Report_{selected_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.warning("No saved reports found.")
