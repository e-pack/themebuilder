import streamlit as st
import json
import colorsys
from copy import deepcopy

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Power BI Theme Builder",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; margin-top: 1rem !important; }
    h3 { font-size: 1.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-size: 0.85rem;
    }
    div[data-testid="stExpander"] summary {
        font-size: 0.95rem;
        font-weight: 600;
    }
    .color-swatch {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        border: 1px solid #ccc;
        vertical-align: middle;
        margin-right: 6px;
    }
    .preview-card {
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 16px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def lighten(hex_color: str, factor: float = 0.3) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return rgb_to_hex(r, g, b)


def darken(hex_color: str, factor: float = 0.3) -> str:
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return rgb_to_hex(r, g, b)


def desaturate(hex_color: str, factor: float = 0.3) -> str:
    r, g, b = [x / 255.0 for x in hex_to_rgb(hex_color)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = max(0, s * (1 - factor))
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
    return rgb_to_hex(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def generate_palette(primary: str, count: int = 8) -> list:
    """Generate a harmonious palette from a primary color."""
    colors = [primary]
    colors.append(darken(primary, 0.35))
    colors.append(lighten(primary, 0.3))
    colors.append(desaturate(primary, 0.4))
    r, g, b = [x / 255.0 for x in hex_to_rgb(primary)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    for offset in [0.08, -0.08, 0.17]:
        h2 = (h + offset) % 1.0
        r2, g2, b2 = colorsys.hsv_to_rgb(h2, s * 0.85, v * 0.9)
        colors.append(rgb_to_hex(int(r2 * 255), int(g2 * 255), int(b2 * 255)))
    colors.append(darken(primary, 0.55))
    return colors[:count]


def color_fill(hex_color: str) -> dict:
    return {"solid": {"color": hex_color}}


def render_swatch_row(colors: list, labels: list = None):
    html = '<div style="display:flex; gap:6px; flex-wrap:wrap; margin:4px 0;">'
    for i, c in enumerate(colors):
        label = labels[i] if labels and i < len(labels) else c
        html += (
            f'<div style="text-align:center;">'
            f'<div style="width:48px;height:48px;background:{c};border-radius:6px;'
            f'border:1px solid #ccc;"></div>'
            f'<div style="font-size:10px;color:#666;margin-top:2px;">{label}</div>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Default theme state
# ─────────────────────────────────────────────
DEFAULT_THEME = {
    "name": "Custom Theme",
    "dataColors": ["#118DFF", "#12239E", "#E66C37", "#6B007B", "#E044A7", "#744EC2", "#D9B300", "#D64550"],
    "background": "#FFFFFF",
    "foreground": "#252423",
    "tableAccent": "#118DFF",
    "firstLevelElements": "#252423",
    "secondLevelElements": "#605E5C",
    "thirdLevelElements": "#F3F2F1",
    "fourthLevelElements": "#B3B0AD",
    "secondaryBackground": "#C8C6C4",
    "good": "#2E8B57",
    "neutral": "#D9B300",
    "bad": "#D64554",
    "maximum": "#118DFF",
    "center": "#D9B300",
    "minimum": "#DEEFFF",
    "null": "#FF7F48",
    "textClasses": {
        "callout": {"fontSize": 28, "fontFace": "Segoe UI", "color": "#252423"},
        "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#252423"},
        "header": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#252423"},
        "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": "#252423"},
    },
    "visualStyles": {},
}

FONT_OPTIONS = [
    "Segoe UI", "Segoe UI Semibold", "Segoe UI Bold", "Segoe UI Light",
    "Arial", "Calibri", "Cambria", "Consolas", "Courier New",
    "DIN", "Georgia", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana",
]

VISUAL_TYPES = [
    ("lineChart", "Line Chart"),
    ("clusteredBarChart", "Clustered Bar"),
    ("clusteredColumnChart", "Clustered Column"),
    ("barChart", "Stacked Bar"),
    ("columnChart", "Stacked Column"),
    ("areaChart", "Area Chart"),
    ("lineClusteredColumnComboChart", "Line & Clustered Column Combo"),
    ("lineStackedColumnComboChart", "Line & Stacked Column Combo"),
    ("pieChart", "Pie Chart"),
    ("donutChart", "Donut Chart"),
    ("waterfallChart", "Waterfall"),
    ("funnel", "Funnel"),
    ("scatterChart", "Scatter Chart"),
    ("treemap", "Treemap"),
    ("map", "Map"),
    ("filledMap", "Filled Map"),
    ("gauge", "Gauge"),
    ("kpi", "KPI"),
    ("card", "Card (Legacy)"),
    ("cardVisual", "Card (New)"),
    ("multiRowCard", "Multi-Row Card"),
    ("tableEx", "Table"),
    ("pivotTable", "Matrix"),
    ("slicer", "Slicer"),
    ("shape", "Shape"),
    ("image", "Image"),
    ("textbox", "Textbox"),
]

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = deepcopy(DEFAULT_THEME)

theme = st.session_state.theme


# ─────────────────────────────────────────────
# Sidebar — Import / Export / Reset
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🎨 Power BI Theme Builder")
    st.caption("Build, customize, and export Power BI theme JSON files.")

    st.divider()

    # Import existing theme
    st.subheader("Import Theme")
    uploaded = st.file_uploader("Upload a .json theme file", type=["json"], key="upload")
    if uploaded is not None:
        try:
            imported = json.loads(uploaded.read().decode("utf-8"))
            if "name" in imported:
                st.session_state.theme = imported
                theme = st.session_state.theme
                st.success(f'Loaded: "{imported["name"]}"')
            else:
                st.error("JSON must contain a 'name' field.")
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")

    st.divider()

    # Reset
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.session_state.theme = deepcopy(DEFAULT_THEME)
        theme = st.session_state.theme
        st.rerun()

    st.divider()

    # Export
    st.subheader("Export Theme")
    export_json = json.dumps(theme, indent=4)
    st.download_button(
        label="⬇️ Download Theme JSON",
        data=export_json,
        file_name=f"{theme['name'].replace(' ', '_')}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.caption("Built for Power BI Desktop theme customization. "
               "Import into PBI via View → Themes → Browse for themes.")


# ─────────────────────────────────────────────
# Main area tabs
# ─────────────────────────────────────────────
tab_general, tab_colors, tab_typography, tab_visuals, tab_json, tab_preview = st.tabs([
    "⚙️ General", "🎨 Colors", "🔤 Typography", "📊 Visual Styles", "📄 JSON", "👁️ Preview"
])


# ═══════════════════════════════════════════
# TAB: General
# ═══════════════════════════════════════════
with tab_general:
    st.header("General Settings")

    theme["name"] = st.text_input("Theme Name", value=theme.get("name", "Custom Theme"))

    st.subheader("Structural Colors")
    st.caption("These set foundational colors for UI elements across the entire report.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        theme["background"] = st.color_picker("Background", value=theme.get("background", "#FFFFFF"))
        theme["foreground"] = st.color_picker("Foreground", value=theme.get("foreground", "#252423"))
    with col2:
        theme["firstLevelElements"] = st.color_picker(
            "1st Level (primary text)", value=theme.get("firstLevelElements", "#252423"))
        theme["secondLevelElements"] = st.color_picker(
            "2nd Level (labels/axes)", value=theme.get("secondLevelElements", "#605E5C"))
    with col3:
        theme["thirdLevelElements"] = st.color_picker(
            "3rd Level (gridlines)", value=theme.get("thirdLevelElements", "#F3F2F1"))
        theme["fourthLevelElements"] = st.color_picker(
            "4th Level (dimmed)", value=theme.get("fourthLevelElements", "#B3B0AD"))
    with col4:
        theme["secondaryBackground"] = st.color_picker(
            "Secondary Background", value=theme.get("secondaryBackground", "#C8C6C4"))
        theme["tableAccent"] = st.color_picker(
            "Table Accent", value=theme.get("tableAccent", "#118DFF"))

    st.subheader("Semantic / Conditional Colors")
    st.caption("Used by KPIs, waterfall charts, and conditional formatting dialogs.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        theme["good"] = st.color_picker("Good", value=theme.get("good", "#2E8B57"))
    with col2:
        theme["neutral"] = st.color_picker("Neutral", value=theme.get("neutral", "#D9B300"))
    with col3:
        theme["bad"] = st.color_picker("Bad", value=theme.get("bad", "#D64554"))
    with col4:
        theme["null"] = st.color_picker("Null", value=theme.get("null", "#FF7F48"))

    col1, col2, col3 = st.columns(3)
    with col1:
        theme["maximum"] = st.color_picker("Maximum (gradient)", value=theme.get("maximum", "#118DFF"))
    with col2:
        theme["center"] = st.color_picker("Center (gradient)", value=theme.get("center", "#D9B300"))
    with col3:
        theme["minimum"] = st.color_picker("Minimum (gradient)", value=theme.get("minimum", "#DEEFFF"))


# ═══════════════════════════════════════════
# TAB: Colors (Data Palette)
# ═══════════════════════════════════════════
with tab_colors:
    st.header("Data Colors")
    st.caption("These colors are used for chart series, categories, and data points. "
               "Power BI cycles through them in order.")

    # Auto-generate option
    with st.expander("🪄 Auto-Generate Palette from Primary Color"):
        gen_col1, gen_col2 = st.columns([1, 3])
        with gen_col1:
            gen_primary = st.color_picker("Primary color", value=theme["dataColors"][0] if theme["dataColors"] else "#118DFF", key="gen_primary")
        with gen_col2:
            gen_count = st.slider("Number of colors", 4, 16, len(theme["dataColors"]), key="gen_count")
        if st.button("Generate Palette"):
            theme["dataColors"] = generate_palette(gen_primary, gen_count)
            st.rerun()

    st.divider()

    # Manual color editing
    num_colors = st.number_input(
        "Number of data colors",
        min_value=2, max_value=32,
        value=len(theme.get("dataColors", [])),
        key="num_data_colors"
    )

    # Adjust list length
    while len(theme["dataColors"]) < num_colors:
        theme["dataColors"].append("#888888")
    theme["dataColors"] = theme["dataColors"][:num_colors]

    # Render color pickers in rows of 8
    for row_start in range(0, num_colors, 8):
        cols = st.columns(min(8, num_colors - row_start))
        for i, col in enumerate(cols):
            idx = row_start + i
            with col:
                theme["dataColors"][idx] = st.color_picker(
                    f"Color {idx + 1}",
                    value=theme["dataColors"][idx],
                    key=f"dc_{idx}"
                )

    st.subheader("Palette Preview")
    render_swatch_row(theme["dataColors"], [f"#{i+1}" for i in range(len(theme["dataColors"]))])


# ═══════════════════════════════════════════
# TAB: Typography
# ═══════════════════════════════════════════
with tab_typography:
    st.header("Text Classes")
    st.caption("These define default typography across the report. "
               "Secondary classes (bold label, light label, etc.) inherit from these automatically.")

    if "textClasses" not in theme:
        theme["textClasses"] = deepcopy(DEFAULT_THEME["textClasses"])

    tc = theme["textClasses"]

    for class_key, class_label, description in [
        ("callout", "Callout (Card Values / KPI)", "Large data values on cards and KPI visuals."),
        ("title", "Title (Visual Titles / Axis Titles)", "Titles on visuals, category axis titles, slicer headers."),
        ("header", "Header (Key Influencers / Tab Headers)", "Key influencers headers, tab headers."),
        ("label", "Label (Table/Matrix Values, Axis Labels)", "Table values, axis labels, legend text, slicer items."),
    ]:
        with st.expander(f"📝 {class_label}"):
            st.caption(description)
            if class_key not in tc:
                tc[class_key] = {"fontSize": 10, "fontFace": "Segoe UI", "color": "#252423"}

            col1, col2, col3 = st.columns(3)
            with col1:
                current_font = tc[class_key].get("fontFace", "Segoe UI")
                font_idx = FONT_OPTIONS.index(current_font) if current_font in FONT_OPTIONS else 0
                tc[class_key]["fontFace"] = st.selectbox(
                    "Font", FONT_OPTIONS, index=font_idx, key=f"tc_font_{class_key}"
                )
            with col2:
                tc[class_key]["fontSize"] = st.number_input(
                    "Size (pt)", min_value=6, max_value=72,
                    value=tc[class_key].get("fontSize", 10),
                    key=f"tc_size_{class_key}"
                )
            with col3:
                tc[class_key]["color"] = st.color_picker(
                    "Color", value=tc[class_key].get("color", "#252423"),
                    key=f"tc_color_{class_key}"
                )


# ═══════════════════════════════════════════
# TAB: Visual Styles
# ═══════════════════════════════════════════
with tab_visuals:
    st.header("Visual Styles")
    st.caption("Configure background, border, and formatting defaults per visual type. "
               "The global wildcard (*) applies to all visuals unless overridden.")

    if "visualStyles" not in theme:
        theme["visualStyles"] = {}

    vs = theme["visualStyles"]

    # ── Global wildcard section ──
    with st.expander("🌐 Global Defaults (applies to all visuals)", expanded=True):
        st.caption("Settings here apply to every visual. Override per-visual below.")

        if "*" not in vs:
            vs["*"] = {"*": {}}
        glob = vs["*"].get("*", {})
        vs["*"]["*"] = glob

        # Title
        st.markdown("**Visual Title**")
        title_cfg = glob.get("title", [{}])[0] if "title" in glob else {}
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        with t_col1:
            title_show = st.checkbox("Show title", value=title_cfg.get("show", True), key="glob_title_show")
        with t_col2:
            title_color = st.color_picker(
                "Title color",
                value=title_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                key="glob_title_color"
            )
        with t_col3:
            title_size = st.number_input(
                "Title size", 8, 36,
                value=title_cfg.get("fontSize", 14),
                key="glob_title_size"
            )
        with t_col4:
            title_font_val = title_cfg.get("fontFamily", "Segoe UI Semibold")
            title_font_idx = FONT_OPTIONS.index(title_font_val) if title_font_val in FONT_OPTIONS else 0
            title_font = st.selectbox("Title font", FONT_OPTIONS, index=title_font_idx, key="glob_title_font")

        glob["title"] = [{
            "show": title_show,
            "fontColor": color_fill(title_color),
            "fontSize": title_size,
            "fontFamily": title_font,
            "alignment": "Left",
        }]

        st.divider()

        # Subtitle
        st.markdown("**Subtitle**")
        sub_cfg = glob.get("subTitle", [{}])[0] if "subTitle" in glob else {}
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            sub_color = st.color_picker(
                "Subtitle color",
                value=sub_cfg.get("fontColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                key="glob_sub_color"
            )
        with s_col2:
            sub_size = st.number_input("Subtitle size", 6, 24,
                                        value=sub_cfg.get("fontSize", 11), key="glob_sub_size")
        with s_col3:
            sub_font_val = sub_cfg.get("fontFamily", "Segoe UI")
            sub_font_idx = FONT_OPTIONS.index(sub_font_val) if sub_font_val in FONT_OPTIONS else 0
            sub_font = st.selectbox("Subtitle font", FONT_OPTIONS, index=sub_font_idx, key="glob_sub_font")

        glob["subTitle"] = [{
            "show": True,
            "fontColor": color_fill(sub_color),
            "fontSize": sub_size,
            "fontFamily": sub_font,
        }]

        st.divider()

        # Category Axis
        st.markdown("**Category Axis**")
        cat_cfg = glob.get("categoryAxis", [{}])[0] if "categoryAxis" in glob else {}
        ca_col1, ca_col2, ca_col3, ca_col4 = st.columns(4)
        with ca_col1:
            ca_label_color = st.color_picker(
                "Axis label color",
                value=cat_cfg.get("labelColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                key="glob_ca_color"
            )
        with ca_col2:
            ca_size = st.number_input("Axis font size", 6, 24,
                                       value=cat_cfg.get("fontSize", 10), key="glob_ca_size")
        with ca_col3:
            ca_show_title = st.checkbox("Show axis title", value=cat_cfg.get("showAxisTitle", False), key="glob_ca_title")
        with ca_col4:
            ca_gridline = st.checkbox("Show gridlines", value=cat_cfg.get("gridlineShow", False), key="glob_ca_grid")

        glob["categoryAxis"] = [{
            "show": True,
            "labelColor": color_fill(ca_label_color),
            "fontSize": ca_size,
            "fontFamily": "Segoe UI",
            "showAxisTitle": ca_show_title,
            "gridlineShow": ca_gridline,
        }]

        st.divider()

        # Value Axis
        st.markdown("**Value Axis**")
        val_cfg = glob.get("valueAxis", [{}])[0] if "valueAxis" in glob else {}
        va_col1, va_col2, va_col3, va_col4 = st.columns(4)
        with va_col1:
            va_label_color = st.color_picker(
                "Axis label color",
                value=val_cfg.get("labelColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                key="glob_va_color"
            )
        with va_col2:
            va_size = st.number_input("Axis font size", 6, 24,
                                       value=val_cfg.get("fontSize", 10), key="glob_va_size")
        with va_col3:
            va_gridline = st.checkbox("Show gridlines", value=val_cfg.get("gridlineShow", True), key="glob_va_grid")
        with va_col4:
            va_grid_color = st.color_picker(
                "Gridline color",
                value=val_cfg.get("gridlineColor", {}).get("solid", {}).get("color", "#E0E0E0"),
                key="glob_va_grid_color"
            )

        glob["valueAxis"] = [{
            "show": True,
            "labelColor": color_fill(va_label_color),
            "fontSize": va_size,
            "fontFamily": "Segoe UI",
            "showAxisTitle": False,
            "gridlineShow": va_gridline,
            "gridlineColor": color_fill(va_grid_color),
            "gridlineThickness": 1,
        }]

        st.divider()

        # Legend
        st.markdown("**Legend**")
        leg_cfg = glob.get("legend", [{}])[0] if "legend" in glob else {}
        lg_col1, lg_col2, lg_col3, lg_col4 = st.columns(4)
        with lg_col1:
            lg_show = st.checkbox("Show legend", value=leg_cfg.get("show", True), key="glob_lg_show")
        with lg_col2:
            lg_pos_options = ["Top", "Bottom", "Left", "Right", "TopCenter", "BottomCenter"]
            lg_pos_val = leg_cfg.get("position", "Top")
            lg_pos_idx = lg_pos_options.index(lg_pos_val) if lg_pos_val in lg_pos_options else 0
            lg_pos = st.selectbox("Position", lg_pos_options, index=lg_pos_idx, key="glob_lg_pos")
        with lg_col3:
            lg_size = st.number_input("Font size", 6, 24,
                                       value=leg_cfg.get("fontSize", 10), key="glob_lg_size")
        with lg_col4:
            lg_color = st.color_picker(
                "Label color",
                value=leg_cfg.get("labelColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                key="glob_lg_color"
            )

        glob["legend"] = [{
            "show": lg_show,
            "position": lg_pos,
            "fontSize": lg_size,
            "fontFamily": "Segoe UI",
            "labelColor": color_fill(lg_color),
        }]

    # ── Page background ──
    with st.expander("📄 Page Background"):
        if "page" not in vs:
            vs["page"] = {"*": {}}
        page_bg_cfg = vs["page"].get("*", {}).get("background", [{}])[0] if "background" in vs["page"].get("*", {}) else {}

        pg_col1, pg_col2 = st.columns(2)
        with pg_col1:
            page_bg = st.color_picker(
                "Page background color",
                value=page_bg_cfg.get("color", {}).get("solid", {}).get("color", "#FFFFFF"),
                key="page_bg_color"
            )
        with pg_col2:
            page_transparency = st.slider(
                "Transparency %", 0, 100,
                value=page_bg_cfg.get("transparency", 0),
                key="page_bg_trans"
            )

        vs["page"]["*"]["background"] = [{
            "color": color_fill(page_bg),
            "transparency": page_transparency,
        }]

    # ── Per-visual overrides ──
    st.divider()
    st.subheader("Per-Visual Overrides")
    st.caption("Enable and configure background, border, and specific formatting for individual visual types.")

    for vis_key, vis_label in VISUAL_TYPES:
        with st.expander(f"📊 {vis_label} (`{vis_key}`)"):

            enable_key = f"enable_{vis_key}"
            already_configured = vis_key in vs
            enabled = st.checkbox(
                f"Enable overrides for {vis_label}",
                value=already_configured,
                key=enable_key
            )

            if not enabled:
                if vis_key in vs:
                    del vs[vis_key]
                continue

            if vis_key not in vs:
                vs[vis_key] = {"*": {}}
            vis_cfg = vs[vis_key].get("*", {})
            vs[vis_key]["*"] = vis_cfg

            # Background
            bg_cfg = vis_cfg.get("background", [{}])[0] if "background" in vis_cfg else {}
            st.markdown("**Background**")
            bg_c1, bg_c2, bg_c3 = st.columns(3)
            with bg_c1:
                bg_show = st.checkbox(
                    "Show background", value=bg_cfg.get("show", False),
                    key=f"{vis_key}_bg_show"
                )
            with bg_c2:
                bg_color = st.color_picker(
                    "Color",
                    value=bg_cfg.get("color", {}).get("solid", {}).get("color", "#F0F0F0"),
                    key=f"{vis_key}_bg_color"
                )
            with bg_c3:
                bg_trans = st.slider(
                    "Transparency %", 0, 100,
                    value=bg_cfg.get("transparency", 0),
                    key=f"{vis_key}_bg_trans"
                )

            vis_cfg["background"] = [{
                "show": bg_show,
                "color": color_fill(bg_color),
                "transparency": bg_trans,
            }]

            # Border
            bdr_cfg = vis_cfg.get("border", [{}])[0] if "border" in vis_cfg else {}
            st.markdown("**Border**")
            bd_c1, bd_c2, bd_c3 = st.columns(3)
            with bd_c1:
                bd_show = st.checkbox(
                    "Show border", value=bdr_cfg.get("show", True),
                    key=f"{vis_key}_bd_show"
                )
            with bd_c2:
                bd_color = st.color_picker(
                    "Border color",
                    value=bdr_cfg.get("color", {}).get("solid", {}).get("color", "#E0E0E0"),
                    key=f"{vis_key}_bd_color"
                )
            with bd_c3:
                bd_radius = st.number_input(
                    "Corner radius", 0, 30,
                    value=bdr_cfg.get("radius", 8),
                    key=f"{vis_key}_bd_radius"
                )

            vis_cfg["border"] = [{
                "show": bd_show,
                "color": color_fill(bd_color),
                "radius": bd_radius,
            }]

            # ── Card-specific fields ──
            if vis_key == "card":
                st.markdown("**Card Labels**")
                card_labels_cfg = vis_cfg.get("labels", [{}])[0] if "labels" in vis_cfg else {}
                card_cat_cfg = vis_cfg.get("categoryLabels", [{}])[0] if "categoryLabels" in vis_cfg else {}

                cl_c1, cl_c2, cl_c3 = st.columns(3)
                with cl_c1:
                    card_val_color = st.color_picker(
                        "Value color",
                        value=card_labels_cfg.get("color", {}).get("solid", {}).get("color", "#1A1A1A"),
                        key="card_val_color"
                    )
                with cl_c2:
                    card_val_size = st.number_input(
                        "Value font size", 8, 72,
                        value=card_labels_cfg.get("fontSize", 28),
                        key="card_val_size"
                    )
                with cl_c3:
                    card_cat_color = st.color_picker(
                        "Category label color",
                        value=card_cat_cfg.get("color", {}).get("solid", {}).get("color", "#252423"),
                        key="card_cat_color"
                    )

                vis_cfg["labels"] = [{
                    "color": color_fill(card_val_color),
                    "fontSize": card_val_size,
                    "fontFamily": "Segoe UI",
                }]
                vis_cfg["categoryLabels"] = [{
                    "show": True,
                    "color": color_fill(card_cat_color),
                    "fontSize": 12,
                    "fontFamily": "Segoe UI Semibold",
                }]

            # ── New Card visual fields ──
            if vis_key == "cardVisual":
                st.markdown("**Card Visual Values & Labels**")
                cv_val_cfg = vis_cfg.get("value", [{}])[0] if "value" in vis_cfg else {}
                cv_lbl_cfg = vis_cfg.get("label", [{}])[0] if "label" in vis_cfg else {}

                cv_c1, cv_c2, cv_c3, cv_c4 = st.columns(4)
                with cv_c1:
                    cv_val_color = st.color_picker(
                        "Value color",
                        value=cv_val_cfg.get("fontColor", {}).get("solid", {}).get("color", "#1A1A1A"),
                        key="cv_val_color"
                    )
                with cv_c2:
                    cv_val_size = st.number_input(
                        "Value size", 8, 72,
                        value=cv_val_cfg.get("fontSize", 28),
                        key="cv_val_size"
                    )
                with cv_c3:
                    cv_lbl_color = st.color_picker(
                        "Label color",
                        value=cv_lbl_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                        key="cv_lbl_color"
                    )
                with cv_c4:
                    cv_lbl_size = st.number_input(
                        "Label size", 6, 36,
                        value=cv_lbl_cfg.get("fontSize", 12),
                        key="cv_lbl_size"
                    )

                vis_cfg["value"] = [{
                    "$id": "default",
                    "fontSize": cv_val_size,
                    "fontColor": color_fill(cv_val_color),
                    "fontFamily": "Segoe UI",
                }]
                vis_cfg["label"] = [{
                    "$id": "default",
                    "show": True,
                    "fontSize": cv_lbl_size,
                    "fontColor": color_fill(cv_lbl_color),
                    "fontFamily": "Segoe UI Semibold",
                }]

            # ── Table/Matrix specific ──
            if vis_key in ("tableEx", "pivotTable"):
                st.markdown("**Column Headers**")
                ch_cfg = vis_cfg.get("columnHeaders", [{}])[0] if "columnHeaders" in vis_cfg else {}
                ch_c1, ch_c2, ch_c3 = st.columns(3)
                with ch_c1:
                    ch_font_color = st.color_picker(
                        "Header font color",
                        value=ch_cfg.get("fontColor", {}).get("solid", {}).get("color", "#FFFFFF"),
                        key=f"{vis_key}_ch_fc"
                    )
                with ch_c2:
                    ch_back_color = st.color_picker(
                        "Header background",
                        value=ch_cfg.get("backColor", {}).get("solid", {}).get("color", "#118DFF"),
                        key=f"{vis_key}_ch_bg"
                    )
                with ch_c3:
                    ch_size = st.number_input(
                        "Header font size", 6, 24,
                        value=ch_cfg.get("fontSize", 11),
                        key=f"{vis_key}_ch_size"
                    )

                vis_cfg["columnHeaders"] = [{
                    "fontColor": color_fill(ch_font_color),
                    "backColor": color_fill(ch_back_color),
                    "fontSize": ch_size,
                    "fontFamily": "Segoe UI Semibold",
                }]

                st.markdown("**Values**")
                v_cfg = vis_cfg.get("values", [{}])[0] if "values" in vis_cfg else {}
                v_c1, v_c2 = st.columns(2)
                with v_c1:
                    v_primary_bg = st.color_picker(
                        "Primary row bg",
                        value=v_cfg.get("backColorPrimary", {}).get("solid", {}).get("color", "#FFFFFF"),
                        key=f"{vis_key}_v_pbg"
                    )
                with v_c2:
                    v_alt_bg = st.color_picker(
                        "Alternating row bg",
                        value=v_cfg.get("backColorSecondary", {}).get("solid", {}).get("color", "#F9F9F9"),
                        key=f"{vis_key}_v_abg"
                    )

                vis_cfg["values"] = [{
                    "fontColorPrimary": color_fill(theme.get("firstLevelElements", "#252423")),
                    "backColorPrimary": color_fill(v_primary_bg),
                    "fontColorSecondary": color_fill(theme.get("firstLevelElements", "#252423")),
                    "backColorSecondary": color_fill(v_alt_bg),
                    "fontSize": 11,
                    "fontFamily": "Segoe UI",
                }]

                st.markdown("**Totals**")
                tot_cfg = vis_cfg.get("total", [{}])[0] if "total" in vis_cfg else {}
                tot_c1, tot_c2 = st.columns(2)
                with tot_c1:
                    tot_fc = st.color_picker(
                        "Totals font color",
                        value=tot_cfg.get("fontColor", {}).get("solid", {}).get("color", "#FFFFFF"),
                        key=f"{vis_key}_tot_fc"
                    )
                with tot_c2:
                    tot_bg = st.color_picker(
                        "Totals background",
                        value=tot_cfg.get("backColor", {}).get("solid", {}).get("color", "#1A1A1A"),
                        key=f"{vis_key}_tot_bg"
                    )

                vis_cfg["total"] = [{
                    "fontColor": color_fill(tot_fc),
                    "backColor": color_fill(tot_bg),
                    "fontSize": 11,
                    "fontFamily": "Segoe UI Semibold",
                }]

            # ── Waterfall specific ──
            if vis_key == "waterfallChart":
                st.markdown("**Sentiment Colors**")
                sent_cfg = vis_cfg.get("sentimentColors", [{}])[0] if "sentimentColors" in vis_cfg else {}
                wf_c1, wf_c2, wf_c3 = st.columns(3)
                with wf_c1:
                    wf_inc = st.color_picker(
                        "Increase",
                        value=sent_cfg.get("increaseFill", {}).get("solid", {}).get("color", "#2E8B57"),
                        key="wf_inc"
                    )
                with wf_c2:
                    wf_dec = st.color_picker(
                        "Decrease",
                        value=sent_cfg.get("decreaseFill", {}).get("solid", {}).get("color", "#D64554"),
                        key="wf_dec"
                    )
                with wf_c3:
                    wf_tot = st.color_picker(
                        "Total",
                        value=sent_cfg.get("totalFill", {}).get("solid", {}).get("color", "#118DFF"),
                        key="wf_tot"
                    )

                vis_cfg["sentimentColors"] = [{
                    "increaseFill": color_fill(wf_inc),
                    "decreaseFill": color_fill(wf_dec),
                    "totalFill": color_fill(wf_tot),
                }]

            # ── Line chart specific ──
            if vis_key == "lineChart":
                st.markdown("**Line Styles**")
                ls_cfg = vis_cfg.get("lineStyles", [{}])[0] if "lineStyles" in vis_cfg else {}
                ls_c1, ls_c2, ls_c3 = st.columns(3)
                with ls_c1:
                    ls_width = st.number_input(
                        "Stroke width", 1, 10,
                        value=ls_cfg.get("strokeWidth", 2),
                        key="ls_width"
                    )
                with ls_c2:
                    ls_marker = st.checkbox(
                        "Show markers",
                        value=ls_cfg.get("showMarker", False),
                        key="ls_marker"
                    )
                with ls_c3:
                    ls_marker_size = st.number_input(
                        "Marker size", 1, 20,
                        value=ls_cfg.get("markerSize", 5),
                        key="ls_marker_size"
                    )

                vis_cfg["lineStyles"] = [{
                    "strokeWidth": ls_width,
                    "showMarker": ls_marker,
                    "markerSize": ls_marker_size,
                }]


# ═══════════════════════════════════════════
# TAB: JSON Output
# ═══════════════════════════════════════════
with tab_json:
    st.header("Generated Theme JSON")
    st.caption("Copy this directly or use the download button in the sidebar.")

    # Clean empty visualStyles
    clean_theme = deepcopy(theme)
    if "visualStyles" in clean_theme:
        vs_clean = clean_theme["visualStyles"]
        empty_keys = [k for k, v in vs_clean.items() if v == {"*": {}}]
        for k in empty_keys:
            del vs_clean[k]
        if not vs_clean:
            del clean_theme["visualStyles"]

    json_output = json.dumps(clean_theme, indent=4)
    st.code(json_output, language="json", line_numbers=True)

    st.download_button(
        label="⬇️ Download Theme JSON",
        data=json_output,
        file_name=f"{theme['name'].replace(' ', '_')}.json",
        mime="application/json",
    )


# ═══════════════════════════════════════════
# TAB: Preview
# ═══════════════════════════════════════════
with tab_preview:
    st.header("Theme Preview")
    st.caption("Approximate preview of how your theme will look in Power BI.")

    page_bg = theme.get("background", "#FFFFFF")

    # Data colors bar
    st.subheader("Data Color Palette")
    render_swatch_row(theme["dataColors"])

    st.divider()

    # Structural colors
    st.subheader("Structural Colors")
    struct_colors = [
        theme.get("firstLevelElements", "#252423"),
        theme.get("secondLevelElements", "#605E5C"),
        theme.get("thirdLevelElements", "#F3F2F1"),
        theme.get("fourthLevelElements", "#B3B0AD"),
        theme.get("background", "#FFFFFF"),
        theme.get("secondaryBackground", "#C8C6C4"),
        theme.get("tableAccent", "#118DFF"),
    ]
    struct_labels = ["1st Level", "2nd Level", "3rd Level", "4th Level", "Background", "2nd Background", "Table Accent"]
    render_swatch_row(struct_colors, struct_labels)

    st.divider()

    # Semantic colors
    st.subheader("Semantic Colors")
    sem_colors = [theme.get("good", "#2E8B57"), theme.get("neutral", "#D9B300"),
                  theme.get("bad", "#D64554"), theme.get("null", "#FF7F48")]
    sem_labels = ["Good", "Neutral", "Bad", "Null"]
    render_swatch_row(sem_colors, sem_labels)

    st.divider()

    # Gradient
    st.subheader("Conditional Formatting Gradient")
    grad_colors = [theme.get("minimum", "#DEEFFF"), theme.get("center", "#D9B300"), theme.get("maximum", "#118DFF")]
    grad_html = (
        f'<div style="height:32px;border-radius:6px;'
        f'background:linear-gradient(to right, {grad_colors[0]}, {grad_colors[1]}, {grad_colors[2]});'
        f'border:1px solid #ccc;"></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:10px;color:#666;">'
        f'<span>Minimum</span><span>Center</span><span>Maximum</span></div>'
    )
    st.markdown(grad_html, unsafe_allow_html=True)

    st.divider()

    # Typography preview
    st.subheader("Typography")
    for cls_key, cls_label in [("callout", "Callout"), ("title", "Title"), ("header", "Header"), ("label", "Label")]:
        tc_item = theme.get("textClasses", {}).get(cls_key, {})
        font = tc_item.get("fontFace", "Segoe UI")
        size = tc_item.get("fontSize", 10)
        color = tc_item.get("color", "#252423")
        # Cap preview size for readability
        preview_size = min(size, 36)
        st.markdown(
            f'<div style="font-family:{font},sans-serif;font-size:{preview_size}px;color:{color};'
            f'padding:4px 0;">{cls_label}: {font} {size}pt</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Mock card preview
    st.subheader("Card Preview")
    card_vs = theme.get("visualStyles", {}).get("card", {}).get("*", {})
    card_bg_raw = card_vs.get("background", [{}])[0] if "background" in card_vs else {}
    card_bg_color = card_bg_raw.get("color", {}).get("solid", {}).get("color", page_bg)
    card_bg_show = card_bg_raw.get("show", False)
    card_bdr_raw = card_vs.get("border", [{}])[0] if "border" in card_vs else {}
    card_bdr_color = card_bdr_raw.get("color", {}).get("solid", {}).get("color", "#E0E0E0")
    card_bdr_show = card_bdr_raw.get("show", False)
    card_bdr_radius = card_bdr_raw.get("radius", 0)
    card_label_raw = card_vs.get("categoryLabels", [{}])[0] if "categoryLabels" in card_vs else {}
    card_label_color = card_label_raw.get("color", {}).get("solid", {}).get("color", theme.get("foreground", "#252423"))
    card_val_raw = card_vs.get("labels", [{}])[0] if "labels" in card_vs else {}
    card_val_color = card_val_raw.get("color", {}).get("solid", {}).get("color", theme.get("foreground", "#252423"))
    card_val_size = card_val_raw.get("fontSize", 28)

    card_style_bg = card_bg_color if card_bg_show else page_bg
    card_style_border = f"1px solid {card_bdr_color}" if card_bdr_show else "1px solid transparent"

    mock_cards_html = f'<div style="display:flex;gap:12px;padding:16px;background:{page_bg};border-radius:8px;">'
    for label, value in [("Gross Sales", "127.9M"), ("Profit", "16.9M"), ("Units Sold", "1.13M")]:
        mock_cards_html += (
            f'<div style="flex:1;background:{card_style_bg};border:{card_style_border};'
            f'border-radius:{card_bdr_radius}px;padding:16px;">'
            f'<div style="font-size:12px;color:{card_label_color};font-weight:600;font-family:Segoe UI,sans-serif;">{label}</div>'
            f'<div style="font-size:{min(card_val_size, 32)}px;color:{card_val_color};font-family:Segoe UI,sans-serif;font-weight:400;">{value}</div>'
            f'</div>'
        )
    mock_cards_html += '</div>'
    st.markdown(mock_cards_html, unsafe_allow_html=True)
