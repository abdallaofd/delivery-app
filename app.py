import io
import json
import os
import re
import pandas as pd
import streamlit as st

# ==========================================
# 1. إعدادات الصفحة والتصميم الاحترافي المنسق
# ==========================================
st.set_page_config(
    page_title="نظام إدارة الداشبورد والتوريدات",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تطبيق CSS متقدم لتوسيق العناوين وتجميل العناصر
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* الخلفية العامة */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* العناوين الرئيسية المتمركزة في منتصف الصفحة */
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

    /* العناوين الفرعية لتكون في المنتصف ومحددة */
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
    
    /* تحسين وتوسيط البطاقات الإحصائية KPIs */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        border-radius: 12px;
        padding: 16px;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    
    div[data-testid="stMetric"] label {
        justify-content: center !important;
        font-weight: 700 !important;
        color: #64748b !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        justify-content: center !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }
    
    /* تحسين الأزرار */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        font-size: 15px;
        padding: 10px 24px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* أسلوب التنبيهات */
    .stAlert {
        border-radius: 10px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DB_FILE = "database.json"


# ==========================================
# 2. دوال إدارة قاعدة البيانات المحلية
# ==========================================
def load_db():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {"riders": [], "payments": []}


def save_db(db):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4)


db = load_db()


def clean_text(text):
  if pd.isna(text):
    return ""
  text = str(text).strip().lower()
  text = re.sub(r"\s+", " ", text)
  return text


def auto_register_rider(code, name):
  """تسجيل المندوب تلقائياً في قائمة المناديب إن لم يكن موجوداً"""
  if not name or str(name).strip() == "":
    return
  code_str = str(code).strip() if pd.notna(code) else ""
  name_str = str(name).strip()

  existing_riders = db.get("riders", [])
  exists = any(
      r.get("name") == name_str or (code_str and r.get("code") == code_str)
      for r in existing_riders
  )

  if not exists:
    db["riders"].append({"code": code_str, "name": name_str})
    save_db(db)


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
    ],
)

