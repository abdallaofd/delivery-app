import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(page_title="حساب إجمالي قبض المندوبين", layout="wide")

st.title("📊 تطبيق حساب إجمالي قبض المندوب (لأحدث شهر فقط)")

# رفع الملف
uploaded_file = st.file_uploader(
    "قم برفع ملف الاكسيل (Excel / CSV)", type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:
    try:
        # قراءة الملف
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("تم رفع الملف بنجاح!")

        # عرض التبويبات أو اختيار الشيت إذا كان الملف يحتوي على عدة شيتات
        st.subheader("📋 معاينة البيانات الأوليّة")
        st.dataframe(df.head())

        # التأكد من أسماء الأعمدة واستبدال المسافات لسهولة التعامل
        # نفترض هنا أن عمود التاريخ اسمه 'التاريخ' أو 'Date' أو 'F' وعمود المندوب اسمه 'اسم المندوب' وعمود المبلغ اسمه 'المبلغ' أو 'الصافي'
        # يمكنك اختيار الأعمدة من الواجهة إذا كانت أسمائها مختلفة

        st.markdown("---")
        st.subheader("⚙️ إعدادات الفلترة والحساب")

        col1, col2, col3 = st.columns(3)

        with col1:
            date_col = st.selectbox(
                "حدد عمود التاريخ:",
                options=df.columns,
                index=0 if "التاريخ" not in df.columns else df.columns.get_loc("التاريخ"),
            )

        with col2:
            agent_col = st.selectbox(
                "حدد عمود اسم المندوب / السائق:",
                options=df.columns,
                index=(
                    df.columns.get_loc("اسم المندوب")
                    if "اسم المندوب" in df.columns
                    else 0
                ),
            )

        with col3:
            amount_col = st.selectbox(
                "حدد عمود المبلغ / القبض:",
                options=df.columns,
                index=(
                    df.columns.get_loc("المبلغ")
                    if "المبلغ" in df.columns
                    else 0
                ),
            )

        # تحويل عمود التاريخ لتاريخ
        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", dayfirst=True
        )

        # استبعاد الصفوف التي لا تحتوي على تاريخ صحيح
        df_clean = df.dropna(subset=["_parsed_date"]).copy()

        if not df_clean.empty:
            # استخراج أحدث شهر وسنة موجودين في البيانات
            df_clean["_year_month"] = df_clean["_parsed_date"].dt.to_period("M")
            latest_period = df_clean["_year_month"].max()

            # عرض أحدث شهر تم العثور عليه
            st.info(
                f"📅 **أحدث شهر تم كشفه تلقائياً في الشيت:** {latest_period.strftime('%m-%Y')} (شهر {latest_period.month})"
            )

            # فلترة البيانات لأحدث شهر فقط
            df_latest_month = df_clean[
                df_clean["_year_month"] == latest_period
            ].copy()

            # تحويل المبلغ إلى أرقام
            df_latest_month[amount_col] = pd.to_numeric(
                df_latest_month[amount_col], errors="coerce"
            ).fillna(0)

            # حساب إجمالي قبض كل مندوب
            result_df = (
                df_latest_month.groupby(agent_col)[amount_col]
                .sum()
                .reset_index()
            )
            result_df.columns = [agent_col, f"إجمالي القبض ({latest_period.strftime('%m-%Y')})"]
            result_df = result_df.sort_values(
                by=f"إجمالي القبض ({latest_period.strftime('%m-%Y')})",
                ascending=False,
            )

            # عرض النتائج
            st.markdown("---")
            st.subheader(
                f"💰 إجمالي قبض المندوبين لشهر {latest_period.month} ({latest_period.year})"
            )

            st.dataframe(result_df, use_container_width=True)

            # ملخص سريع
            total_payout = result_df[
                f"إجمالي القبض ({latest_period.strftime('%m-%Y')})"
            ].sum()
            total_agents = result_df[agent_col].nunique()

            m1, m2 = st.columns(2)
            m1.metric("عدد المندوبين", f"{total_agents} مندوب")
            m2.metric("إجمالي المبالغ المطلوبة للشهر", f"{total_payout:,.2f} ج.م")

            # زر لتصدير النتيجة لملف إكسيل جاهز
            csv = result_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 تحميل تقرير قبض الشهر الأخير (CSV)",
                data=csv,
                file_name=f"قبض_شهر_{latest_period.month}_{latest_period.year}.csv",
                mime="text/csv",
            )
        else:
            st.warning(
                "لم يتم العثور على تواريخ صالحة في العمود المحدد، يرجى التأكد من اختيار عمود التاريخ الصحيح."
            )

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
