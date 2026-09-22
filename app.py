import io
import pandas as pd
import streamlit as st
from supabase import create_client

# ==========================================
# 1. إعدادات الاتصال بقاعدة البيانات السحابية (Supabase)
# ==========================================
SUPABASE_URL = "https://xoiwmchqsluhgygkfsvm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvaXdtY2hxc2x1aGd5Z2tmc3ZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3Mjc1MDcsImV4cCI6MjEwMDMwMzUwN30.0Mi_UYLL1EImmqsAM2ZRycNOYbcXjIg73TIHDJHOmuI"


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()


def clean_text(text):
    if pd.isna(text) or text is None:
        return ""
    text_str = str(text).strip().lower()
    if text_str.endswith(".0"):
        text_str = text_str[:-2]
    return " ".join(text_str.split())


def clean_code(code_val):
    if pd.isna(code_val) or code_val is None:
        return ""
    c_str = str(code_val).strip()
    if c_str.endswith(".0"):
        c_str = c_str[:-2]
    return c_str


def get_riders():
    try:
        res = supabase.table("riders").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


def get_payments():
    try:
        res = supabase.table("payments").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


def get_deleted_payments():
    try:
        res = supabase.table("deleted_payments").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


def auto_register_rider(code, name, phone=""):
    if not name or str(name).strip() == "":
        return
    
    clean_c = clean_code(code)
    clean_n = clean_text(name)
    clean_p = clean_code(phone)

    existing_riders = get_riders()
    
    found_rider = None
    for r in existing_riders:
        r_c = clean_code(r.get("code"))
        r_n = clean_text(r.get("name"))
        
        # البحث بالأولوية للكود أولاً ثم الاسم
        if clean_c and r_c == clean_c:
            found_rider = r
            break
        elif not clean_c and clean_n and r_n == clean_n:
            found_rider = r
            break

    if not found_rider:
        try:
            supabase.table("riders").insert(
                {"code": clean_c, "name": str(name).strip(), "phone": clean_p}
            ).execute()
        except Exception:
            pass
    else:
        # تحديث الكود أو الموبايل إن وُجِدا ولم يكونا مسجلين سابقاً
        existing_code = clean_code(found_rider.get("code"))
        existing_phone = clean_code(found_rider.get("phone"))
        
        updates = {}
        if not existing_code and clean_c:
            updates["code"] = clean_c
        if (not existing_phone or existing_phone == "0") and clean_p and clean_p != "0":
            updates["phone"] = clean_p
            
        if updates:
            try:
                supabase.table("riders").update(updates).eq("id", found_rider.get("id")).execute()
            except Exception:
                pass


def save_dashboard_data(df_dash, id_col, name_col, cod_col, status_col, vendor_col):
    try:
        supabase.table("dashboard_data").delete().neq("id", 0).execute()
        records = []
        for _, r in df_dash.iterrows():
            records.append({
                "rider_code": clean_code(r[id_col]),
                "rider_name": str(r[name_col]).strip() if pd.notna(r[name_col]) else "",
                "amount": float(r[cod_col]) if pd.notna(r[cod_col]) else 0.0,
                "status": str(r[status_col]).strip() if status_col and pd.notna(r[status_col]) else "",
            })
        if records:
            supabase.table("dashboard_data").insert(records).execute()
    except Exception:
        pass


def delete_dashboard_data():
    try:
        supabase.table("dashboard_data").delete().neq("id", 0).execute()
        return True
    except Exception:
        return False


def get_dashboard_data():
    try:
        res = supabase.table("dashboard_data").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


def save_salaries_data(df_sal_grouped):
    try:
        supabase.table("salaries_data").delete().neq("id", 0).execute()
        records = []
        for _, r in df_sal_grouped.iterrows():
            rec = {
                "rider_code": clean_code(r["Code_Clean"]),
                "rider_name": str(r["Name_Clean"]).strip(),
                "amount": float(r["Salary_Clean"]),
            }
            if "Month_Year" in r:
                rec["month_year"] = str(r["Month_Year"])
            records.append(rec)
        if records:
            supabase.table("salaries_data").insert(records).execute()
    except Exception:
        pass


def delete_salaries_data():
    try:
        supabase.table("salaries_data").delete().neq("id", 0).execute()
        return True
    except Exception:
        return False


def get_salaries_data():
    try:
        res = supabase.table("salaries_data").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


