import io
import pandas as pd
import streamlit as st
from supabase import create_client

# ==========================================
# 1. إعدادات الاتصال بقاعدة البيانات السحابية (Supabase)
# ==========================================
SUPABASE_URL = "https://xoiwmchqsluhgygkfsvm.supabase.co"
SUPABASE_KEY = "sb_publishable_TVd6D2jmfePoUZq0QEn-jw_OI560HWH"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# دالة قراءة المناديب
def get_riders():
    try:
        res = supabase.table("riders").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

# دالة إدخال مناديب جدد
def save_riders(riders_list):
    if not riders_list:
        return
    existing = {str(r["code"]).strip(): r["name"] for r in get_riders()}
    new_entries = []
    for code, name in riders_list:
        str_code = str(code).strip()
        if str_code and str_code not in existing:
            new_entries.append({"code": str_code, "name": str(name).strip()})
    if new_entries:
        supabase.table("riders").insert(new_entries).execute()

# دالة حفظ التوريدات
def save_payments(payments_list):
    if payments_list:
        supabase.table("payments").insert(payments_list).execute()

# دالة جلب التوريدات
def get_payments():
    try:
        res = supabase.table("payments").select("*").execute()
        return res.data if res.data else []
    except Exception:
        return []

# دالة حفظ بيانات الداشبورد السحابية
def save_dashboard_data(df_dash):
    try:
        # مسح بيانات الداشبورد القديمة واحتفاظ بأحدث إصدار فقط
        supabase.table("dashboard_data").delete().neq("id", 0).execute()
        
        records = []
        for _, row in df_dash.iterrows():
            records.append({
                "rider_code": str(row['كود المندوب']).strip(),
                "rider_name": str(row.get('اسم المندوب', '')).strip(),
                "amount": float(row.get('العهدة / المستحق', 0)),
                "status": str(row.get('الحالة', '')).strip()
            })
        if records:
            supabase.table("dashboard_data").insert(records).execute()
    except Exception as e:
        st.error(f"خطأ في حفظ الداشبورد سحابياً: {e}")

