import streamlit as st
import os
import json
import shutil
import re
import base64

st.set_page_config(layout="wide", page_title="Rank-1 UPSC Command Center", page_icon="🏆")

# ----------------------------------------------------
# 📊 LOCAL HARD DRIVE STORAGE FILE ROUTING MAPPINGS
# ----------------------------------------------------
FOLDER_ID = "1nOHMq4Cliu8-8RggR6ncGZgFPRdKjZNU"

from googleapiclient.discovery import build
from google.oauth2 import service_account
import io
from googleapiclient.http import MediaIoBaseDownload

# Streamlit Secure Cloud Credentials Connection Layer
if "gcp_service_account" in st.secrets:
    creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    drive_service = build('drive', 'v3', credentials=creds)
else:
    st.error("Google Cloud Platform Credentials Key Missing from Streamlit Secrets Panel.")
    st.stop()

def cloud_download_json(filename, default_factory):
    try:
        results = drive_service.files().list(q=f"'{FOLDER_ID}' in parents and name='{filename}'", fields="files(id)").execute()
        files = results.get('files', [])
        if not files: return default_factory()
        request = drive_service.files().get_media(fileId=files[0]['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done: _, done = downloader.next_chunk()
        fh.seek(0)
        return json.loads(fh.read().decode('utf-8'))
    except Exception:
        return default_factory()

# Cloud Virtual File Path Definitions
TAXONOMY_JSON_PATH = "upsc_dynamic_taxonomy.json"
METADATA_JSON_PATH = "upsc_metadata_config.json"
INTERFACE_CONFIG_PATH = "upsc_interface_settings.json"
PRACTICE_CANVAS_PATH = "upsc_self_practice_canvas.json"
PYQ_DATABASE_PATH = "upsc_historical_pyqs.json"

os.makedirs(UNSORTED_STAGE_DIR, exist_ok=True)
os.makedirs(FINAL_SORTED_VAULT, exist_ok=True)

# ----------------------------------------------------
# 📂 DATA PERSISTENCE IO LAYER UTILITIES
# ----------------------------------------------------
def load_json_file(file_path, default_factory):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default_factory()
    return default_factory()

def save_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

if "taxonomy" not in st.session_state:
    st.session_state.taxonomy = load_json_file(TAXONOMY_JSON_PATH, lambda: {
        "GS_1": {
            "Geography": ["Oceanology", "Geomorphology", "Climatology"],
            "History": ["Modern_Indian_History", "Freedom_Struggle"],
            "Society": ["Indian_Social_Structure", "Women_Empowerment", "Caste", "Urbanisation"]
        },
        "GS_2": {"Polity": ["Executive", "Legislature", "Judiciary"], "Governance": ["E_Governance_Applications"]},
        "GS_3": {"Science_And_Technology": ["Nanotechnology_Robotics"], "Economy": ["Inclusive_Growth"]},
        "GS_4": {"Ethics_Theory": ["Human_Values_Essence"]}
    })

if "meta_tags" not in st.session_state:
    st.session_state.meta_tags = load_json_file(METADATA_JSON_PATH, lambda: {
        "flags": ["Standard_Review", "High_Yield_Diagram", "Excellent_Introduction", "Case_Study_Rich", "Weak_Needs_Rework"],
        "toppers": ["Zinnia_Arora", "Animesh_Pradhan", "Ishita_Kishore", "Anonymous_Topper"]
    })

if "practice_canvas" not in st.session_state:
    st.session_state.practice_canvas = load_json_file(PRACTICE_CANVAS_PATH, lambda: {})

if "pyq_database" not in st.session_state:
    st.session_state.pyq_database = load_json_file(PYQ_DATABASE_PATH, lambda: {
        "Oceanology": [
            {"year": "2024", "text": "Critically evaluate the impact of changing ocean currents on global marine ecosystems."},
            {"year": "2022", "text": "Discuss the environmental significance of the bioluminescence phenomenon in ocean waters."},
            {"year": "2019", "text": "How do ocean currents and water masses differ in their impacts on marine life and coastal climates?"}
        ],
        "Nanotechnology_Robotics": [
            {"year": "2023", "text": "Assess the application of nanotechnology in India's target healthcare sector transformation blueprint."},
            {"year": "2020", "text": "Discuss how artificial intelligence and robotics are poised to alter defensive warfare parameters."}
        ],
        "Caste": [
            {"year": "2025", "text": "Analyze how digital governance metrics are inadvertently restructuring traditional caste networks in rural blocks."},
            {"year": "2018", "text": "Is caste losing its relevance in understanding the socio-political fabric of modern urban spaces?"}
        ]
    })

raw_ui = load_json_file(INTERFACE_CONFIG_PATH, lambda: {})
ui = {
    "font_family": raw_ui.get("font_family", "Courier New"),
    "base_font_size": raw_ui.get("base_font_size", 16),
    "title_font_size": raw_ui.get("title_font_size", 36),
    "header_font_size": raw_ui.get("header_font_size", 24),
    "bg_color": raw_ui.get("bg_color", "#121214"),
    "text_color": raw_ui.get("text_color", "#E4E6EB"),
    "card_bg": raw_ui.get("card_bg", "#1E1E24"),
    "accent_color": raw_ui.get("accent_color", "#3A3F47"),
    "btn_bg": raw_ui.get("btn_bg", "#1E1E24"),
    "btn_text": raw_ui.get("btn_text", "#E4E6EB"),
    "secondary_panel_bg": raw_ui.get("secondary_panel_bg", "#1E1E24"),
    "border_radius": raw_ui.get("border_radius", 8),
    "global_scale_val": raw_ui.get("global_scale_val", 100)
}
st.session_state.ui_settings = ui

# ----------------------------------------------------
# 🎨 DYNAMIC FULL-APP CSS INJECTION
# ----------------------------------------------------
css_override = f"""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stSidebar"] {{
        font-family: '{ui["font_family"]}', monospace !important;
        font-size: {ui["base_font_size"]}px !important;
        color: {ui["text_color"]} !important;
        background-color: {ui["bg_color"]} !important;
    }}
    h1, h2, h3, h4, label, p, span, li, [data-testid="stMarkdownContainer"] p, [data-testid="stExpander"] p {{
        color: {ui["text_color"]} !important;
    }}
    [data-testid="stSidebarUserContent"] div[data-testid="stExpander"] {{
        background-color: {ui["card_bg"]} !important;
        border: 1px solid {ui["accent_color"]} !important;
        border_radius: {ui["border_radius"]}px !important;
    }}
    [data-testid="stSidebarUserContent"] div[data-testid="stExpander"] summary {{
        color: {ui["text_color"]} !important;
    }}
    div[data-testid="stExpander"] {{
        background-color: {ui["card_bg"]} !important;
        border-radius: {ui["border_radius"]}px !important;
        border: 1px solid {ui["accent_color"]} !important;
    }}
    div[data-testid="stVerticalBlock"] {{
        background-color: transparent !important;
    }}
    .stTabs [data-baseline] {{
        background-color: {ui["bg_color"]} !important;
    }}
    div[data-testid="stNotificationV2"] {{
        background-color: {ui["secondary_panel_bg"]} !important;
        color: {ui["text_color"]} !important;
        border: 1px solid {ui["accent_color"]} !important;
    }}
    input, select, textarea, div[data-baseweb="select"], div[data-baseweb="popover"] {{
        background-color: {ui["card_bg"]} !important;
        color: {ui["text_color"]} !important;
    }}
    .stButton>button {{
        border-radius: {ui["border_radius"]}px !important;
        background-color: {ui["btn_bg"]} !important;
        color: {ui["btn_text"]} !important;
        border: 1px solid {ui["accent_color"]} !important;
    }}
</style>
"""
st.markdown(css_override, unsafe_allow_html=True)

def get_all_vault_files():
    all_files = []
    if not os.path.exists(FINAL_SORTED_VAULT): return all_files
    for gs in os.listdir(FINAL_SORTED_VAULT):
        gs_path = os.path.join(FINAL_SORTED_VAULT, gs)
        if not os.path.isdir(gs_path): continue
        for sub in os.listdir(gs_path):
            sub_path = os.path.join(gs_path, sub)
            if not os.path.isdir(sub_path): continue
            for top in os.listdir(sub_path):
                top_path = os.path.join(sub_path, top)
                if not os.path.isdir(top_path): continue
                for file in os.listdir(top_path):
                    if file.endswith(".png"):
                        all_files.append({
                            "gs": gs, "subject": sub, "topic": top,
                            "filename": file, "full_path": os.path.join(top_path, file)
                        })
    return all_files

vault_dataset = get_all_vault_files()

paper_counts = {}
for p in st.session_state.taxonomy.keys():
    paper_counts[p] = 0

subject_counts = {}
topic_counts = {}

for entry in vault_dataset:
    p, s, t = entry["gs"], entry["subject"], entry["topic"]
    if p in paper_counts: paper_counts[p] += 1
    s_key = f"{p} || {s}"
    subject_counts[s_key] = subject_counts.get(s_key, 0) + 1
    t_key = f"{p} || {s} || {t}"
    topic_counts[t_key] = topic_counts.get(t_key, 0) + 1

# ----------------------------------------------------
# 🧠 RE-ENGINEERED 3-COLUMN UNIFIED CARD DISPATCHER (IMAGE + DATA + PRACTICE/PYQ)
# ----------------------------------------------------
def render_universal_topper_card(entry, component_id_prefix):
    file_title = entry["filename"]
    try:
        meta_parts = file_title.split("__Q_")
        header_meta = meta_parts[0]
        q_slug_text = meta_parts[1].replace(".png", "").replace("_", " ")
        topper_tag = re.search(r'\[(.*?)\]', header_meta).group(1)
        priority_flag = header_meta.split("]")[-1].split("__")[1]
        marks_match = re.search(r'__Marks_(.*?|.*?)($|__)', header_meta)
        marks_tag = marks_match.group(1).replace('_', ' ') if marks_match else ""
        notes_match = re.search(r'__Notes_(.*)', header_meta)
        notes_tag = notes_match.group(1).replace('_', ' ') if notes_match else ""
    except:
        topper_tag = "Topper_Copy"; priority_flag = "Standard_Review"; marks_tag = ""; notes_tag = ""; q_slug_text = file_title.replace(".png", "").replace("_", " ")

    with st.expander(f"✍️ Topper: {topper_tag.replace('_',' ')} | Tag: {priority_flag.replace('_',' ')} | {entry['topic'].replace('_',' ')}", expanded=False):
        left_canvas, mid_editor, right_practice = st.columns([5, 4, 4], gap="medium")
        
        with left_canvas:
            individual_fine_scale = st.slider("Fine-Scale Local Width (%)", 10, 100, 100, key=f"sz_{component_id_prefix}_{file_title}")
            composite_calculated_width = int(ui["global_scale_val"] * (individual_fine_scale / 100))
            
            html_image_wrapper = f"""
            <div style="width: 100%; text-align: center; overflow-x: auto; padding: 5px; background-color:#0A0A0C; border-radius:4px;">
                <img src="data:image/png;base64," style="width: {composite_calculated_width}%; max-width: 100%; height: auto; border-radius: {ui["border_radius"]}px; border: 1px solid {ui["accent_color"]};" />
            </div>
            """
            with open(entry["full_path"], "rb") as img_file:
                encoded_bytes = base64.b64encode(img_file.read()).decode()
                html_image_wrapper = html_image_wrapper.replace("data:image/png;base64,", f"data:image/png;base64,{encoded_bytes}")
            st.markdown(html_image_wrapper, unsafe_allow_html=True)
            
        with mid_editor:
            st.markdown("##### ✏️ Modify Asset Metadata Matrix")
            change_topper = st.text_input("Candidate Identity Label:", topper_tag.replace("_", " "), key=f"top_{component_id_prefix}_{file_title}")
            
            tag_c1, tag_c2 = st.columns(2)
            with tag_c1:
                usable_flags = st.session_state.meta_tags["flags"]
                flag_idx = usable_flags.index(priority_flag) if priority_flag in usable_flags else 0
                change_flag = st.selectbox("Strategy Focus Marking Tag:", usable_flags, index=flag_idx, key=f"flg_{component_id_prefix}_{file_title}")
            with tag_c2:
                change_marks = st.text_input("Evaluator Marks Metric Value:", marks_tag, key=f"mrk_{component_id_prefix}_{file_title}")
            
            change_question = st.text_area("Scanned Question Statement Text:", q_slug_text, height=90, key=f"qns_{component_id_prefix}_{file_title}")
            change_notes = st.text_area("Value-Addition Revision Internal Notes:", notes_tag, height=100, key=f"nts_{component_id_prefix}_{file_title}")
            
            path_c1, path_c2, path_c3 = st.columns(3)
            with path_c1:
                paper_options = list(st.session_state.taxonomy.keys())
                paper_idx = paper_options.index(entry["gs"]) if entry["gs"] in paper_options else 0
                mov_gs = st.selectbox("Shift Paper:", paper_options, index=paper_idx, key=f"mgs_{component_id_prefix}_{file_title}")
            with path_c2:
                subject_options = list(st.session_state.taxonomy.get(mov_gs, {}).keys()) if st.session_state.taxonomy.get(mov_gs, {}) else ["General_Topics"]
                sub_idx = subject_options.index(entry["subject"]) if entry["subject"] in subject_options else 0
                mov_sub = st.selectbox("Shift Subject:", subject_options, index=sub_idx, key=f"msb_{component_id_prefix}_{file_title}")
            with path_c3:
                micro_options = st.session_state.taxonomy.get(mov_gs, {}).get(mov_sub, []) if mov_sub in st.session_state.taxonomy.get(mov_gs, {}) else ["General_Subtopic"]
                top_idx = micro_options.index(entry["topic"]) if entry["topic"] in micro_options else 0
                mov_top = st.selectbox("Shift Microtheme:", micro_options, index=top_idx, key=f"mtp_{component_id_prefix}_{file_title}")
            
            st.markdown("###")
            btn_c1, btn_c2 = st.columns(2)
            with btn_c1:
                execute_update = st.button("💾 Commit Profile Matrix Changes", key=f"save_{component_id_prefix}_{file_title}", use_container_width=True, type="primary")
            with btn_c2:
                purge_sheet = st.button("🗑️ Purge Sheet Chunks From Disk", key=f"del_{component_id_prefix}_{file_title}", use_container_width=True)

        with right_practice:
            st.markdown("##### 🧠 Active Practice & Trend Linker")
            active_theme = entry["topic"]
            
            if active_theme in st.session_state.pyq_database and st.session_state.pyq_database[active_theme]:
                st.markdown(f"**📌 Relevant UPSC PYQ Trends for {active_theme.replace('_',' ')}:**")
                for pyq in st.session_state.pyq_database[active_theme]:
                    st.caption(f"📅 **{pyq['year']}**: {pyq['text']}")
            else:
                st.caption("ℹ️ No historical PYQ trend vectors loaded under this microtheme node block.")
                
            st.markdown("---")
            st.caption("📝 **My Structure Brainstorming Slate:**")
            p_key = f"canvas_{file_title}"
            existing_canvas_data = st.session_state.practice_canvas.get(p_key, {"intro": "", "diagram": "", "case_study": ""})
            
            pract_intro = st.text_input("My Introduction Hook Strategy:", value=existing_canvas_data.get("intro", ""), key=f"pr_int_{component_id_prefix}_{file_title}")
            pract_diag = st.text_input("My Structural Diagram Concept Outline:", value=existing_canvas_data.get("diagram", ""), key=f"pr_dia_{component_id_prefix}_{file_title}")
            pract_case = st.text_area("My Value-Addition Case Studies/Data Points:", value=existing_canvas_data.get("case_study", ""), height=70, key=f"pr_cas_{component_id_prefix}_{file_title}")
            
            if st.button("💾 Lock My Practice Frame Insights", key=f"btn_pr_{component_id_prefix}_{file_title}", use_container_width=True):
                st.session_state.practice_canvas[p_key] = {"intro": pract_intro, "diagram": pract_diag, "case_study": pract_case}
                save_json_file(PRACTICE_CANVAS_PATH, st.session_state.practice_canvas)
                st.toast("Practice blueprint logged to configuration disk arrays!")

        if execute_update:
            s_top = change_topper.strip().replace(" ", "_")
            s_flg = f"__{change_flag}"
            s_mrk = f"__Marks_{change_marks.strip().replace(' ', '_')}" if change_marks.strip() else ""
            s_nts = f"__Notes_{change_notes.strip().replace(' ', '_').replace('\n', '_')}" if change_notes.strip() else ""
            s_qns = change_question.strip().replace(" ", "_").replace('\n', '_')
            
            new_filename = f"[{s_top}]{s_flg}{s_mrk}{s_nts}__Q_{s_qns}.png"
            if len(new_filename) > 220: new_filename = new_filename[:210] + "...png"
            
            target_dir = os.path.join(FINAL_SORTED_VAULT, mov_gs, mov_sub, mov_top)
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(entry["full_path"], os.path.join(target_dir, new_filename))
            st.rerun()
        elif purge_sheet:
            os.remove(entry["full_path"])
            st.rerun()

# ----------------------------------------------------
# 🏁 APPLICATION TAB ROUTER LAYOUT
# ----------------------------------------------------
tab_repo_view, tab_topper_dossier, tab_system_metrics, tab_pyq_manager, tab_bulk_stager = st.tabs([
    "📚 Main Dynamic Syllabus Vault View",
    "✍️ Independent Topper Dossier Portal",
    "📊 Hierarchical Tree Analytics Tracker",
    "📜 UPSC Past Year Questions Bank",
    "📂 Native Staging File Uploader Area"
])

# ====================================================
# TAB 1: PRIMARY REPOSITORY GALLERY VIEW
# ====================================================
with tab_repo_view:
    ec_col1, ec_col2 = st.columns([3, 1])
    with ec_col1:
        st.markdown("### 📚 UPSC Core Syllabus Repository Gallery")
    with ec_col2:
        if st.button("📥 Generate Value-Addition Cheat Sheets", type="secondary", use_container_width=True):
            compendium_buffer = []
            for item in vault_dataset:
                if "__Notes_" in item["filename"]:
                    try:
                        notes_extracted = item["filename"].split("__Notes_")[1].split("__Q_")[0].replace("_", " ")
                        compendium_buffer.append(f"📌 [Paper: {item['gs']} | Subtopic: {item['topic']}]\n📝 Data Profile: {notes_extracted}\n")
                    except: continue
            if compendium_buffer:
                st.download_button("💾 Save Export Document", data="\n".join(compendium_buffer), file_name="UPSC_Mains_Value_Addition_CheatSheet.txt", use_container_width=True)
            else:
                st.toast("No notes marked in your vault folder layers to compile yet.")

    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        view_gs = st.selectbox("Filter GS Paper Room:", ["All GS Papers"] + list(st.session_state.taxonomy.keys()), key="r_gs")
    with v_col2:
        v_subs = ["All Subjects"] + list(st.session_state.taxonomy.get(view_gs, {}).keys()) if view_gs != "All GS Papers" else ["All Subjects"]
        view_sub = st.selectbox("Filter Core Subject Head:", v_subs, key="r_sub")
    with v_col3:
        v_topics = ["All Microthemes"] + st.session_state.taxonomy.get(view_gs, {}).get(view_sub, []) if (view_gs != "All GS Papers" and view_sub != "All Subjects") else ["All Microthemes"]
        view_topic = st.selectbox("Filter Syllabus Microtheme:", v_topics, key="r_top")
    with v_col4:
        view_flag = st.selectbox("Filter Value-Addition Strategy Flag:", ["All Strategy Flags"] + st.session_state.meta_tags["flags"], key="r_flg")

    st.markdown("---")

    filtered_vault = []
    for entry in vault_dataset:
        file_title = entry["filename"]
        try:
            meta_parts = file_title.split("__Q_")
            header_meta = meta_parts[0]
            priority_flag = header_meta.split("]")[-1].split("__")[1]
        except: priority_flag = "Standard_Review"
            
        if view_gs != "All GS Papers" and entry["gs"] != view_gs: continue
        if view_sub != "All Subjects" and entry["subject"] != view_sub: continue
        if view_topic != "All Microthemes" and entry["topic"] != view_topic: continue
        if view_flag != "All Strategy Flags" and priority_flag != view_flag: continue
        filtered_vault.append(entry)

    if not filtered_vault:
        st.info("📁 Active Directory Target Empty. No answer scripts match the selected filter configuration.")
    else:
        for entry in filtered_vault:
            render_universal_topper_card(entry, component_id_prefix="mainvault")

# ====================================================
# TAB 2: EXPLICIT 4-TIER FILTERING TOPPER DOSSIER PORTAL
# ====================================================
with tab_topper_dossier:
    st.markdown("### ✍️ Dedicated Candidate Evaluation Dossier Room")
    target_dossier_topper = st.selectbox("Select Target Topper Name Profile:", st.session_state.meta_tags["toppers"], key="dossier_top_select")
    
    td_col1, td_col2, td_col3, td_col4 = st.columns(4)
    with td_col1:
        doss_gs = st.selectbox("Dossier GS Paper Room:", ["All GS Papers"] + list(st.session_state.taxonomy.keys()), key="d_gs")
    with td_col2:
        d_subs = ["All Subjects"] + list(st.session_state.taxonomy.get(doss_gs, {}).keys()) if doss_gs != "All GS Papers" else ["All Subjects"]
        doss_sub = st.selectbox("Dossier Core Subject Head:", d_subs, key="d_sub")
    with td_col3:
        d_topics = ["All Microthemes"] + st.session_state.taxonomy.get(doss_gs, {}).get(doss_sub, []) if (doss_gs != "All GS Papers" and doss_sub != "All Subjects") else ["All Microthemes"]
        doss_topic = st.selectbox("Dossier Syllabus Microtheme:", d_topics, key="d_top")
    with td_col4:
        doss_flag = st.selectbox("Dossier Value-Addition Strategy Flag:", ["All Strategy Flags"] + st.session_state.meta_tags["flags"], key="d_flg")

    topper_isolated_vault = []
    for entry in vault_dataset:
        file_title = entry["filename"]
        try:
            t_tag = re.search(r'\[(.*?)\]', file_title).group(1)
            meta_parts = file_title.split("__Q_")
            priority_flag = meta_parts[0].split("]")[-1].split("__")[1]
            
            if t_tag.lower() != target_dossier_topper.strip().lower(): continue
            if doss_gs != "All GS Papers" and entry["gs"] != doss_gs: continue
            if doss_sub != "All Subjects" and entry["subject"] != doss_sub: continue
            if doss_topic != "All Microthemes" and entry["topic"] != doss_topic: continue
            if doss_flag != "All Strategy Flags" and priority_flag != doss_flag: continue
            
            topper_isolated_vault.append(entry)
        except: continue
            
    if not topper_isolated_vault:
        st.info(f"No records archived matching your 4-tier filter configuration profiles for candidate `{target_dossier_topper}`.")
    else:
        dossier_tree = {}
        for entry in topper_isolated_vault:
            g, s, t = entry["gs"], entry["subject"], entry["topic"]
            if g not in dossier_tree: dossier_tree[g] = {}
            if s not in dossier_tree[g]: dossier_tree[g][s] = {}
            if t not in dossier_tree[g][s]: dossier_tree[g][s][t] = []
            dossier_tree[g][s][t].append(entry)
            
        for d_gs in sorted(dossier_tree.keys()):
            with st.expander(f"📁 {d_gs.replace('_',' ')} — Workspace Room Nodes Active", expanded=True):
                for d_sub in sorted(dossier_tree[d_gs].keys()):
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;🗂️ **Core Subject Module Node:** `{d_sub.replace('_',' ')}`")
                    for d_top in sorted(dossier_tree[d_gs][d_sub].keys()):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🌿 **Syllabus Microtheme Target:** `{d_top.replace('_',' ')}`")
                        for entry in dossier_tree[d_gs][d_sub][d_top]:
                            render_universal_topper_card(entry, component_id_prefix="dossierportal")

# ====================================================
# TAB 3: MATRIX HEATMAP GENERATOR AND TRACKER TREE (SORTED + EXPANDERS)
# ====================================================
with tab_system_metrics:
    st.markdown("#### 🌲 Dynamic Global Matrix Coverage Index Node Map")
    
    sorted_papers_global = sorted(paper_counts.items(), key=lambda x: x[1], reverse=True)
    for p_name, p_count in sorted_papers_global:
        with st.expander(f"📁 {p_name.replace('_',' ')} — ({p_count} Total Elements)", expanded=False):
            p_subs = [s for s in subject_counts.keys() if s.startswith(p_name)]
            sorted_subs = sorted(p_subs, key=lambda x: subject_counts[x], reverse=True)
            for s_key in sorted_subs:
                s_name = s_key.split(" || ")[1]
                s_count = subject_counts.get(s_key, 0)
                with st.expander(f"📂 {s_name.replace('_',' ')} — ({s_count} Files Indexed)", expanded=False):
                    
                    # Pull microthemes dynamically from taxonomy to avoid missing empty ones
                    micros_in_sub = st.session_state.taxonomy.get(p_name, {}).get(s_name, [])
                    sorted_tops = sorted(micros_in_sub, key=lambda x: topic_counts.get(f"{p_name} || {s_name} || {x}", 0), reverse=True)
                    
                    for t_name in sorted_tops:
                        t_key = f"{p_name} || {s_name} || {t_name}"
                        t_val = topic_counts.get(t_key, 0)
                        
                        if t_val == 0: color_icon = "🔴 [HIGH GAP]"
                        elif t_val <= 2: color_icon = "🟡 [DEVELOPING]"
                        else: color_icon = "🟢 [MASTERED]"
                        
                        with st.expander(f"🌿 {color_icon} {t_name.replace('_',' ')} — ({t_val} copies active)", expanded=False):
                            theme_files = [e for e in vault_dataset if e["gs"] == p_name and e["subject"] == s_name and e["topic"] == t_name]
                            if theme_files:
                                for t_file in theme_files:
                                    render_universal_topper_card(t_file, component_id_prefix="metricstree")
                            else:
                                st.caption("ℹ️ No active files indexed under this syllabus node.")

# ====================================================
# TAB 4: DECOUPLED DYNAMIC PAST YEAR QUESTIONS ROOM (FOLDABLE + SORTED)
# ====================================================
with tab_pyq_manager:
    st.markdown("### 📜 UPSC Past Year Questions Comprehensive Bank")
    view_pane, insert_pane = st.columns([1, 1], gap="large")
    
    with view_pane:
        st.markdown("##### 🔍 Complete Syllabus Tree PYQ Index Explorer")
        
        sorted_papers_pyq = sorted(st.session_state.taxonomy.keys(), key=lambda x: sum(len(st.session_state.pyq_database.get(m, [])) for s in st.session_state.taxonomy[x] for m in st.session_state.taxonomy[x][s]), reverse=True)
        for paper_id in sorted_papers_pyq:
            with st.expander(f"📕 {paper_id.replace('_',' ')} Historical Trends", expanded=False):
                
                sorted_subjects_pyq = sorted(st.session_state.taxonomy[paper_id].keys(), key=lambda s: sum(len(st.session_state.pyq_database.get(m, [])) for m in st.session_state.taxonomy[paper_id][s]), reverse=True)
                for subject_id in sorted_subjects_pyq:
                    with st.expander(f"📁 {subject_id.replace('_',' ')}", expanded=False):
                        
                        sorted_micros_pyq = sorted(st.session_state.taxonomy[paper_id][subject_id], key=lambda m: len(st.session_state.pyq_database.get(m, [])), reverse=True)
                        for micro_id in sorted_micros_pyq:
                            questions_list = st.session_state.pyq_database.get(micro_id, [])
                            q_count = len(questions_list)
                            
                            with st.expander(f"🌿 `{micro_id.replace('_',' ')}` — ({q_count} Questions Loaded)", expanded=False):
                                if q_count > 0:
                                    for idx, q_data in enumerate(questions_list):
                                        col_txt, col_btn = st.columns([5, 1])
                                        with col_txt:
                                            st.markdown(f"📅 **{q_data['year']}**: {q_data['text']}")
                                        with col_btn:
                                            if st.button("🗑️ Prune", key=f"del_bank_{micro_id}_{idx}"):
                                                st.session_state.pyq_database[micro_id].pop(idx)
                                                save_json_file(PYQ_DATABASE_PATH, st.session_state.pyq_database)
                                                st.rerun()
                                else:
                                    st.caption("❌ No historical questions logged under this microtheme yet.")

    with insert_pane:
        st.markdown("##### ➕ Manual PYQ Question Inserter Core")
        in_pyq_gs = st.selectbox("Assign Target Paper:", list(st.session_state.taxonomy.keys()), key="in_pyq_gs")
        in_pyq_sub = st.selectbox("Assign Subject Category:", list(st.session_state.taxonomy[in_pyq_gs].keys()) if st.session_state.taxonomy[in_pyq_gs] else ["General_Topics"], key="in_pyq_sub")
        in_pyq_top = st.selectbox("Assign Syllabus Microtheme Node:", st.session_state.taxonomy[in_pyq_gs].get(in_pyq_sub, []) if in_pyq_sub in st.session_state.taxonomy[in_pyq_gs] else ["General_Subtopic"], key="in_pyq_top")
        
        in_pyq_year = st.text_input("Enter Question Exam Year Parameters (e.g., 2024):", placeholder="2026")
        in_pyq_text = st.text_area("Type Complete Official UPSC Exam Question Text String:")
        
        if st.button("💾 Append & Sync Question to PYQ Bank", type="primary", use_container_width=True):
            if in_pyq_year and in_pyq_text and in_pyq_top:
                if in_pyq_top not in st.session_state.pyq_database:
                    st.session_state.pyq_database[in_pyq_top] = []
                st.session_state.pyq_database[in_pyq_top].insert(0, {"year": in_pyq_year.strip(), "text": in_pyq_text.strip()})
                save_json_file(PYQ_DATABASE_PATH, st.session_state.pyq_database)
                st.success("Past Year Question synchronized cleanly across repository systems!")
                st.rerun()

# ====================================================
# TAB 5: BULK STAGER DROP ZONE
# ====================================================
with tab_bulk_stager:
    st.markdown("### 📥 Fast Loose Image Drop Utility Zone")
    st.caption("Drop stray png crops right from your local desktop arrays into the pending queue directory instantly.")
    
    manual_raw_upload = st.file_uploader("Upload Fragment Images:", type=["png"], accept_multiple_files=True)
    assigned_manual_title = st.text_input("Assign Target Question Sentence/Keywords for Uploaded Files:")
    
    if st.button("⚡ Inject Into Active Sorter Queue Pipeline") and manual_raw_upload and assigned_manual_title:
        clean_manual_title = assigned_manual_title.strip().replace(" ", "_")
        for file_img in manual_raw_upload:
            out_dest_p = os.path.join(UNSORTED_STAGE_DIR, f"{clean_manual_title}_Source_ManualDesktopDrop.png")
            with open(out_dest_p, "wb") as f_out:
                f_out.write(file_img.read())
        st.success("Assets transferred into active staging slots.")
        st.rerun()

# ====================================================
# 🛠️ UTILITY QUEUE STAGING AREA UTILITIES
# ====================================================
st.markdown("### ---")
st.markdown("### 🛠️ Secondary System Utilities Dashboard")
util_sorter_tab, = st.tabs(["📥 Active Queue Sorter Linker Panel"])

with util_sorter_tab:
    staging_files = [f for f in os.listdir(UNSORTED_STAGE_DIR) if f.endswith(".png")]
    if not staging_files: st.info("🎉 Staging Queue Clear! No unsorted chunks left to process.")
    else:
        current_target_file = staging_files[0]
        display_question_sentence = current_target_file.split("_Source_")[0].replace("_", " ") if "_Source_" in current_target_file else current_target_file.replace(".png","").replace("_"," ")
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.info(f"**📝 Question Statement Text:**\n\n{display_question_sentence}")
            st.image(os.path.join(UNSORTED_STAGE_DIR, current_target_file), use_container_width=True)
        with col2:
            st.markdown("##### Manual Routing Parameters")
            gs_paper = st.selectbox("1. Assign GS Paper Partition:", list(st.session_state.taxonomy.keys()), key="s_gs_p")
            subject_head = st.selectbox("2. Assign Subject Head Category:", list(st.session_state.taxonomy[gs_paper].keys()) if st.session_state.taxonomy[gs_paper] else ["General_Topics"], key="s_sub_h")
            microtheme_topic = st.selectbox("3. Route to Syllabus Microtheme:", st.session_state.taxonomy[gs_paper].get(subject_head, []) if subject_head in st.session_state.taxonomy[gs_paper] else ["General_Subtopic"], key="s_mic_t")
            topper_name = st.selectbox("✍️ *Assign Candidate Identity Profile:*", st.session_state.meta_tags["toppers"], key="s_top_n")
            marks_value = st.text_input("📊 Score Achieved on this Answer (Optional):", key="s_marks")
            revision_tag = st.selectbox("🔥 Core Value-Addition Priority Flag:", st.session_state.meta_tags["flags"], key="s_flag")
            custom_study_notes = st.text_area("📝 Append Custom Value-Addition Study Notes:", key="s_notes")
            
            if st.button("📥 Commit Custom Metadata Routing Path", type="primary", use_container_width=True, key="commit_stage_btn"):
                c_top = topper_name.strip().replace(" ", "_")
                c_mrk = f"__Marks_{marks_value.strip().replace(' ', '_')}" if marks_value else ""
                c_flg = f"__{revision_tag}"
                c_nts = f"__Notes_{custom_study_notes.strip().replace(' ', '_').replace('\n', '_')}" if custom_study_notes.strip() else ""
                c_slug = current_target_file.split("_Source_")[0] if "_Source_" in current_target_file else current_target_file.replace(".png","")
                
                final_name = f"[{c_top}]{c_flg}{c_mrk}{c_nts}__Q_{c_slug}.png"
                t_dir = os.path.join(FINAL_SORTED_VAULT, gs_paper, subject_head, microtheme_topic)
                os.makedirs(t_dir, exist_ok=True)
                shutil.copy2(os.path.join(UNSORTED_STAGE_DIR, current_target_file), os.path.join(t_dir, final_name))
                os.remove(os.path.join(UNSORTED_STAGE_DIR, current_target_file))
                st.rerun()

# ----------------------------------------------------
# 🗤 SIDEBAR PARAMETERS PANEL (WITH SEARCH & ADMIN METADATA CONSOLE)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🔎 Interactive Platform Search")
    search_q = st.text_input("Search anything across vault matrix...")
    filter_mode = st.selectbox("Search Target Scope Filter:", ["All Fields", "Topper Name", "Value-Addition Notes", "Question Text", "Paper Room", "Microtheme Node"])
    
    if search_q:
        st.markdown("#### 🎯 Clickable Search Matches:")
        search_hits = 0
        for item in vault_dataset:
            f_title = item["filename"]
            try:
                meta_parts = f_title.split("__Q_")
                h_meta = meta_parts[0]
                q_text = meta_parts[1].replace(".png", "").replace("_", " ")
                cand_name = re.search(r'\[(.*?)\]', h_meta).group(1).replace("_", " ")
                v_notes = h_meta.split("__Notes_")[1].split("__Q_")[0].replace("_", " ") if "__Notes_" in h_meta else ""
            except:
                cand_name = "Topper Copy"; q_text = f_title.replace(".png", ""); v_notes = ""
            
            is_match = False
            s_term = search_q.lower()
            
            if filter_mode == "All Fields":
                is_match = (s_term in f_title.lower() or s_term in item["gs"].lower() or s_term in item["topic"].lower())
            elif filter_mode == "Topper Name":
                is_match = (s_term in cand_name.lower())
            elif filter_mode == "Value-Addition Notes":
                is_match = (s_term in v_notes.lower())
            elif filter_mode == "Question Text":
                is_match = (s_term in q_text.lower())
            elif filter_mode == "Paper Room":
                is_match = (s_term in item["gs"].lower() or s_term in item["subject"].lower())
            elif filter_mode == "Microtheme Node":
                is_match = (s_term in item["topic"].lower())
                
            if is_match:
                search_hits += 1
                if st.button(f"🔗 [{item['gs']}] {cand_name} - {item['topic'].replace('_',' ')}", key=f"sidebar_sh_{f_title}_{search_hits}"):
                    st.toast("Opening asset data context matrix...")
                    render_universal_topper_card(item, component_id_prefix="sidebar_search_popup")
                    
        if search_hits == 0:
            st.caption("ℹ️ No parameters matching query patterns.")
            
    # ====================================================
    # 🛠️ NEW: CENTRAL SYLLABUS & METADATA PARAMETERS CONSOLE
    # ====================================================
    st.markdown("---")
    with st.expander("🛠️ Syllabus Core Taxonomy Admin Console", expanded=False):
        st.markdown("🔧 **Modify GS Papers & Custom Core Options**")
        
        # Section A: Manage GS Papers
        p_op = st.selectbox("Select Target GS Paper Architecture:", list(st.session_state.taxonomy.keys()), key="adm_p_sel")
        new_paper_name = st.text_input("Create New GS Paper Code Node Name:", placeholder="GS_5_Optional")
        if st.button("➕ Append New GS Paper Room", use_container_width=True):
            if new_paper_name.strip():
                clean_p = new_paper_name.strip().replace(" ", "_")
                if clean_p not in st.session_state.taxonomy:
                    st.session_state.taxonomy[clean_p] = {}
                    save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
                    st.success(f"Added paper room: {clean_p}")
                    st.rerun()

        if st.button("🗑️ Delete Selected GS Paper Architecture Room", use_container_width=True):
            if len(st.session_state.taxonomy.keys()) > 1:
                st.session_state.taxonomy.pop(p_op)
                save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
                st.warning(f"Purged paper structural entry: {p_op}")
                st.rerun()
                
        st.markdown("---")
        # Section B: Manage Subject Head Categories
        st.markdown(f"📂 **Manage Subject Heads inside `{p_op}`**")
        current_subjects = list(st.session_state.taxonomy.get(p_op, {}).keys())
        sub_op = st.selectbox("Select Target Subject Category Head:", current_subjects if current_subjects else ["None Active"], key="adm_s_sel")
        
        new_sub_name = st.text_input("Create New Subject Head Classification Label:", placeholder="International_Relations")
        if st.button("➕ Append New Subject Head Category", use_container_width=True):
            if new_sub_name.strip() and p_op:
                clean_s = new_sub_name.strip().replace(" ", "_")
                if clean_s not in st.session_state.taxonomy[p_op]:
                    st.session_state.taxonomy[p_op][clean_s] = []
                    save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
                    st.success(f"Added classification module: {clean_s}")
                    st.rerun()

        if sub_op != "None Active" and st.button("🗑️ Delete Selected Subject Head Category", use_container_width=True):
            st.session_state.taxonomy[p_op].pop(sub_op)
            save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
            st.warning(f"Purged category entry: {sub_op}")
            st.rerun()
            
        st.markdown("---")
        # Section C: Manage Microtheme Identity Profiles
        st.markdown(f"🌿 **Manage Microthemes inside `{sub_op}`**")
        current_microthemes = st.session_state.taxonomy.get(p_op, {}).get(sub_op, []) if sub_op != "None Active" else []
        micro_op = st.selectbox("Select Target Syllabus Microtheme Node:", current_microthemes if current_microthemes else ["None Active"], key="adm_m_sel")
        
        new_micro_name = st.text_input("Create New Specific Syllabus Microtheme Target Name:", placeholder="Bilateral_Groupings")
        if st.button("➕ Append New Syllabus Microtheme Node Target", use_container_width=True):
            if new_micro_name.strip() and p_op and sub_op != "None Active":
                clean_m = new_micro_name.strip().replace(" ", "_")
                if clean_m not in st.session_state.taxonomy[p_op][sub_op]:
                    st.session_state.taxonomy[p_op][sub_op].append(clean_m)
                    save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
                    st.success(f"Added target node: {clean_m}")
                    st.rerun()

        if micro_op != "None Active" and st.button("🗑️ Delete Selected Syllabus Microtheme Node Target", use_container_width=True):
            st.session_state.taxonomy[p_op][sub_op].remove(micro_op)
            save_json_file(TAXONOMY_JSON_PATH, st.session_state.taxonomy)
            st.warning(f"Purged target entry: {micro_op}")
            st.rerun()

    with st.expander("📋 Candidate Profiles & Priority Flags Configuration Admin", expanded=False):
        # Section D: Manage Candidate Profiles (Toppers)
        st.markdown("👤 **Manage Topper Profiles**")
        topper_op = st.selectbox("Select Registered Candidate Profile Identity:", st.session_state.meta_tags["toppers"], key="adm_t_sel")
        new_topper_name = st.text_input("Register New Topper Profile Candidate Identity Label Name:", placeholder="Shruti_Sharma")
        if st.button("➕ Register New Topper Profile Identity", use_container_width=True):
            if new_topper_name.strip():
                clean_t = new_topper_name.strip().replace(" ", "_")
                if clean_t not in st.session_state.meta_tags["toppers"]:
                    st.session_state.meta_tags["toppers"].append(clean_t)
                    save_json_file(METADATA_JSON_PATH, st.session_state.meta_tags)
                    st.success(f"Registered identity: {clean_t}")
                    st.rerun()
        if st.button("🗑️ Deregister Selected Topper Identity Profile", use_container_width=True):
            if len(st.session_state.meta_tags["toppers"]) > 1:
                st.session_state.meta_tags["toppers"].remove(topper_op)
                save_json_file(METADATA_JSON_PATH, st.session_state.meta_tags)
                st.warning(f"Purged registration: {topper_op}")
                st.rerun()

        st.markdown("---")
        # Section E: Manage Core Value-Addition Priority Flags
        st.markdown("🔥 **Manage Strategy Flags**")
        flag_op = st.selectbox("Select Focus Strategy Marking Tag Flag:", st.session_state.meta_tags["flags"], key="adm_f_sel")
        new_flag_name = st.text_input("Create New Custom Operational Strategy Tag Focus Label Flag Name:", placeholder="Data_Rich_Map")
        if st.button("➕ Create New Operational Strategy Tag Focus Label Flag", use_container_width=True):
            if new_flag_name.strip():
                clean_f = new_flag_name.strip().replace(" ", "_")
                if clean_f not in st.session_state.meta_tags["flags"]:
                    st.session_state.meta_tags["flags"].append(clean_f)
                    save_json_file(METADATA_JSON_PATH, st.session_state.meta_tags)
                    st.success(f"Generated priority label configuration flag: {clean_f}")
                    st.rerun()
        if st.button("🗑️ Delete Selected Strategy Priority Configuration Flag", use_container_width=True):
            if len(st.session_state.meta_tags["flags"]) > 1:
                st.session_state.meta_tags["flags"].remove(flag_op)
                save_json_file(METADATA_JSON_PATH, st.session_state.meta_tags)
                st.warning(f"Purged priority label configuration flag: {flag_op}")
                st.rerun()

    st.markdown("---")
    with st.expander("🎨 Master UI Color Scheme Configurator (Everything)", expanded=False):
        ui["bg_color"] = st.color_picker("App Background Layer Color:", ui["bg_color"])
        ui["text_color"] = st.color_picker("Typography & Labels Layer Color:", ui["text_color"])
        ui["card_bg"] = st.color_picker("Container Card Module Surface Color:", ui["card_bg"])
        ui["accent_color"] = st.color_picker("Active Structural Borders Color:", ui["accent_color"])
        ui["btn_bg"] = st.color_picker("Interactive Buttons Surface Color:", ui["btn_bg"])
        ui["btn_text"] = st.color_picker("Interactive Buttons Label Typography Color:", ui["btn_text"])
        ui["secondary_panel_bg"] = st.color_picker("Dossier Workspace Panels:", ui["secondary_panel_bg"])
        
        if st.button("💾 Lock Dynamic Colors", use_container_width=True, key="save_colors_btn"):
            save_json_file(INTERFACE_CONFIG_PATH, ui)
            st.rerun()

    with st.expander("⚙️ UI Typography Style & Dimension Customizer", expanded=False):
        font_options = ["Courier New", "Segoe UI", "Arial", "Roboto", "Georgia"]
        default_font_idx = font_options.index(ui["font_family"]) if ui["font_family"] in font_options else 0
        ui["font_family"] = st.selectbox("Global Text Font Face Style:", font_options, index=default_font_idx)
        
        ui["base_font_size"] = st.slider("Body Text Font Size (px):", 12, 24, ui["base_font_size"])
        ui["title_font_size"] = st.slider("Dashboard Main Title Size (px):", 24, 60, ui["title_font_size"])
        ui["header_font_size"] = st.slider("Section Headers Font Size (px):", 18, 40, ui["header_font_size"])
        ui["border_radius"] = st.slider("Card Border Corner Radius (px):", 0, 24, ui["border_radius"])
        
        st.markdown("---")
        ui["global_scale_val"] = st.slider("🎛️ Global Master Sheet Size Scale Override (%)", 10, 100, ui["global_scale_val"], key="master_scale_slider_sidebar")
        
        if st.button("💾 Apply & Lock Global Configurations", use_container_width=True, key="save_typo_btn"):
            save_json_file(INTERFACE_CONFIG_PATH, ui)
            st.rerun()