# ==========================================
# 2. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="نظام إدارة الداشبورد والتوريدات",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    /* إخفاء القوائم والأيقونات السفلية والعلوية تماماً */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    
    [data-testid="stStatusWidget"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    div[class*="stAppViewer"] > footer {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    
    /* إخفاء الأيقونات العائمة بالأسفل اليمين/اليسار */
    div[class*="viewerBadge"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    button[title="View source"] {display: none !important;}
    .stApp > footer {display: none !important;}
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-bottom: 0px;}
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 25px 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: center !important;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    
    .main-header h1 {
        margin: 0 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-align: center !important;
    }
    
    .main-header p {
        margin: 8px 0 0 0 !important;
        font-size: 15px !important;
        opacity: 0.92;
        text-align: center !important;
    }

    .section-title {
        text-align: center !important;
        color: #1e293b;
        font-weight: 700;
        font-size: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        border-radius: 12px;
        padding: 16px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        justify-content: center !important;
    }
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 15px;
        padding: 10px 24px;
        width: 100%;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. القائمة الجانبية
# ==========================================
st.sidebar.markdown(
    "<h2 style='text-align: center; margin-bottom: 20px;'>⚡ لوحة التحكم</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "الانتقال إلى الشاشة:",
    [
        "📊 مطابقة الداشبورد اليومية",
        "➕ إضافة / تسجيل توريد يومي",
        "👥 إدارة أسماء المناديب",
        "📜 سجل التوريدات الشهرية",
        "💰 تجميع مرتبات المناديب",
    ],
)

# ==========================================
# الشاشة الأولى: مطابقة الداشبورد
# ==========================================
if menu == "📊 مطابقة الداشبورد اليومية":
    st.markdown(
        """
    <div class="main-header">
        <h1>📊 مطابقة عهدة الداشبورد مع التوريدات السحابية</h1>
        <p>متابعة مديونيات المناديب والصافي المستحق بلحظة بلحظة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_up1, col_up2 = st.columns([3, 1])

    with col_up1:
        dash_file = st.file_uploader(
            "📥 ارفع ملف الداشبورد الجديد (CSV أو Excel)", type=["csv", "xlsx", "xls"]
        )

    with col_up2:
        st.write("🗑️ مسح الداشبورد الحالي:")
        if st.button("🔥 مسح الشيت المحفوظ"):
            if delete_dashboard_data():
                st.success("✅ تم مسح شيت الداشبورد!")
                st.rerun()

    with st.spinner("⏳ 👨🏻‍🦯🏃🏻 جاري تحميل البيانات أستنو شوية  ..."):
        df_dash_raw = None
        if dash_file:
            try:
                df_dash_raw = (
                    pd.read_csv(dash_file)
                    if dash_file.name.endswith(".csv")
                    else pd.read_excel(dash_file)
                )
                dash_cols = df_dash_raw.columns.tolist()

                id_col = next(
                    (c for c in dash_cols if "id" in str(c).lower() or "كود" in str(c).lower()),
                    dash_cols[0],
                )
                name_col_dash = next(
                    (c for c in dash_cols if "name" in str(c).lower() or "اسم" in str(c).lower()),
                    dash_cols[1] if len(dash_cols) > 1 else dash_cols[0],
                )
                cod_col = next(
                    (c for c in dash_cols if any(k in str(c).lower() for k in ["cod", "balance", "عهدة", "عجز", "مستحق", "amount"])),
                    dash_cols[-1],
                )
                status_col = next(
                    (c for c in dash_cols if "status" in str(c).lower() or "حالة" in str(c).lower()),
                    None,
                )
                vendor_col = next(
                    (c for c in dash_cols if "vendor" in str(c).lower() or "شركة" in str(c).lower()),
                    None,
                )

                save_dashboard_data(df_dash_raw, id_col, name_col_dash, cod_col, status_col, vendor_col)
                st.success("✅ تم استبدال وحفظ الداشبورد السحابي بنجاح!")
            except Exception as e:
                st.error(f"خطأ في قراءة الملف: {e}")
        else:
            saved_dash = get_dashboard_data()
            if saved_dash:
                df_dash_raw = pd.DataFrame(saved_dash)
                id_col = "rider_code"
                name_col_dash = "rider_name"
                cod_col = "amount"
                status_col = "status"
                vendor_col = None

        if df_dash_raw is not None and not df_dash_raw.empty:
            try:
                df_dash = df_dash_raw.dropna(subset=[name_col_dash]).copy()
                df_dash["Name_Clean"] = df_dash[name_col_dash].apply(clean_text)
                df_dash["Code_Clean"] = df_dash[id_col].apply(clean_code)
                df_dash["COD_Balance"] = pd.to_numeric(
                    df_dash[cod_col], errors="coerce"
                ).fillna(0)

                for _, r_item in df_dash.iterrows():
                    auto_register_rider(r_item[id_col], r_item[name_col_dash])

                # 1) جلب التوريدات المسجلة
                payments_list = get_payments()
                if payments_list:
                    df_pay_db = pd.DataFrame(payments_list)
                    df_pay_db["Name_Clean"] = df_pay_db["rider_name"].apply(clean_text)
                    df_pay_db["Code_Clean"] = df_pay_db.get("rider_code", pd.Series([""]*len(df_pay_db))).apply(clean_code)
                    
                    # تجميع المبالغ بواسطة الاسم والكود معاً لمنع تكرار الأسماء المتشابهة
                    pay_sum_name = df_pay_db.groupby("Name_Clean")["amount"].sum().to_dict()
                    pay_sum_code = df_pay_db[df_pay_db["Code_Clean"] != ""].groupby("Code_Clean")["amount"].sum().to_dict()

                    def calculate_paid(row):
                        c = row["Code_Clean"]
                        n = row["Name_Clean"]
                        if c in pay_sum_code:
                            return pay_sum_code[c]
                        return pay_sum_name.get(n, 0.0)

                    df_dash["Total_Paid"] = df_dash.apply(calculate_paid, axis=1)
                else:
                    df_dash["Total_Paid"] = 0.0

                merged = df_dash.copy()
                merged["Remaining_Balance"] = (
                    merged["COD_Balance"] - merged["Total_Paid"]
                )

                # 2) جلب أرقام الهواتف والأكواد من قاعدة بيانات المناديب
                riders_db = get_riders()
                if riders_db:
                    df_riders_db = pd.DataFrame(riders_db)
                    df_riders_db["Code_Clean"] = df_riders_db.get("code", pd.Series([""]*len(df_riders_db))).apply(clean_code)
                    df_riders_db["Name_Clean"] = df_riders_db.get("name", pd.Series([""]*len(df_riders_db))).apply(clean_text)
                    
                    if "phone" in df_riders_db.columns:
                        df_riders_db["Phone_Val"] = df_riders_db["phone"].apply(clean_code)
                    else:
                        df_riders_db["Phone_Val"] = ""

                    phone_map_code = df_riders_db[df_riders_db["Code_Clean"] != ""].set_index("Code_Clean")["Phone_Val"].to_dict()
                    phone_map_name = df_riders_db[df_riders_db["Name_Clean"] != ""].set_index("Name_Clean")["Phone_Val"].to_dict()

                    code_map_name = df_riders_db[df_riders_db["Name_Clean"] != ""].set_index("Name_Clean")["Code_Clean"].to_dict()

                    # استكمال الأكواد الفارغة إن وُجدت
                    merged["Code_Clean"] = merged.apply(
                        lambda r: r["Code_Clean"] if r["Code_Clean"] else code_map_name.get(r["Name_Clean"], ""), axis=1
                    )

                    merged["رقم الموبايل"] = merged["Code_Clean"].map(phone_map_code)
                    merged["رقم الموبايل"] = merged["رقم الموبايل"].fillna(merged["Name_Clean"].map(phone_map_name))
                    merged["رقم الموبايل"] = merged["رقم الموبايل"].replace("", "غير مسجل").fillna("غير مسجل")
                else:
                    merged["رقم الموبايل"] = "غير مسجل"

                # 3) جلب إجمالي المرتب
                salaries_db = get_salaries_data()
                if salaries_db:
                    df_sal_db = pd.DataFrame(salaries_db)
                    df_sal_db["Code_Clean"] = df_sal_db.get("rider_code", pd.Series([""]*len(df_sal_db))).apply(clean_code)
                    df_sal_db["Name_Clean"] = df_sal_db.get("rider_name", pd.Series([""]*len(df_sal_db))).apply(clean_text)
                    df_sal_db["Salary_Val"] = pd.to_numeric(df_sal_db.get("amount", pd.Series([0]*len(df_sal_db))), errors="coerce").fillna(0)

                    sal_sum_code = df_sal_db[df_sal_db["Code_Clean"] != ""].groupby("Code_Clean")["Salary_Val"].sum().to_dict()
                    sal_sum_name = df_sal_db[df_sal_db["Name_Clean"] != ""].groupby("Name_Clean")["Salary_Val"].sum().to_dict()

                    merged["إجمالي المرتب"] = merged["Code_Clean"].map(sal_sum_code)
                    merged["إجمالي المرتب"] = merged["إجمالي المرتب"].fillna(merged["Name_Clean"].map(sal_sum_name))
                    merged["إجمالي المرتب"] = merged["إجمالي المرتب"].fillna(0)
                else:
                    merged["إجمالي المرتب"] = 0

                def categorize(row):
                    cod = row["COD_Balance"]
                    paid = row["Total_Paid"]
                    rem = row["Remaining_Balance"]
                    status = str(row[status_col]).lower() if status_col and status_col in row else ""

                    if status == "left" and rem > 0:
                        return "⚠️ مغادر وعليه مديونية"
                    elif rem <= 0 and cod > 0:
                        return "🟢 تم التسوية بالكامل"
                    elif paid > 0 and rem > 0:
                        return "🟡 توريد جزئي (متبقي فلوس)"
                    elif cod > 0 and paid == 0:
                        return "🔴 لم يورد إطلاقاً"
                    else:
                        return "⚪ لا يوجد عليه عهدة"

                merged["الحالة المالية"] = merged.apply(categorize, axis=1)

                st.markdown(
                    "<div class='section-title'>📈 ملخص موقف العهد والتوريدات</div>",
                    unsafe_allow_html=True,
                )
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(
                    "إجمالي عهدة الداشبورد", f"{int(merged['COD_Balance'].sum()):,} ج.م"
                )
                c2.metric(
                    "إجمالي التوريدات المسجلة", f"{int(merged['Total_Paid'].sum()):,} ج.م"
                )
                c3.metric(
                    "الصافي المطلوب تحصيله",
                    f"{int(merged['Remaining_Balance'].sum()):,} ج.م",
                )
                c4.metric(
                    "مناديب مغادرين بمديونية",
                    f"{merged[merged['الحالة المالية'] == '⚠️ مغادر وعليه مديونية'].shape[0]} مندوب",
                )

                st.divider()

                merged[id_col] = merged["Code_Clean"]

                display_cols = [id_col, name_col_dash, "رقم الموبايل"]
                if status_col and status_col in merged.columns:
                    display_cols.append(status_col)
                if vendor_col and vendor_col in merged.columns:
                    display_cols.append(vendor_col)
                
                display_cols.extend(
                    ["COD_Balance", "Total_Paid", "Remaining_Balance", "إجمالي المرتب", "الحالة المالية"]
                )

                final_table = merged[display_cols].copy()
                final_table[id_col] = final_table[id_col].apply(clean_code)
                final_table.rename(
                    columns={
                        id_col: "كود المندوب",
                        name_col_dash: "اسم المندوب",
                        "COD_Balance": "عهدة الداشبورد",
                        "Total_Paid": "إجمالي المورد هذا الشهر",
                        "Remaining_Balance": "المتبقي الفعلي",
                    },
                    inplace=True,
                )

                st.dataframe(
                    final_table.sort_values(by="المتبقي الفعلي", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                )
            except Exception as e:
                st.error(f"خطأ في معالجة البيانات: {e}")

# ==========================================
# الشاشة الثانية: تسجيل توريد يومي
# ==========================================
elif menu == "➕ إضافة / تسجيل توريد يومي":
    st.markdown(
        """
    <div class="main-header">
        <h1>➕ تسجيل توريد جديد للمندوب (سحابي)</h1>
        <p>حفظ فوري في قاعدة البيانات السحابية لضمان عدم ضياع أي بيانات</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "<div class='section-title'>1️⃣ تسجيل توريد فردي</div>",
            unsafe_allow_html=True,
        )
        riders_data = get_riders()

        if not riders_data:
            st.warning("⚠️ لا يوجد مناديب مسجلين.")
            rider_code_input = st.text_input("كود المندوب:", key="single_pay_code")
            rider_name_input = st.text_input("اسم المندوب:", key="single_pay_name")
            selected_rider_name = rider_name_input
            selected_rider_code = rider_code_input
        else:
            rider_options = {
                f"{clean_code(r.get('code'))} - {r['name']}": r for r in riders_data if "name" in r
            }
            choice = st.selectbox("اختر المندوب:", list(rider_options.keys()), key="single_pay_select")
            selected_rider_name = rider_options[choice]["name"]
            selected_rider_code = rider_options[choice].get("code", "")

        pay_date = st.date_input("تاريخ التوريد:", key="single_pay_date")
        amount = st.number_input("المبلغ المورد (ج.م):", min_value=0, step=50, key="single_pay_amount")
        notes = st.text_input("ملاحظات / رقم الإيصال:", key="single_pay_notes")

        if st.button("💾 حفظ التوريد في السحابة", type="primary", key="btn_save_single_pay"):
            if selected_rider_name and amount > 0:
                with st.spinner("جاري إرسال الحفظ للسحابة..."):
                    auto_register_rider(selected_rider_code, selected_rider_name)
                    supabase.table("payments").insert({
                        "rider_code": clean_code(selected_rider_code),
                        "rider_name": str(selected_rider_name).strip(),
                        "date": str(pay_date),
                        "amount": float(amount),
                        "notes": notes if notes else "تعديل/إدخال يدوي",
                    }).execute()
                
                st.toast(f"✅ تم الحفظ: {amount} ج.م - {selected_rider_name}", icon="🎉")
                st.success(
                    f"🎉 **تم تسجيل التوريد بنجاح!**\n\n"
                    f"👤 **المندوب:** {selected_rider_name}\n\n"
                    f"💰 **المبلغ:** {int(amount):,} ج.م\n\n"
                    f"📅 **التاريخ:** {pay_date}"
                )
            else:
                st.error("⚠️ يرجى التأكد من اختيار المندوب وكتابة مبلغ أكبر من صفر.")

    with col2:
        st.markdown(
            "<div class='section-title'>2️⃣ رفع شيت توريدات (جملة)</div>",
            unsafe_allow_html=True,
        )
        batch_file = st.file_uploader(
            "ارفع شيت التوريدات (Excel/CSV)",
            type=["xlsx", "xls", "csv"],
            key="batch",
        )

        if batch_file:
            if st.button("📥 رفع وسحب البيانات للسحابة", type="primary", key="btn_upload_batch"):
                try:
                    df_b = (
                        pd.read_csv(batch_file)
                        if batch_file.name.endswith(".csv")
                        else pd.read_excel(batch_file)
                    )
                    cols = df_b.columns.tolist()

                    code_c = next(
                        (
                            c
                            for c in cols
                            if "id" in str(c).lower() or "كود" in str(c).lower()
                        ),
                        None,
                    )
                    name_c = next(
                        (
                            c
                            for c in cols
                            if any(
                                k in str(c).lower()
                                for k in ["name", "اسم", "الطيار", "rider", "driver"]
                            )
                        ),
                        cols[0],
                    )
                    amount_c = next(
                        (
                            c
                            for c in cols
                            if any(
                                k in str(c).lower()
                                for k in [
                                    "earnings",
                                    "مستحقات",
                                    "أرباح",
                                    "ارباح",
                                    "مبلغ",
                                    "paid",
                                    "amount",
                                ]
                            )
                        ),
                        cols[-1],
                    )
                    date_c = next(
                        (
                            c
                            for c in cols
                            if "date" in str(c).lower() or "تاريخ" in str(c).lower()
                        ),
                        None,
                    )
                    notes_c = next(
                        (
                            c
                            for c in cols
                            if "note" in str(c).lower() or "ملاحظ" in str(c).lower()
                        ),
                        None,
                    )

                    new_payments = []

                    for _, r in df_b.iterrows():
                        if pd.notna(r[name_c]) and pd.notna(r[amount_c]):
                            try:
                                raw_amt = str(r[amount_c]).replace(",", "").strip()
                                amt_val = float(raw_amt)
                                r_name_val = str(r[name_c]).strip()
                                r_code_val = clean_code(r[code_c]) if code_c and pd.notna(r[code_c]) else ""

                                parsed_date = pd.to_datetime(r[date_c], errors="coerce") if date_c and pd.notna(r[date_c]) else pd.Timestamp.now()
                                r_date_val = str(parsed_date.date()) if pd.notna(parsed_date) else str(pd.Timestamp.now().date())

                                r_notes_val = (
                                    str(r[notes_c]).strip()
                                    if (notes_c and pd.notna(r[notes_c]))
                                    else "استيراد شيت"
                                )

                                if amt_val > 0 and r_name_val:
                                    auto_register_rider(r_code_val, r_name_val)
                                    new_payments.append({
                                        "rider_code": r_code_val,
                                        "rider_name": r_name_val,
                                        "date": r_date_val,
                                        "amount": amt_val,
                                        "notes": r_notes_val,
                                    })
                            except Exception:
                                continue

                    if new_payments:
                        supabase.table("payments").insert(new_payments).execute()
                        st.toast(f"✅ تم رفع {len(new_payments)} حركة!", icon="🚀")
                        st.success(f"✅ تم رفع {len(new_payments)} حركة توريد بنجاح للسحابة!")
                    else:
                        st.warning("⚠️ لم يتم العثور على حركات توريد صالحة في الملف.")

                except Exception as e:
                    st.error(f"خطأ أثناء معالجة الملف: {e}")

# ==========================================
# الشاشة الثالثة: إدارة أسماء المناديب
# ==========================================
elif menu == "👥 إدارة أسماء المناديب":
    st.markdown(
        """
    <div class="main-header">
        <h1>👥 إدارة قاعدة بيانات المناديب (سحابياً)</h1>
        <p>إضافة، رفع شيت المناديب، تحديث الموبايل، وحذف المناديب مع الأرشيف</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("<div class='section-title'>➕ إضافة مندوب جديد فردياً</div>", unsafe_allow_html=True)
        r_code = st.text_input("كود المندوب (ID):", key="add_rider_code")
        r_name = st.text_input("اسم المندوب بالكامل:", key="add_rider_name")
        r_phone = st.text_input("رقم الموبايل:", key="add_rider_phone")
        if st.button("إضافة المندوب للسحابة", type="primary", key="btn_add_rider"):
            if r_name:
                auto_register_rider(r_code, r_name, r_phone)
                st.toast("✅ تم تسجيل المندوب بنجاح!", icon="👤")
                st.success("تمت إضافة المندوب بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم المندوب على الأقل.")

    with col_r2:
        st.markdown("<div class='section-title'>📤 رفع شيت قاعدة بيانات المناديب</div>", unsafe_allow_html=True)
        riders_file = st.file_uploader("ارفع شيت المناديب (Excel/CSV):", type=["xlsx", "xls", "csv"], key="riders_bulk")
        if riders_file:
            if st.button("📥 رفع وحفظ بيانات المناديب", type="primary", key="btn_upload_riders"):
                try:
                    df_rf = pd.read_csv(riders_file) if riders_file.name.endswith(".csv") else pd.read_excel(riders_file)
                    rf_cols = df_rf.columns.tolist()

                    code_col_r = next((c for c in rf_cols if any(k in str(c).lower() for k in ["code", "id", "كود"])), rf_cols[0])
                    name_col_r = next((c for c in rf_cols if any(k in str(c).lower() for k in ["name", "اسم", "rider", "طيار"])), rf_cols[1] if len(rf_cols) > 1 else rf_cols[0])
                    phone_col_r = next((c for c in rf_cols if any(k in str(c).lower() for k in ["phone", "mobile", "موبايل", "هاتف", "تليفون"])), None)

                    count_added = 0
                    for _, row in df_rf.iterrows():
                        raw_name = str(row[name_col_r]).strip() if pd.notna(row[name_col_r]) else ""
                        if not raw_name:
                            continue
                        
                        raw_code = clean_code(row[code_col_r]) if pd.notna(row[code_col_r]) else ""
                        raw_phone = clean_code(row[phone_col_r]) if phone_col_r and pd.notna(row[phone_col_r]) else ""

                        auto_register_rider(raw_code, raw_name, raw_phone)
                        count_added += 1

                    st.toast(f"✅ تم معالجة الشيت بنجاح!", icon="🚀")
                    st.success("✅ تم تحديث ومعالجة قاعدة البيانات بدون تكرار بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ أثناء رفع الملف: {e}")

    st.divider()

    col_edit1, col_edit2 = st.columns(2)

    with col_edit1:
        st.markdown("<div class='section-title'>📱 إضافة / تعديل رقم الموبايل والكود</div>", unsafe_allow_html=True)
        riders_list_edit = get_riders()
        if riders_list_edit:
            r_edit_options = {f"{clean_code(r.get('code'))} - {r.get('name', '')}": r for r in riders_list_edit if "name" in r}
            if r_edit_options:
                selected_r_edit = st.selectbox("اختر المندوب لتحديث بياناته:", list(r_edit_options.keys()), key="select_edit_rider")
                selected_rider_obj = r_edit_options[selected_r_edit]
                
                new_c = st.text_input("كود المندوب:", value=clean_code(selected_rider_obj.get("code")), key="edit_rider_code")
                new_p = st.text_input("رقم الموبايل:", value=clean_code(selected_rider_obj.get("phone")), key="edit_rider_phone")

                if st.button("💾 حفظ التعديل للمندوب", type="primary", key="btn_save_edit_rider"):
                    try:
                        supabase.table("riders").update({
                            "code": clean_code(new_c),
                            "phone": clean_code(new_p)
                        }).eq("id", selected_rider_obj.get("id")).execute()

                        st.toast("✅ تم تحديث بيانات المندوب!", icon="📲")
                        st.success("تم تحديث البيانات بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في الحفظ: {e}")

    with col_edit2:
        st.markdown("<div class='section-title'>🗑️ حذف مندوب وأرشفته</div>", unsafe_allow_html=True)
        riders_list = get_riders()
        if riders_list:
            r_options = {f"{clean_code(r.get('code'))} - {r.get('name', '')}": r for r in riders_list if "name" in r}
            if r_options:
                selected_r_del = st.selectbox("اختر المندوب المراد حذفه:", list(r_options.keys()), key="del_rider_select")
                
                if st.button("❌ نقل المندوب للأرشيف وحذفه", type="secondary", key="btn_del_rider"):
                    r_item = r_options[selected_r_del]
                    try:
                        supabase.table("deleted_riders").insert({
                            "original_id": r_item.get("id"),
                            "code": clean_code(r_item.get("code")),
                            "name": r_item.get("name", ""),
                            "phone": clean_code(r_item.get("phone")),
                            "deleted_at": str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }).execute()

                        supabase.table("riders").delete().eq("id", r_item.get("id")).execute()
                        st.toast("✅ تم حذف المندوب وأرشفته بنجاح!", icon="🗑️")
                        st.success(f"تم حذف المندوب ({r_item.get('name')}) ونقله للأرشيف.")
                        st.rerun()
                    except Exception as e:
                        try:
                            supabase.table("riders").delete().eq("id", r_item.get("id")).execute()
                            st.success(f"تم حذف المندوب ({r_item.get('name')}) بنجاح.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"خطأ أثناء حذف المندوب: {ex}")
        else:
            st.info("لا يوجد مناديب مسجلين للحذف.")

    st.divider()
    st.subheader("📋 قاعدة بيانات أسماء المناديب المعتمدة")
    riders_list = get_riders()
    if riders_list:
        df_r_show = pd.DataFrame(riders_list)
        
        cols_to_show = []
        if "code" in df_r_show.columns: 
            df_r_show["code"] = df_r_show["code"].apply(clean_code)
            cols_to_show.append("code")
        if "name" in df_r_show.columns: 
            cols_to_show.append("name")
        if "phone" in df_r_show.columns: 
            df_r_show["phone"] = df_r_show["phone"].apply(clean_code)
            cols_to_show.append("phone")
        
        df_r_show = df_r_show[cols_to_show].fillna("")
        df_r_show.rename(columns={
            "code": "كود المندوب",
            "name": "اسم المندوب",
            "phone": "رقم الموبايل"
        }, inplace=True)

        st.dataframe(df_r_show, use_container_width=True, hide_index=True)

        csv_r = df_r_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل كامل قاعدة بيانات المناديب (CSV)",
            data=csv_r,
            file_name="riders_database.csv",
            mime="text/csv",
            key="btn_download_riders_csv"
        )
    else:
        st.info("لا يوجد مناديب مسجلين حالياً.")

# ==========================================
# الشاشة الرابعة: سجل التوريدات والأرشيف
# ==========================================
elif menu == "📜 سجل التوريدات الشهرية":
    st.markdown(
        """
    <div class="main-header">
        <h1>📜 سجل التوريدات وإدارتها</h1>
        <p>حذف وإدارة التوريدات مع حماية البيانات عبر الأرشيف السحابي</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    payments_list = get_payments()

    st.subheader("🗑️ حذف توريد محدد ونقله للأرشيف")
    if payments_list:
        pay_options = {
            f"ID: {p.get('id')} - {p.get('rider_name', '')} - {int(p.get('amount', 0)):,} ج.م ({p.get('date', '')})": p
            for p in payments_list if "id" in p
        }
        if pay_options:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                selected_pay_str = st.selectbox(
                    "اختر التوريد المراد حسابه:", list(pay_options.keys()), key="select_pay_to_del"
                )
            with col_btn:
                st.write("")
                st.write("")
                if st.button("❌ نقل إلى أرشيف المحذوفات", type="secondary", key="btn_move_to_archive"):
                    selected_item = pay_options[selected_pay_str]
                    pay_id = selected_item["id"]
                    try:
                        supabase.table("deleted_payments").insert({
                            "original_id": pay_id,
                            "rider_code": clean_code(selected_item.get("rider_code")),
                            "rider_name": selected_item.get("rider_name", ""),
                            "amount": selected_item.get("amount", 0.0),
                            "date": str(selected_item.get("date", "")),
                            "notes": selected_item.get("notes", ""),
                            "deleted_at": str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
                        }).execute()

                        supabase.table("payments").delete().eq("id", pay_id).execute()
                        st.toast("🗑️ تم النقل للأرشيف", icon="✅")
                        st.success("✅ تم نقل التوريد إلى الأرشيف بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ تعذر نقل الحركة للأرشيف بسبب خطأ: {e}")
    else:
        st.info("لا توجد توريدات حالية للحذف.")

    st.divider()

    st.subheader("📋 التوريدات الحالية النشطة")
    if payments_list:
        df_p = pd.DataFrame(payments_list)
        if "rider_code" in df_p.columns:
            df_p["rider_code"] = df_p["rider_code"].apply(clean_code)
        cols = ["id", "rider_code", "rider_name", "date", "amount", "notes"]
        available_cols = [c for c in cols if c in df_p.columns]
        df_p_show = df_p[available_cols].copy()
        df_p_show.rename(
            columns={
                "id": "رقم الحركة",
                "rider_code": "كود المندوب",
                "rider_name": "اسم المندوب",
                "date": "التاريخ",
                "amount": "المبلغ",
                "notes": "ملاحظات",
            },
            inplace=True,
        )
        st.dataframe(df_p_show, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد توريدات مسجلة بالسحابة حتى الآن.")

    st.divider()

    st.subheader("🗑️ أرشيف المحذوفات (الاسترجاع أو الحذف النهائي)")
    deleted_list = get_deleted_payments()

    if deleted_list:
        del_options = {
            f"ID الأرشيف: {d.get('id')} | المندوب: {d.get('rider_name', '')} | المبلغ: {int(d.get('amount', 0)):,} ج.م | الحذف: {d.get('deleted_at', '')}": d
            for d in deleted_list if "id" in d
        }

        if del_options:
            selected_del_str = st.selectbox(
                "اختر التوريد المحذوف للتحكم به:",
                list(del_options.keys()),
                key="select_archived_pay"
            )

            col_act1, col_act2, col_act3 = st.columns([2, 2, 1])

            with col_act1:
                if st.button("↩️ استرجاع التوريد المختار", type="primary", key="btn_restore_pay"):
                    item_to_restore = del_options[selected_del_str]
                    del_id = item_to_restore.get("id")
                    try:
                        supabase.table("payments").insert({
                            "rider_code": clean_code(item_to_restore.get("rider_code")),
                            "rider_name": item_to_restore.get("rider_name", ""),
                            "date": str(item_to_restore.get("date", "")),
                            "amount": float(item_to_restore.get("amount", 0.0)),
                            "notes": f"مسترجع من المحذوفات: {item_to_restore.get('notes', '')}",
                        }).execute()

                        supabase.table("deleted_payments").delete().eq("id", del_id).execute()
                        st.toast("↩️ تم الاسترجاع بنجاح!", icon="🎉")
                        st.success("✅ تم استرجاع التوريد وإعادته للتوريدات النشطة!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ أثناء استرجاع البيانات: {e}")

            with col_act2:
                if st.button("❌ حذف نهائي من الأرشيف", type="secondary", key="btn_perm_del_pay"):
                    item_to_delete = del_options[selected_del_str]
                    del_id = item_to_delete.get("id")
                    try:
                        supabase.table("deleted_payments").delete().eq("id", del_id).execute()
                        st.toast("🗑️ تم الحذف النهائي", icon="🔥")
                        st.success("✅ تم حذف الحركة نهائياً من أرشيف قاعدة البيانات!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ أثناء الحذف النهائي: {e}")

            with col_act3:
                if st.button("🔥 إفراغ الأرشيف", key="btn_empty_archive"):
                    try:
                        supabase.table("deleted_payments").delete().neq("id", 0).execute()
                        st.toast("🔥 تم مسح الأرشيف بالكامل", icon="🧹")
                        st.success("✅ تم إفراغ الأرشيف بالكامل بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ أثناء تفريغ الأرشيف: {e}")

        st.write("")
        df_del = pd.DataFrame(deleted_list)
        if "rider_code" in df_del.columns:
            df_del["rider_code"] = df_del["rider_code"].apply(clean_code)
        cols_del = [
            "id",
            "rider_code",
            "rider_name",
            "date",
            "amount",
            "notes",
            "deleted_at",
        ]
        available_cols_del = [c for c in cols_del if c in df_del.columns]
        df_del_show = df_del[available_cols_del].copy()
        df_del_show.rename(
            columns={
                "id": "معرف الأرشيف",
                "rider_code": "كود المندوب",
                "rider_name": "اسم المندوب",
                "date": "تاريخ التوريد الأصلي",
                "amount": "المبلغ",
                "notes": "ملاحظات",
                "deleted_at": "توقيت الحذف",
            },
            inplace=True,
        )
        st.dataframe(df_del_show, use_container_width=True, hide_index=True)
    else:
        st.info("سجل المحذوفات فارغ، لم يتم حذف أي حركات مؤخراً.")

    st.divider()
    with st.expander("⚠️ منطقة الخطر: مسح كافة التوريدات النشطة"):
        st.warning("تحذير: سيقوم هذا الخيار بنقل جميع التوريدات النشطة إلى جدول الأرشيف.")
        
        if "confirm_delete_all" not in st.session_state:
            st.session_state.confirm_delete_all = False

        if not st.session_state.confirm_delete_all:
            if st.button("🔥 مسح كافة التوريدات", type="primary", key="btn_clear_all_payments"):
                st.session_state.confirm_delete_all = True
                st.rerun()
        else:
            st.error("🚨 هل أنت متأكد تماماً من رغبتك في نقل كل التوريدات إلى الأرشيف؟")
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                if st.button("✅ نعم، تأكيد المسح الشامل", type="primary", key="btn_confirm_clear_all"):
                    if payments_list:
                        try:
                            records_to_archive = []
                            now_str = str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
                            for p in payments_list:
                                records_to_archive.append({
                                    "original_id": p.get("id"),
                                    "rider_code": clean_code(p.get("rider_code")),
                                    "rider_name": p.get("rider_name", ""),
                                    "amount": p.get("amount", 0.0),
                                    "date": str(p.get("date", "")),
                                    "notes": p.get("notes", ""),
                                    "deleted_at": now_str,
                                })

                            if records_to_archive:
                                supabase.table("deleted_payments").insert(records_to_archive).execute()

                            supabase.table("payments").delete().neq("id", 0).execute()
                            st.session_state.confirm_delete_all = False
                            st.success("✅ تم مسح ونقل كافة التوريدات للأرشيف بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"خطأ أثناء المسح الشامل: {e}")
                    else:
                        st.info("لا توجد بيانات للمسح.")
                        st.session_state.confirm_delete_all = False
            with col_conf2:
                if st.button("❌ إلغاء", key="btn_cancel_clear_all"):
                    st.session_state.confirm_delete_all = False
                    st.rerun()

# ==========================================
# الشاشة الخامسة: تجميع مرتبات المناديب
# ==========================================
elif menu == "💰 تجميع مرتبات المناديب":
    st.markdown(
        """
    <div class="main-header">
        <h1>💰 تجميع مرتبات المناديب وحساب الاستحقاقات</h1>
        <p>تجميع المرتبات بالسحابة مع إمكانية الفلترة وتحديد شهر منفصل بسهولة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_s1, col_s2 = st.columns([3, 1])

    with col_s1:
        sal_file = st.file_uploader(
            "📥 ارفع شيت مرتبات جديد (Excel أو CSV):", type=["xlsx", "xls", "csv"], key="salary_file"
        )

    with col_s2:
        st.write("🗑️ مسح شيت المرتبات المحفوظ:")
        if st.button("🔥 مسح المرتبات المحفوظة", key="btn_clear_salaries"):
            if delete_salaries_data():
                st.success("✅ تم مسح المرتبات المحفوظة!")
                st.rerun()

    grouped_data = None

    if sal_file:
        try:
            df_sal = (
                pd.read_csv(sal_file)
                if sal_file.name.endswith(".csv")
                else pd.read_excel(sal_file)
            )

            cols = df_sal.columns.tolist()

            code_c = next(
                (c for c in cols if any(k in str(c).lower() for k in ["كود", "id", "code"])),
                cols[0],
            )
            name_c = next(
                (c for c in cols if any(k in str(c).lower() for k in ["اسم", "name", "مندوب", "طيار", "rider", "driver"])),
                cols[1] if len(cols) > 1 else cols[0],
            )
            salary_c = next(
                (c for c in cols if any(k in str(c).lower() for k in ["مرتب", "مبلغ", "مستحق", "صافي", "salary", "amount", "earning", "total", "يومي"])),
                cols[-1],
            )
            date_c = next(
                (c for c in cols if any(k in str(c).lower() for k in ["تاريخ", "شهر", "date", "month", "day", "يوم"])),
                None,
            )

            st.markdown("<div class='section-title'>⚙️ تحديد أعمدة شيت المرتبات</div>", unsafe_allow_html=True)
            col_sel1, col_sel2, col_sel3, col_sel4 = st.columns(4)

            with col_sel1:
                selected_code_col = st.selectbox("عمود كود المندوب:", cols, index=cols.index(code_c), key="sal_col_code")
            with col_sel2:
                selected_name_col = st.selectbox("عمود اسم المندوب:", cols, index=cols.index(name_c), key="sal_col_name")
            with col_sel3:
                selected_sal_col = st.selectbox("عمود المرتب / المبلغ:", cols, index=cols.index(salary_c), key="sal_col_amount")
            with col_sel4:
                date_options = ["بدون تحديد / شهر واحد"] + cols
                default_date_idx = (cols.index(date_c) + 1) if date_c and date_c in cols else 0
                selected_date_col = st.selectbox("عمود التاريخ / الشهر (للتقسيم):", date_options, index=default_date_idx, key="sal_col_date")

            df_sal["Salary_Clean"] = pd.to_numeric(
                df_sal[selected_sal_col].astype(str).str.replace(",", "").str.strip(), errors="coerce"
            ).fillna(0)

            df_sal["Code_Clean"] = df_sal[selected_code_col].apply(clean_code)
            df_sal["Name_Clean"] = df_sal[selected_name_col].astype(str).str.strip()

            if selected_date_col != "بدون تحديد / شهر واحد":
                df_sal["Parsed_Date"] = pd.to_datetime(df_sal[selected_date_col], errors="coerce")
                df_sal["Month_Year"] = df_sal["Parsed_Date"].dt.strftime("%Y-%m").fillna("غير محدد")
                group_cols = ["Month_Year", "Code_Clean", "Name_Clean"]
            else:
                group_cols = ["Code_Clean", "Name_Clean"]

            grouped_data = df_sal.groupby(group_cols, as_index=False)["Salary_Clean"].sum()

            for _, r_item in grouped_data.iterrows():
                auto_register_rider(r_item["Code_Clean"], r_item["Name_Clean"])

            save_salaries_data(grouped_data)
            st.success("✅ تم معالجة وحفظ شيت المرتبات في السحابة بنجاح!")

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء معالجة شيت المرتبات: {e}")

    else:
        saved_salaries = get_salaries_data()
        if saved_salaries:
            grouped_data = pd.DataFrame(saved_salaries)
            grouped_data.rename(
                columns={
                    "rider_code": "Code_Clean",
                    "rider_name": "Name_Clean",
                    "amount": "Salary_Clean",
                    "month_year": "Month_Year",
                },
                inplace=True,
            )

    if grouped_data is not None and not grouped_data.empty:
        st.divider()

        if "Month_Year" in grouped_data.columns and grouped_data["Month_Year"].notna().any():
            available_months = sorted(grouped_data["Month_Year"].dropna().unique().tolist())

            col_flt1, col_flt2 = st.columns([1, 2])
            with col_flt1:
                selected_month_filter = st.selectbox(
                    "📅 اختر الشهر لإظهاره منفصلاً:",
                    ["عرض كافة الأشهر"] + available_months,
                    key="filter_sal_month"
                )

            if selected_month_filter != "عرض كافة الأشهر":
                df_display = grouped_data[grouped_data["Month_Year"] == selected_month_filter].copy()
                st.markdown(f"<div class='section-title'>📊 إجمالي مرتبات شهر ({selected_month_filter})</div>", unsafe_allow_html=True)
            else:
                df_display = grouped_data.copy()
                st.markdown("<div class='section-title'>📊 إجمالي كافة الأشهر المسجلة</div>", unsafe_allow_html=True)

            st.metric("إجمالي المرتبات لهذا العرض", f"{int(df_display['Salary_Clean'].sum()):,} ج.م")

            final_sal_table = df_display.rename(
                columns={
                    "Month_Year": "الشهر / السنة",
                    "Code_Clean": "كود المندوب",
                    "Name_Clean": "اسم المندوب",
                    "Salary_Clean": "إجمالي المرتب المستحق",
                }
            )
            final_sal_table["كود المندوب"] = final_sal_table["كود المندوب"].apply(clean_code)
            final_sal_table = final_sal_table.sort_values(by="اسم المندوب")
            st.dataframe(final_sal_table, use_container_width=True, hide_index=True)

        else:
            st.markdown("<div class='section-title'>📊 إجمالي المرتبات المحفوظة</div>", unsafe_allow_html=True)
            st.metric("إجمالي المرتبات للكل", f"{int(grouped_data['Salary_Clean'].sum()):,} ج.م")

            final_sal_table = grouped_data.rename(
                columns={
                    "Code_Clean": "كود المندوب",
                    "Name_Clean": "اسم المندوب",
                    "Salary_Clean": "إجمالي المرتب المستحق",
                }
            )
            final_sal_table["كود المندوب"] = final_sal_table["كود المندوب"].apply(clean_code)
            final_sal_table = final_sal_table.sort_values(by="إجمالي المرتب المستحق", ascending=False)
            st.dataframe(final_sal_table, use_container_width=True, hide_index=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            final_sal_table.to_excel(writer, index=False, sheet_name="تقرير المرتبات")

        st.download_button(
            label="📥 تحميل التقرير المعروض (Excel)",
            data=buffer.getvalue(),
            file_name="Salaries_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            key="btn_download_sal_excel"
        )
    else:
        st.info("💡 لا يوجد شيت مرتبات محفوظ حالياً. قم برفع شيت مرتبات جديد للبدء.")