# دالة جلب الداشبورد السحابي المحفوظ
def get_dashboard_data():
    try:
        res = supabase.table("dashboard_data").select("*").execute()
        if res.data:
            return pd.DataFrame(res.data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# ==========================================
# 2. إعدادات الصفحة والواجهة
# ==========================================
st.set_page_config(page_title="نظام إدارة الداشبورد والتوريدات", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("⚡ لوحة التحكم")
menu = st.sidebar.radio(
    "الانتقال إلى الشاشة:",
    ["📊 مطابقة الداشبورد اليومية", "➕ إضافة / تسجيل توريد يومي", "👥 إدارة أسماء المناديب", "📜 سجل التوريدات الشهري"]
)

# ==========================================
# 3. شاشة مطابقة الداشبورد
# ==========================================
if menu == "📊 مطابقة الداشبورد اليومية":
    st.markdown("<h2 style='text-align: center; color: #1E88E5;'>📊 مطابقة عهدة الداشبورد مع التوريدات السحابية</h2>", unsafe_allow_html=True)
    st.info("💡 البيانات المجهزة محفوظة سحابياً تلقائياً، ويمكنك تحديث شيت الداشبورد في أي وقت عند صدور شيت جديد.")

    uploaded_dash = st.file_uploader("📂 رفع ملف الداشبورد الجديد (اختياري للتحديث):", type=["csv", "xlsx", "xls"])
    
    # تحميل الداشبورد الحالي المحفوظ سحابياً أو الملف الجديد
    df_dash = pd.DataFrame()
    
    if uploaded_dash:
        try:
            if uploaded_dash.name.endswith('.csv'):
                df_dash = pd.read_csv(uploaded_dash)
            else:
                df_dash = pd.read_excel(uploaded_dash)
            
            # توحيد أسماء الأعمدة
            dash_code_col = [c for c in df_dash.columns if 'كود' in str(c) or 'code' in str(c).lower()]
            dash_amt_col = [c for c in df_dash.columns if 'مبلغ' in str(c) or 'عهدة' in str(c) or 'صافي' in str(c) or 'amount' in str(c).lower()]
            dash_name_col = [c for c in df_dash.columns if 'اسم' in str(c) or 'name' in str(c).lower()]
            dash_status_col = [c for c in df_dash.columns if 'حالة' in str(c) or 'status' in str(c).lower()]

            if dash_code_col and dash_amt_col:
                df_dash = df_dash.rename(columns={
                    dash_code_col[0]: 'كود المندوب',
                    dash_amt_col[0]: 'العهدة / المستحق'
                })
                if dash_name_col:
                    df_dash = df_dash.rename(columns={dash_name_col[0]: 'اسم المندوب'})
                if dash_status_col:
                    df_dash = df_dash.rename(columns={dash_status_col[0]: 'الحالة'})
                
                # حفظ في السحابة فوراً
                save_dashboard_data(df_dash)
                st.success("✅ تم تحديث وحفظ شيت الداشبورد الجديد سحابياً بنجاح!")
            else:
                st.error("❌ لم يتم التعرف على أعمدة الكود أو المبلغ في الشيت المرفوع.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
    else:
        # جلب البيانات من السحابة إذا لم يتم رفع ملف جديد
        cloud_dash = get_dashboard_data()
        if not cloud_dash.empty:
            df_dash = cloud_dash.rename(columns={
                'rider_code': 'كود المندوب',
                'rider_name': 'اسم المندوب',
                'amount': 'العهدة / المستحق',
                'status': 'الحالة'
            })

    # إجراء المطابقة وإظهار النتائج لو البيانات متوفرة
    if not df_dash.empty:
        df_dash['كود المندوب'] = df_dash['كود المندوب'].astype(str).str.strip()
        
        # حفظ أسماء المناديب الجدد أوتوماتيكياً
        if 'اسم المندوب' in df_dash.columns:
            new_riders = [(row['كود المندوب'], row['اسم المندوب']) for _, row in df_dash.iterrows() if pd.notna(row['اسم المندوب'])]
            save_riders(new_riders)

        # جلب التوريدات وحساب الإجمالي لكل مندوب
        payments_data = get_payments()
        if payments_data:
            df_pay = pd.DataFrame(payments_data)
            df_pay['rider_code'] = df_pay['rider_code'].astype(str).str.strip()
            pay_summary = df_pay.groupby('rider_code')['amount'].sum().reset_index()
            pay_summary.columns = ['كود المندوب', 'إجمالي المورد سحابياً']
        else:
            pay_summary = pd.DataFrame(columns=['كود المندوب', 'إجمالي المورد سحابياً'])

        # دمج الداشبورد مع التوريدات
        merged = pd.merge(df_dash, pay_summary, on='كود المندوب', how='left')
        merged['إجمالي المورد سحابياً'] = merged['إجمالي المورد سحابياً'].fillna(0)
        merged['الصافي المتبقي / العجز'] = merged['العهدة / المستحق'] - merged['إجمالي المورد سحابياً']

        # كروت الأداء Financial Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("إجمالي العهد المطلوب", f"{merged['العهدة / المستحق'].sum():,.2f} ج.م")
        col2.metric("إجمالي المورد بالسحابة", f"{merged['إجمالي المورد سحابياً'].sum():,.2f} ج.م", delta_color="normal")
        col3.metric("إجمالي المتبقي (العجز)", f"{merged['الصافي المتبقي / العجز'].sum():,.2f} ج.م", delta_color="inverse")
        
        migrated_count = 0
        if 'الحالة' in merged.columns:
            migrated_count = len(merged[merged['الحالة'].str.contains('مغادر|مستقيل|منقطع', na=False)])
        col4.metric("عدد المغادرين بمديونية", f"{migrated_count} مندوب")

        st.divider()
        st.subheader("📋 جدول مطابقة العُهد والتوريدات التفصيلي")
        st.dataframe(merged, use_container_width=True)
    else:
        st.warning("⚠️ لا توجد بيانات داشبورد محفوظة حالياً. يرجى رفع شيت الداشبورد أول مرة للحفظ في السحابة.")

# ==========================================
# 4. شاشة إضافة / تسجيل توريد يومي
# ==========================================
elif menu == "➕ إضافة / تسجيل توريد يومي":
    st.header("➕ تسجيل توريد جديد")
    
    tab1, tab2 = st.tabs(["📝 تسجيل فردي", "📂 رفع شيت توريدات بالجملة"])
    
    riders_data = get_riders()
    rider_options = {f"{r['code']} - {r['name']}": r['code'] for r in riders_data} if riders_data else {}

    with tab1:
        if not rider_options:
            st.warning("لا يوجد مناديب مسجلين، يرجى إضافة مناديب أو رفع شيت أولاً.")
        else:
            selected_rider_str = st.selectbox("اختر المندوب:", list(rider_options.keys()))
            rider_code = rider_options[selected_rider_str]
            rider_name = selected_rider_str.split(" - ")[1]
            
            pay_date = st.date_input("تاريخ التوريد:")
            amount = st.number_input("المبلغ المورد (ج.م):", min_value=0.0, step=50.0)
            notes = st.text_input("ملاحظات / رقم الإيصال:")

            if st.button("💾 حفظ التوريد السحابي", type="primary"):
                if amount > 0:
                    save_payments([{
                        "rider_code": str(rider_code),
                        "rider_name": rider_name,
                        "date": str(pay_date),
                        "amount": float(amount),
                        "notes": notes
                    }])
                    st.success(f"تم تسجيل توريد بمبلغ {amount} ج.م للمندوب {rider_name} بنجاح!")
                else:
                    st.error("يرجى إدخال مبلغ أكبر من الصفر.")

    with tab2:
        uploaded_pay = st.file_uploader("ارفع شيت التوريدات (Excel/CSV):", type=["csv", "xlsx", "xls"])
        if uploaded_pay:
            try:
                df_p = pd.read_csv(uploaded_pay) if uploaded_pay.name.endswith('.csv') else pd.read_excel(uploaded_pay)
                st.write("معاينة البيانات المرفوعة:", df_p.head())
                
                code_col = st.selectbox("اختر عمود كود المندوب:", df_p.columns)
                amt_col = st.selectbox("اختر عمود المبلغ:", df_p.columns)
                date_col = st.selectbox("اختر عمود التاريخ (إن وجد):", [None] + list(df_p.columns))
                
                if st.button("🚀 رفع التوريدات دفعة واحدة إلى السحابة"):
                    p_records = []
                    for _, row in df_p.iterrows():
                        p_records.append({
                            "rider_code": str(row[code_col]).strip(),
                            "rider_name": "",
                            "date": str(row[date_col]) if date_col and pd.notna(row[date_col]) else str(pd.Timestamp.now().date()),
                            "amount": float(row[amt_col]) if pd.notna(row[amt_col]) else 0.0,
                            "notes": "رفع بالجملة"
                        })
                    save_payments(p_records)
                    st.success("✅ تم حفظ جميع التوريدات في قاعدة البيانات السحابية بنجاح!")
            except Exception as e:
                st.error(f"خطأ في معالجة الملف: {e}")

# ==========================================
# 5. شاشة إدارة أسماء المناديب
# ==========================================
elif menu == "👥 إدارة أسماء المناديب":
    st.header("👥 أسماء المناديب المسجلين سحابياً")
    
    with st.form("add_rider_form"):
        c1, c2 = st.columns(2)
        new_code = c1.text_input("كود المندوب:")
        new_name = c2.text_input("اسم المندوب:")
        submit = st.form_submit_button("إضافة مندوب جديد")
        
        if submit and new_code and new_name:
            save_riders([(new_code, new_name)])
            st.success(f"تم إضافة المندوب {new_name} بنجاح!")

    riders_list = get_riders()
    if riders_list:
        st.dataframe(pd.DataFrame(riders_list), use_container_width=True)
    else:
        st.info("لا يوجد مناديب مسجلين حالياً.")

# ==========================================
# 6. شاشة سجل التوريدات الشهري
# ==========================================
elif menu == "📜 سجل التوريدات الشهري":
    st.header("📜 سجل التوريدات الموردة سحابياً")
    pay_data = get_payments()
    if pay_data:
        df_p = pd.DataFrame(pay_data)
        st.dataframe(df_p, use_container_width=True)
        st.metric("إجمالي التوريدات المسجلة", f"{df_p['amount'].sum():,.2f} ج.م")
    else:
        st.info("لا توجد توريدات مسجلة حتى الآن.")