# ==========================================
# الشاشة الأولى: مطابقة الداشبورد اليومية
# ==========================================
if menu == "📊 مطابقة الداشبورد اليومية":
  st.markdown(
      """
    <div class="main-header">
        <h1>📊 مطابقة عهدة الداشبورد مع التوريدات الشهرية</h1>
        <p>متابعة عجز المناديب، صافي المستحقات، وحالات المغادرين بشكل مباشر ودقيق</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  c_up, c_rst = st.columns([4, 1])
  with c_up:
    dash_file = st.file_uploader(
        "📥 ارفع ملف الداشبورد الحالي (CSV أو Excel)",
        type=["csv", "xlsx", "xls"],
    )
  with c_rst:
    if "dash_df_processed" in st.session_state:
      st.write("")
      st.write("")
      if st.button("🔄 إزالة الملف"):
        del st.session_state["dash_df_processed"]
        st.rerun()

  if dash_file:
    try:
      if dash_file.name.endswith(".csv"):
        try:
          df_dash_raw = pd.read_csv(dash_file)
        except:
          dash_file.seek(0)
          df_dash_raw = pd.read_csv(dash_file, encoding="utf-8-sig")
      else:
        df_dash_raw = pd.read_excel(dash_file)

      dash_cols = df_dash_raw.columns.tolist()
      id_col = next(
          (
              c
              for c in dash_cols
              if "id" in str(c).lower() or "كود" in str(c).lower()
          ),
          dash_cols[0],
      )
      name_col_dash = next(
          (
              c
              for c in dash_cols
              if "name" in str(c).lower() or "اسم" in str(c).lower()
          ),
          dash_cols[1] if len(dash_cols) > 1 else dash_cols[0],
      )
      cod_col = next(
          (
              c
              for c in dash_cols
              if any(
                  k in str(c).lower()
                  for k in ["cod", "balance", "عهدة", "عجز", "مستحق"]
              )
          ),
          dash_cols[-1],
      )
      status_col = next(
          (
              c
              for c in dash_cols
              if "status" in str(c).lower() or "حالة" in str(c).lower()
          ),
          None,
      )
      vendor_col = next(
          (
              c
              for c in dash_cols
              if "vendor" in str(c).lower() or "شركة" in str(c).lower()
          ),
          None,
      )

      df_dash = df_dash_raw.dropna(subset=[name_col_dash]).copy()
      df_dash["Name_Clean"] = df_dash[name_col_dash].apply(clean_text)
      df_dash["COD_Balance"] = pd.to_numeric(
          df_dash[cod_col], errors="coerce"
      ).fillna(0)

      # تسجيل تلقائي للمناديب
      for _, r_item in df_dash.iterrows():
        auto_register_rider(r_item[id_col], r_item[name_col_dash])

      st.session_state["dash_df_processed"] = {
          "df_dash": df_dash,
          "id_col": id_col,
          "name_col_dash": name_col_dash,
          "cod_col": cod_col,
          "status_col": status_col,
          "vendor_col": vendor_col,
      }
    except Exception as e:
      st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

  if "dash_df_processed" in st.session_state:
    data_dict = st.session_state["dash_df_processed"]
    df_dash = data_dict["df_dash"]
    id_col = data_dict["id_col"]
    name_col_dash = data_dict["name_col_dash"]
    status_col = data_dict["status_col"]
    vendor_col = data_dict["vendor_col"]

    payments_list = db.get("payments", [])
    if payments_list:
      df_pay_db = pd.DataFrame(payments_list)
      df_pay_db["Name_Clean"] = df_pay_db["rider_name"].apply(clean_text)
      pay_sum = df_pay_db.groupby("Name_Clean")["amount"].sum().reset_index()
    else:
      pay_sum = pd.DataFrame(columns=["Name_Clean", "amount"])

    merged = pd.merge(
        df_dash,
        pay_sum.rename(columns={"amount": "Total_Paid"}),
        on="Name_Clean",
        how="left",
    )
    merged["Total_Paid"] = merged["Total_Paid"].fillna(0)
    merged["Remaining_Balance"] = merged["COD_Balance"] - merged["Total_Paid"]

    def categorize(row):
      cod = row["COD_Balance"]
      paid = row["Total_Paid"]
      rem = row["Remaining_Balance"]
      status = str(row[status_col]).lower() if status_col else ""

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
        "إجمالي عهدة الداشبورد", f"{merged['COD_Balance'].sum():,.2f} ج.م"
    )
    c2.metric(
        "إجمالي التوريدات المسجلة", f"{merged['Total_Paid'].sum():,.2f} ج.م"
    )
    c3.metric(
        "الصافي المطلوب تحصيله", f"{merged['Remaining_Balance'].sum():,.2f} ج.م"
    )
    c4.metric(
        "مناديب مغادرين بمديونية",
        f"{merged[merged['الحالة المالية'] == '⚠️ مغادر وعليه مديونية'].shape[0]} مندوب",
    )

    st.divider()

    status_filter = st.multiselect(
        "تصفية التقرير حسب الحالة المالية:",
        options=merged["الحالة المالية"].unique(),
        default=merged["الحالة المالية"].unique(),
    )
    filtered_df = merged[merged["الحالة المالية"].isin(status_filter)]

    display_cols = [id_col, name_col_dash]
    if status_col:
      display_cols.append(status_col)
    if vendor_col:
      display_cols.append(vendor_col)
    display_cols.extend(
        ["COD_Balance", "Total_Paid", "Remaining_Balance", "الحالة المالية"]
    )

    final_table = filtered_df[display_cols].copy()
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

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
      final_table.to_excel(writer, sheet_name="متابعة التوريدات", index=False)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
      st.download_button(
          label="📥 تحميل التقرير التفصيلي كملف Excel",
          data=output.getvalue(),
          file_name="تقرير_المتابعة_الفعلي.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          type="primary",
      )
  elif not dash_file:
    st.info("👈 يرجى رفع ملف الداشبورد لعرض الموقف المالي للمناديب.")

# ==========================================
# الشاشة الثانية: تسجيل توريد يومي
# ==========================================
elif menu == "➕ إضافة / تسجيل توريد يومي":
  st.markdown(
      """
    <div class="main-header">
        <h1>➕ تسجيل توريد جديد للمندوب</h1>
        <p>تسجيل المبالغ الموردة إما فردياً أو رفعة واحدة عن طريق شيت أكسيل</p>
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
    riders_data = db.get("riders", [])

    if not riders_data:
      st.warning("⚠️ لا يوجد مناديب مسجلين بعد.")
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
    amount = st.number_input("المبلغ المورد (ج.م):", min_value=0.0, step=50.0)
    notes = st.text_input("ملاحظات / رقم الإيصال (اختياري):")

    if st.button("💾 حفظ التوريد الفردي", type="primary"):
      if selected_rider_name and amount > 0:
        auto_register_rider(selected_rider_code, selected_rider_name)

        db["payments"].append({
            "rider_code": str(selected_rider_code),
            "rider_name": selected_rider_name,
            "date": str(pay_date),
            "amount": amount,
            "notes": notes if notes else "تعديل/إدخال يدوي",
        })
        save_db(db)
        st.success(
            f"✅ تم تسجيل توريد بمبلغ {amount} ج.م للمندوب"
            f" ({selected_rider_name}) بنجاح!"
        )
      else:
        st.error("يرجى إدخال البيانات ومبلغ أكبر من صفر.")

  with col2:
    st.markdown(
        "<div class='section-title'>2️⃣ رفع شيت توريدات (جملة)</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "الأعمدة المقبولة في الشيت: كود المندوب | الاسم | التاريخ | المبلغ |"
        " ملاحظات"
    )
    batch_file = st.file_uploader(
        "ارفع شيت التوريدات (Excel/CSV)",
        type=["xlsx", "xls", "csv"],
        key="batch",
    )

    if batch_file:
      if st.button("📥 استيراد التوريدات الآن", type="primary"):
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
                      for k in [
                          "name",
                          "اسم",
                          "الطيار",
                          "rider",
                          "driver",
                          "row labels",
                      ]
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
                          "مديونية",
                          "paid",
                          "amount",
                          "sum",
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
                  if "note" in str(c).lower()
                  or "ملاحظ" in str(c).lower()
                  or "إيصال" in str(c).lower()
                  or "ايصال" in str(c).lower()
              ),
              None,
          )

          count = 0
          for _, r in df_b.iterrows():
            if pd.notna(r[name_c]) and pd.notna(r[amount_c]):
              try:
                amt_val = float(
                    str(r[amount_c]).replace(",", "").strip()
                )
                r_name_val = str(r[name_c]).strip()
                r_code_val = str(r[code_c]).strip() if code_c else ""

                if date_c and pd.notna(r[date_c]):
                  r_date_val = str(
                      pd.to_datetime(r[date_c], errors="coerce").date()
                  )
                else:
                  r_date_val = str(pd.Timestamp.now().date())

                r_notes_val = (
                    str(r[notes_c]).strip()
                    if (notes_c and pd.notna(r[notes_c]))
                    else "استيراد ملف توريدات"
                )

                if amt_val > 0 and r_name_val:
                  # التسجيل التلقائي للمندوب
                  auto_register_rider(r_code_val, r_name_val)

                  # منع التكرار
                  duplicate = any(
                      p.get("rider_name") == r_name_val
                      and p.get("date") == r_date_val
                      and float(p.get("amount", 0)) == amt_val
                      and p.get("notes") == r_notes_val
                      for p in db["payments"]
                  )

                  if not duplicate:
                    db["payments"].append({
                        "rider_code": r_code_val,
                        "rider_name": r_name_val,
                        "date": r_date_val,
                        "amount": amt_val,
                        "notes": r_notes_val,
                    })
                    count += 1
              except ValueError:
                continue

          save_db(db)
          if count > 0:
            st.success(f"✅ تم استيراد {count} عملية توريد بنجاح دون أي تكرار!")
          else:
            st.info("ℹ️ جميع التوريدات المذكورة في الشيت مسجلة بالفعل سابقاً.")
        except Exception as e:
          st.error(f"خطأ في الاستيراد: {e}")

