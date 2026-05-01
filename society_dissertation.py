import streamlit as st
import pandas as pd

st.set_page_config(page_title="学会発表・論文_教科書", layout="wide")

@st.cache_data
def load_all_data():
    EXCEL_FILE = "society_dissertation.xlsx"
    xl = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
    
    # 全シートを辞書形式で読み込む {シート名: DataFrame}
    data_dict = {}
    all_combined = [] # フィルタ選択肢作成用の全結合データ
    
    for name in xl.sheet_names:
        df_tmp = xl.parse(name)
        if "年度" in df_tmp.columns:
            df_tmp["年度"] = df_tmp["年度"].astype(str).str.replace(".0", "", regex=False)
        data_dict[name] = df_tmp
        all_combined.append(df_tmp[["年度", "事業所", "診療科"]].dropna(how='all'))
    
    # フィルタ用の全データ
    df_for_filter = pd.concat(all_combined, axis=0, ignore_index=True)
    
    return data_dict, df_for_filter

# データのロード
try:
    data_dict, df_filter_base = load_all_data()
    sheet_names = list(data_dict.keys())
except Exception as e:
    st.error(f"データの読み込みに失敗しました: {e}")
    st.stop()

st.title("学会発表・論文_教科書")

# --- 共通絞り込み検索（画面上部に配置） ---
st.write("### 共通絞り込み")
col1, col2, col3 = st.columns(3)

with col1:
    selected_years = st.multiselect(
        "年度を選択",
        options=sorted(df_filter_base["年度"].unique().tolist(), reverse=True)
    )
with col2:
    selected_offices = st.multiselect(
        "事業所を選択",
        options=sorted(df_filter_base["事業所"].unique().tolist())
    )
with col3:
    selected_depts = st.multiselect(
        "診療科を選択",
        options=sorted(df_filter_base["診療科"].dropna().unique().tolist())
    )

# --- タブの作成 ---
# シート名に基づいてタブを動的に作成
tabs = st.tabs(sheet_names)

for i, tab in enumerate(tabs):
    sheet_name = sheet_names[i]
    with tab:
        df_target = data_dict[sheet_name].copy()
        
        # フィルタリング適用
        if selected_years:
            df_target = df_target[df_target["年度"].isin(selected_years)]
        if selected_offices:
            df_target = df_target[df_target["事業所"].isin(selected_offices)]
        if selected_depts:
            df_target = df_target[df_target["診療科"].isin(selected_depts)]
            
        st.write(f"**{sheet_name}** のデータ: {len(df_target)} 件")
        
        # CSVダウンロードボタン（各タブ専用）
        csv = df_target.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 {sheet_name} をCSVで保存",
            data=csv,
            file_name=f'{sheet_name}_extracted.csv',
            key=f"btn_{i}" # タブごとにユニークなキーが必要
        )
        
        # データテーブル表示
        st.dataframe(df_target, use_container_width=True, hide_index=True)

st.markdown("""
    <style>
    div[data-testid="stDataFrame"] { font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)