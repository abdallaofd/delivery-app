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


# دوال قراءة وحفظ البيانات من السحابة مباشرة
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


def save_dashboard_data(df_dash, id_col, name_col, cod_col, status_col, vendor_col):
    try:
        supabase.table("dashboard_data").delete().neq("id", 0).execute()
        records = []
        for _, r in df_dash.iterrows():
            records.append({
                "rider_code": str(r[id_col]).strip() if pd.notna(r[id_col]) else "",
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


# ---- دوال شيت المرتبات ----
def save_salaries_data(df_sal_grouped):
    try:
        supabase.table("salaries_data").delete().neq("id", 0).execute()
        records = []
        for _, r in df_sal_grouped.iterrows():
            rec = {
                "rider_code": str(r["Code_Clean"]),
                "rider_name": str(r["Name_Clean"]),
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


# ---- دوال الشاشة الجديدة (بيانات الموظفين والمناديب employees_data) ----
def get_employees_data():
    try:
        res = supabase.table("employees_data").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []


def save_employee_data(emp_dict):
    try:
        supabase.table("employees_data").insert(emp_dict).execute()
        return True
    except Exception:
        return False


def save_employees_batch(records_list):
    try:
        supabase.table("employees_data").insert(records_list).execute()
        return True
    except Exception:
        return False


def auto_register_rider(code, name):
    if not name or str(name).strip() == "":
        return
    code_str = str(code).strip() if pd.notna(code) else ""
    name_str = str(name).strip()

    existing_riders = get_riders()
    exists = any(
        r.get("name") == name_str or (code_str and r.get("code") == code_str)
        for r in existing_riders
    )

    if not exists:
        try:
            supabase.table("riders").insert(
                {"code": code_str, "name": name_str}
            ).execute()
        except Exception:
            pass


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip().lower()
    text = " ".join(text.split())
    return text


# ==========================================
# 2. إعدادات الصفحة والتصميم الاحترافي المنسق
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
        "📝 بيانات الموظفين والمناديب",
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
            df_dash["COD_Balance"] = pd.to_numeric(
                df_dash[cod_col], errors="coerce"
            ).fillna(0)

            for _, r_item in df_dash.iterrows():
                auto_register_rider(r_item[id_col], r_item[name_col_dash])

            payments_list = get_payments()
            if payments_list:
                df_pay_db = pd.DataFrame(payments_list)
                df_pay_db["Name_Clean"] = df_pay_db["rider_name"].apply(clean_text)
                pay_sum = (
                    df_pay_db.groupby("Name_Clean")["amount"].sum().reset_index()
                )
            else:
                pay_sum = pd.DataFrame(columns=["Name_Clean", "amount"])

            merged = pd.merge(
                df_dash,
                pay_sum.rename(columns={"amount": "Total_Paid"}),
                on="Name_Clean",
                how="left",
            )
            merged["Total_Paid"] = merged["Total_Paid"].fillna(0)
            merged["Remaining_Balance"] = (
                merged["COD_Balance"] - merged["Total_Paid"]
            )

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

            display_cols = [id_col, name_col_dash]
            if status_col and status_col in merged.columns:
                display_cols.append(status_col)
            if vendor_col and vendor_col in merged.columns:
                display_cols.append(vendor_col)
            display_cols.extend(
                ["COD_Balance", "Total_Paid", "Remaining_Balance", "الحالة المالية"]
            )

            final_table = merged[display_cols].copy()
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
            rider_code_input = st.text_input("كود المندوب:")
            rider_name_input = st.text_input("اسم المندوب:")
            selected_rider_name = rider_name_input
            selected_rider_code = rider_code_input
        else:
            rider_options = {
                f"{r.get('code', '')} - {r['name']}": r for r in riders_data
            }
            choice = st.selectbox("اختر المندوب:", list(rider_options.keys()))
            selected_rider_name = rider_options[choice]["name"]
            selected_rider_code = rider_options[choice].get("code", "")

        pay_date = st.date_input("تاريخ التوريد:")
        amount = st.number_input("المبلغ المورد (ج.م):", min_value=0, step=50)
        notes = st.text_input("ملاحظات / رقم الإيصال:")

        if st.button("💾 حفظ التوريد في السحابة", type="primary"):
            if selected_rider_name and amount > 0:
                with st.spinner("جاري إرسال الحفظ للسحابة..."):
                    auto_register_rider(selected_rider_code, selected_rider_name)
                    supabase.table("payments").insert({
                        "rider_code": str(selected_rider_code),
                        "rider_name": selected_rider_name,
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
            if st.button("📥 رفع وسحب البيانات للسحابة", type="primary"):
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
                    new_riders = {}

                    for _, r in df_b.iterrows():
                        if pd.notna(r[name_c]) and pd.notna(r[amount_c]):
                            try:
                                raw_amt = str(r[amount_c]).replace(",", "").strip()
                                amt_val = float(raw_amt)
                                r_name_val = str(r[name_c]).strip()
                                r_code_val = str(r[code_c]).strip() if code_c and pd.notna(r[code_c]) else ""

                                parsed_date = pd.to_datetime(r[date_c], errors="coerce") if date_c and pd.notna(r[date_c]) else pd.Timestamp.now()
                                r_date_val = str(parsed_date.date()) if pd.notna(parsed_date) else str(pd.Timestamp.now().date())

                                r_notes_val = (
                                    str(r[notes_c]).strip()
                                    if (notes_c and pd.notna(r[notes_c]))
                                    else "استيراد شيت"
                                )

                                if amt_val > 0 and r_name_val:
                                    if r_name_val not in new_riders:
                                        new_riders[r_name_val] = r_code_val

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
                        existing_riders = get_riders()
                        existing_names = {r.get("name") for r in existing_riders}
                        riders_to_insert = [
                            {"code": code, "name": name}
                            for name, code in new_riders.items()
                            if name not in existing_names
                        ]
                        if riders_to_insert:
                            supabase.table("riders").insert(riders_to_insert).execute()

                        supabase.table("payments").insert(new_payments).execute()
                        st.toast(f"✅ تم رفع {len(new_payments)} حركة!", icon="🚀")
                        st.success(f"✅ تم رفع {len(new_payments)} حركة توريد بنجاح للسحابة!")
                    else:
                        st.warning("⚠️ لم يتم العثور على حركات توريد صالحة في الملف.")

                except Exception as e:
                    st.error(f"خطأ أثناء معالجة الملف: {e}")

# ==========================================
# الشاشة الثالثة: إدارة أسماء المناديب (مع ميزة حذف وأرشفة المندوب)
# ==========================================
elif menu == "👥 إدارة أسماء المناديب":
    st.markdown(
        """
    <div class="main-header">
        <h1>👥 إدارة بيانات المناديب (سحابياً)</h1>
        <p>عرض، إضافة، وحذف المناديب مع وجود أرشيف كامل للمحذوفات</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("<div class='section-title'>➕ إضافة مندوب جديد</div>", unsafe_allow_html=True)
        r_code = st.text_input("كود المندوب (ID):")
        r_name = st.text_input("اسم المندوب بالكامل:")
        if st.button("إضافة المندوب للسحابة", type="primary"):
            if r_name:
                auto_register_rider(r_code, r_name)
                st.toast("✅ تم تسجيل المندوب بنجاح!", icon="👤")
                st.success("تمت إضافة المندوب بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال اسم المندوب على الأقل.")

    with col_r2:
        st.markdown("<div class='section-title'>🗑️ حذف مندوب وأرشفته</div>", unsafe_allow_html=True)
        riders_list = get_riders()
        if riders_list:
            r_options = {f"{r.get('code', '')} - {r['name']}": r for r in riders_list}
            selected_r_del = st.selectbox("اختر المندوب المراد حسفه:", list(r_options.keys()))
            
            if st.button("❌ نقل المندوب للأرشيف وحذفه", type="secondary"):
                r_item = r_options[selected_r_del]
                try:
                    # 1. نقل إلى أرشيف المناديب المحذوفين
                    supabase.table("deleted_riders").insert({
                        "original_id": r_item.get("id"),
                        "code": r_item.get("code", ""),
                        "name": r_item.get("name", ""),
                        "deleted_at": str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }).execute()

                    # 2. الحذف من جدول المناديب النشط
                    supabase.table("riders").delete().eq("id", r_item.get("id")).execute()
                    st.toast("✅ تم حذف المندوب وأرشفته بنجاح!", icon="🗑️")
                    st.success(f"تم حذف المندوب ({r_item.get('name')}) ونقله للأرشيف.")
                    st.rerun()
                except Exception as e:
                    # في حال عدم وجود جدول deleted_riders، يتم الحذف المباشر
                    try:
                        supabase.table("riders").delete().eq("id", r_item.get("id")).execute()
                        st.success(f"تم حذف المندوب ({r_item.get('name')}) بنجاح.")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"خطأ أثناء حذف المندوب: {ex}")
        else:
            st.info("لا يوجد مناديب مسجلين للحذف.")

    st.divider()
    st.subheader("📋 قائمة أسماء المناديب المعتمدة")
    riders_list = get_riders()
    if riders_list:
        df_r_show = pd.DataFrame(riders_list)
        if "code" in df_r_show.columns and "name" in df_r_show.columns:
            df_r_show = df_r_show[["code", "name"]]
            df_r_show.columns = ["كود المندوب", "اسم المندوب"]
            st.dataframe(df_r_show, use_container_width=True, hide_index=True)

            # زر تحميل قائمة المناديب Excel / CSV
            csv_r = df_r_show.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل قائمة المناديب (Excel / CSV)",
                data=csv_r,
                file_name="riders_list.csv",
                mime="text/csv"
            )
    else:
        st.info("لا يوجد مناديب مسجلين حالياً.")

# ==========================================
# الشاشة الرابعة: بيانات الموظفين والمناديب (مع الرقم القومي وزر التحميل)
# ==========================================
elif menu == "📝 بيانات الموظفين والمناديب":
    st.markdown(
        """
    <div class="main-header">
        <h1>📝 إدارة بيانات الموظفين والمناديب الشاملة</h1>
        <p>إدخال أو رفع شيت البيانات بالكامل للتزامن مع السحابة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["✍️ إدخال يدوي فردي", "📂 رفع شيت Excel/CSV"])

    with tab1:
        st.markdown("<div class='section-title'>➕ تسجيل موظف جديد / إضافة بيانات</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            e_user_code = st.text_input("🆔 كود المندوب / المستخدم (user_code):")
            e_name_ar = st.text_input("👤 الاسم بالعربي (name_ar):")
            e_national_id = st.text_input("🪪 رقم البطاقة / الرقم القومي (national_id):")
            e_branch = st.text_input("🏢 الفرع (branch_name):")

        with c2:
            e_work_mobile = st.text_input("📱 موبايل العمل (work_mobile):")
            e_personal_mobile = st.text_input("📞 الموبايل الشخصي (personal_mobile):")
            e_emergency_1 = st.text_input("🚨 طوارئ 1 (emergency_mobile_1):")
            e_emergency_2 = st.text_input("🚨 طوارئ 2 (emergency_mobile_2):")

        with c3:
            e_transfer_num = st.text_input("💳 رقم التحويل (transfer_number):")
            e_transfer_type = st.selectbox("🔄 نوع التحويل (transfer_type):", ["محفظة (فودافون/غيرها)", "أنستا باي", "حساب بنكي", "أخرى"])
            e_notes = st.text_area("📝 ملاحظات (notes):", height=108)

        if st.button("💾 حفظ البيانات الفردية في السحابة", type="primary"):
            if not e_user_code or not e_name_ar:
                st.error("❌ يرجى إدخال كود المندوب والاسم بالعربي على الأقل.")
            else:
                emp_record = {
                    "user_code": e_user_code.strip(),
                    "name_ar": e_name_ar.strip(),
                    "national_id": e_national_id.strip(),
                    "work_mobile": e_work_mobile.strip(),
                    "personal_mobile": e_personal_mobile.strip(),
                    "emergency_mobile_1": e_emergency_1.strip(),
                    "emergency_mobile_2": e_emergency_2.strip(),
                    "transfer_number": e_transfer_num.strip(),
                    "transfer_type": e_transfer_type,
                    "branch_name": e_branch.strip(),
                    "notes": e_notes.strip()
                }
                if save_employee_data(emp_record):
                    st.toast("✅ تم الحفظ بنجاح!", icon="🎉")
                    st.success("✅ تم حفظ بيانات الموظف في جدول employees_data السحابي!")
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ أثناء الحفظ. تأكد من إعدادات الجدول في Supabase.")

    with tab2:
        st.markdown("<div class='section-title'>📂 رفع واستيراد شيت كامل لبيانات الموظفين</div>", unsafe_allow_html=True)
        emp_file = st.file_uploader("ارفع شيت البيانات (Excel أو CSV)", type=["xlsx", "xls", "csv"], key="emp_uploader")

        if emp_file:
            try:
                df_e = pd.read_csv(emp_file) if emp_file.name.endswith(".csv") else pd.read_excel(emp_file)
                df_e.columns = [str(col).strip() for col in df_e.columns]
                cols_e = ["-- غير محدد --"] + list(df_e.columns)

                st.write("🔍 **ربط أعمدة الشيت مع حقول النظام:**")
                m1, m2, m3 = st.columns(3)
                
                with m1:
                    uc_col = st.selectbox("كود المندوب/المستخدم *", cols_e, index=1 if len(cols_e)>1 else 0)
                    ar_col = st.selectbox("الاسم بالعربي *", cols_e, index=2 if len(cols_e)>2 else 0)
                    nat_col = st.selectbox("رقم البطاقة/القومي", cols_e)
                    br_col = st.selectbox("الفرع", cols_e)

                with m2:
                    wm_col = st.selectbox("موبايل العمل", cols_e)
                    pm_col = st.selectbox("الموبايل الشخصي", cols_e)
                    em1_col = st.selectbox("طوارئ 1", cols_e)
                    em2_col = st.selectbox("طوارئ 2", cols_e)

                with m3:
                    tn_col = st.selectbox("رقم التحويل", cols_e)
                    tt_col = st.selectbox("نوع التحويل", cols_e)
                    nt_col = st.selectbox("ملاحظات", cols_e)

                if st.button("🚀 رفع الشيت بالكامل إلى السحابة", type="primary"):
                    if uc_col == "-- غير محدد --" or ar_col == "-- غير محدد --":
                        st.error("❌ يجب تحديد كود المندوب والاسم بالعربي على الأقل.")
                    else:
                        batch_records = []
                        for _, row in df_e.iterrows():
                            record = {
                                "user_code": str(row[uc_col]).strip() if uc_col != "-- غير محدد --" and pd.notna(row[uc_col]) else "",
                                "name_ar": str(row[ar_col]).strip() if ar_col != "-- غير محدد --" and pd.notna(row[ar_col]) else "",
                                "national_id": str(row[nat_col]).strip() if nat_col != "-- غير محدد --" and pd.notna(row[nat_col]) else "",
                                "work_mobile": str(row[wm_col]).strip() if wm_col != "-- غير محدد --" and pd.notna(row[wm_col]) else "",
                                "personal_mobile": str(row[pm_col]).strip() if pm_col != "-- غير محدد --" and pd.notna(row[pm_col]) else "",
                                "emergency_mobile_1": str(row[em1_col]).strip() if em1_col != "-- غير محدد --" and pd.notna(row[em1_col]) else "",
                                "emergency_mobile_2": str(row[em2_col]).strip() if em2_col != "-- غير محدد --" and pd.notna(row[em2_col]) else "",
                                "transfer_number": str(row[tn_col]).strip() if tn_col != "-- غير محدد --" and pd.notna(row[tn_col]) else "",
                                "transfer_type": str(row[tt_col]).strip() if tt_col != "-- غير محدد --" and pd.notna(row[tt_col]) else "",
                                "branch_name": str(row[br_col]).strip() if br_col != "-- غير محدد --" and pd.notna(row[br_col]) else "",
                                "notes": str(row[nt_col]).strip() if nt_col != "-- غير محدد --" and pd.notna(row[nt_col]) else "",
                            }
                            if record["user_code"] and record["name_ar"]:
                                batch_records.append(record)

                        if batch_records:
                            if save_employees_batch(batch_records):
                                st.toast(f"✅ تم رفع {len(batch_records)} سجل بنجاح!", icon="🎉")
                                st.success(f"✅ تم رفع وحفظ {len(batch_records)} سجل موظف في قاعدة البيانات بنجاح!")
                                st.rerun()
                            else:
                                st.error("❌ حدث خطأ أثناء إضافة البيانات السحابية.")
            except Exception as ex:
                st.error(f"حدث خطأ أثناء قراءة الملف: {ex}")

    st.divider()
    st.markdown("<div class='section-title'>📋 قائمة بيانات الموظفين المسجلة بالسحابة</div>", unsafe_allow_html=True)
    
    emp_list = get_employees_data()
    if emp_list:
        df_emp = pd.DataFrame(emp_list)
        col_map = {
            "id": "المعرف",
            "user_code": "الكود/المستخدم",
            "name_ar": "الاسم بالعربي",
            "national_id": "رقم البطاقة",
            "work_mobile": "موبايل العمل",
            "personal_mobile": "الموبايل الشخصي",
            "emergency_mobile_1": "طوارئ 1",
            "emergency_mobile_2": "طوارئ 2",
            "transfer_number": "رقم التحويل",
            "transfer_type": "نوع التحويل",
            "branch_name": "اسم الفرع",
            "notes": "ملاحظات",
            "created_at": "تاريخ التسجيل"
        }
        df_emp_show = df_emp.rename(columns=col_map)
        st.dataframe(df_emp_show, use_container_width=True, hide_index=True)

        # زر تحميل بيانات الموظفين Excel / CSV
        csv_emp = df_emp_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل كافة بيانات الموظفين (CSV / Excel)",
            data=csv_emp,
            file_name="employees_data_report.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("لا توجد بيانات موظفين مسجلة في جدول employees_data حتى الآن.")

# ==========================================
# الشاشة الخامسة: سجل التوريدات والأرشيف
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

    col_del1, col_del2 = st.columns([2, 1])

    with col_del1:
        st.subheader("🗑️ حذف توريد محدد ونقله للأرشيف")
        if payments_list:
            pay_options = {
                f"ID: {p['id']} - {p['rider_name']} - {int(p['amount']):,} ج.م ({p['date']})": p
                for p in payments_list
            }
            selected_pay_str = st.selectbox(
                "اختر التوريد المراد حسابه:", list(pay_options.keys())
            )
            if st.button("❌ نقل إلى أرشيف المحذوفات", type="secondary"):
                selected_item = pay_options[selected_pay_str]
                pay_id = selected_item["id"]
                try:
                    # 1. الأرشفة
                    supabase.table("deleted_payments").insert({
                        "original_id": pay_id,
                        "rider_code": selected_item.get("rider_code", ""),
                        "rider_name": selected_item.get("rider_name", ""),
                        "amount": selected_item.get("amount", 0.0),
                        "date": str(selected_item.get("date", "")),
                        "notes": selected_item.get("notes", ""),
                        "deleted_at": str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
                    }).execute()

                    # 2. الحذف من جدول التوريدات
                    supabase.table("payments").delete().eq("id", pay_id).execute()
                    st.toast("🗑️ تم النقل للأرشيف", icon="✅")
                    st.success("✅ تم نقل التوريد إلى الأرشيف بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ تعذر نقل الحركة للأرشيف بسبب خطأ في جدول الأرشيف: {e}")
        else:
            st.info("لا توجد توريدات حالية للحذف.")

    with col_del2:
        st.subheader("⚠️ مسح شامل")
        st.write("حذف كافة التوريدات ونقلها للأرشيف:")
        if st.button("🔥 مسح كافة التوريدات", type="primary"):
            if payments_list:
                try:
                    records_to_archive = []
                    now_str = str(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
                    for p in payments_list:
                        records_to_archive.append({
                            "original_id": p.get("id"),
                            "rider_code": p.get("rider_code", ""),
                            "rider_name": p.get("rider_name", ""),
                            "amount": p.get("amount", 0.0),
                            "date": str(p.get("date", "")),
                            "notes": p.get("notes", ""),
                            "deleted_at": now_str,
                        })

                    if records_to_archive:
                        supabase.table("deleted_payments").insert(records_to_archive).execute()

                    supabase.table("payments").delete().neq("id", 0).execute()
                    st.success("✅ تم مسح ونقل كافة التوريدات للأرشيف بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ أثناء المسح الشامل: {e}")

    st.divider()

    st.subheader("📋 التوريدات الحالية النشطة")
    if payments_list:
        df_p = pd.DataFrame(payments_list)
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

    # ==========================================
    # قسم أرشيف المحذوفات (مع الاسترجاع والحذف النهائي)
    # ==========================================
    st.subheader("🗑️ أرشيف المحذوفات (الاسترجاع أو الحذف النهائي)")
    deleted_list = get_deleted_payments()

    if deleted_list:
        del_options = {
            f"ID الأرشيف: {d.get('id')} | المندوب: {d.get('rider_name')} | المبلغ: {int(d.get('amount', 0)):,} ج.م | الحذف: {d.get('deleted_at', '')}": d
            for d in deleted_list
        }

        selected_del_str = st.selectbox(
            "اختر التوريد المحذوف للتحكم به:",
            list(del_options.keys()),
        )

        col_act1, col_act2, col_act3 = st.columns([2, 2, 1])

        with col_act1:
            if st.button("↩️ استرجاع التوريد المختار", type="primary"):
                item_to_restore = del_options[selected_del_str]
                del_id = item_to_restore.get("id")
                try:
                    supabase.table("payments").insert({
                        "rider_code": item_to_restore.get("rider_code", ""),
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
            if st.button("❌ حذف نهائي من الأرشيف", type="secondary"):
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
            if st.button("🔥 إفراغ الأرشيف"):
                try:
                    supabase.table("deleted_payments").delete().neq("id", 0).execute()
                    st.toast("🔥 تم مسح الأرشيف بالكامل", icon="🧹")
                    st.success("✅ تم إفراغ الأرشيف بالكامل بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ أثناء تفريغ الأرشيف: {e}")

        st.write("")
        df_del = pd.DataFrame(deleted_list)
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

# ==========================================
# الشاشة السادسة: تجميع مرتبات المناديب
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
        if st.button("🔥 مسح المرتبات المحفوظة"):
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
                selected_code_col = st.selectbox("عمود كود المندوب:", cols, index=cols.index(code_c))
            with col_sel2:
                selected_name_col = st.selectbox("عمود اسم المندوب:", cols, index=cols.index(name_c))
            with col_sel3:
                selected_sal_col = st.selectbox("عمود المرتب / المبلغ:", cols, index=cols.index(salary_c))
            with col_sel4:
                date_options = ["بدون تحديد / شهر واحد"] + cols
                default_date_idx = (cols.index(date_c) + 1) if date_c and date_c in cols else 0
                selected_date_col = st.selectbox("عمود التاريخ / الشهر (للتقسيم):", date_options, index=default_date_idx)

            df_sal["Salary_Clean"] = pd.to_numeric(
                df_sal[selected_sal_col].astype(str).str.replace(",", "").str.strip(), errors="coerce"
            ).fillna(0)

            df_sal["Code_Clean"] = df_sal[selected_code_col].astype(str).str.strip()
            df_sal["Name_Clean"] = df_sal[selected_name_col].astype(str).str.strip()

            if selected_date_col != "بدون تحديد / شهر واحد":
                df_sal["Parsed_Date"] = pd.to_datetime(df_sal[selected_date_col], errors="coerce")
                df_sal["Month_Year"] = df_sal["Parsed_Date"].dt.strftime("%Y-%m").fillna("غير محدد")
                group_cols = ["Month_Year", "Code_Clean", "Name_Clean"]
            else:
                group_cols = ["Code_Clean", "Name_Clean"]

            grouped_data = df_sal.groupby(group_cols, as_index=False)["Salary_Clean"].sum()

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
        )
    else:
        st.info("💡 لا يوجد شيت مرتبات محفوظ حالياً. قم برفع شيت مرتبات جديد للبدء.")