# ==========================================
# الشاشة الثالثة: إدارة أسماء المناديب
# ==========================================
elif menu == "👥 إدارة أسماء المناديب":
  st.markdown(
      """
    <div class="main-header">
        <h1>👥 إدارة بيانات المناديب الثابتة</h1>
        <p>يتم إضافة المناديب هنا تلقائياً بمجرد رفع أي شيت، ويمكنك الإضافة والتحكم يدوياً</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns(2)

  with col1:
    st.markdown(
        "<div class='section-title'>1️⃣ إضافة مندوب فردي</div>",
        unsafe_allow_html=True,
    )
    r_code = st.text_input("كود المندوب (ID):")
    r_name = st.text_input("اسم المندوب بالكامل:")
    if st.button("إضافة المندوب", type="primary"):
      if r_name:
        auto_register_rider(r_code, r_name)
        st.success("تمت إضافة المندوب بنجاح!")
        st.rerun()

  with col2:
    st.markdown(
        "<div class='section-title'>2️⃣ رفع شيت المناديب (جملة)</div>",
        unsafe_allow_html=True,
    )
    st.caption("شيت يحتوي على: (كود المندوب | اسم المندوب)")
    riders_file = st.file_uploader(
        "ارفع شيت المناديب", type=["xlsx", "xls", "csv"], key="riders_file"
    )
    if riders_file:
      if st.button("📥 حفظ كادر المناديب"):
        try:
          df_r = (
              pd.read_csv(riders_file)
              if riders_file.name.endswith(".csv")
              else pd.read_excel(riders_file)
          )
          cols = df_r.columns.tolist()

          code_col = next(
              (
                  c
                  for c in cols
                  if "id" in str(c).lower() or "كود" in str(c).lower()
              ),
              cols[0],
          )
          name_col = next(
              (
                  c
                  for c in cols
                  if "name" in str(c).lower() or "اسم" in str(c).lower()
              ),
              cols[1] if len(cols) > 1 else cols[0],
          )

          added_count = 0
          for _, row in df_r.iterrows():
            c_val = str(row[code_col]).strip() if pd.notna(row[code_col]) else ""
            n_val = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""

            if n_val:
              before = len(db.get("riders", []))
              auto_register_rider(c_val, n_val)
              after = len(db.get("riders", []))
              if after > before:
                added_count += 1

          st.success(f"✅ تم إضافة {added_count} مندوب جديد للقائمة!")
          st.rerun()
        except Exception as e:
          st.error(f"حدث خطأ أثناء قراءة شيت المناديب: {e}")

  st.divider()
  st.markdown(
      "<div class='section-title'>📋 قائمة المناديب المسجلة بالنظام</div>",
      unsafe_allow_html=True,
  )
  if db.get("riders"):
    df_riders_show = pd.DataFrame(db["riders"])
    df_riders_show.columns = ["كود المندوب", "اسم المندوب"]
    st.dataframe(df_riders_show, use_container_width=True, hide_index=True)

    col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
    with col_del2:
      if st.button("🗑️ مسح جميع المناديب المسجلين"):
        db["riders"] = []
        save_db(db)
        st.success("تم مسح القائمة.")
        st.rerun()
  else:
    st.info("لا يوجد مناديب مضافين حالياً.")

# ==========================================
# الشاشة الرابعة: سجل التوريدات
# ==========================================
elif menu == "📜 سجل التوريدات الشهرية":
  st.markdown(
      """
    <div class="main-header">
        <h1>📜 جميع التوريدات المسجلة هذا الشهر</h1>
        <p>سجل شامل بجميع الحركات والإيداعات المالية المسجلة ببياناتها الدقيقة</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  if db.get("payments"):
    df_p = pd.DataFrame(db["payments"])

    cols_order = ["rider_code", "rider_name", "date", "amount", "notes"]
    for col in cols_order:
      if col not in df_p.columns:
        df_p[col] = ""

    df_p = df_p[cols_order]

    rename_dict = {
        "rider_code": "كود المندوب",
        "rider_name": "اسم المندوب",
        "date": "التاريخ",
        "amount": "المبلغ المورد",
        "notes": "ملاحظات",
    }
    df_p.rename(columns=rename_dict, inplace=True)

    st.dataframe(df_p, use_container_width=True, hide_index=True)

    col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
    with col_del2:
      if st.button("🗑️ مسح جميع التوريدات (بدء شهر جديد)", type="secondary"):
        db["payments"] = []
        save_db(db)
        st.success("تم تفريغ السجل لبداية شهر جديد.")
        st.rerun()
  else:
    st.info("السجل فارغ حتى الآن.")