import streamlit as st
import json
import math
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
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.3rem !important; margin-top: 1rem !important; }
    h3 { font-size: 1.1rem !important; }
    div[data-testid="stExpander"] summary {
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* ── Sidebar nav buttons — flat, left-aligned, full width ── */
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #555 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.55rem 0.9rem !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        border-left: 3px solid transparent !important;
        transition: background 0.15s, color 0.15s !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(49,130,206,0.07) !important;
        color: #1a73e8 !important;
    }

    /* ── Active nav item (rendered as markdown div) ── */
    .nav-active {
        padding: 0.55rem 0.9rem;
        border-radius: 8px;
        background: rgba(49,130,206,0.12);
        color: #1a73e8;
        border-left: 3px solid #1a73e8;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 1px 0;
        line-height: 1.5;
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
        "largeTitle": {"fontSize": 28, "fontFace": "Segoe UI Light", "color": "#252423"},
        "dataTitle": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": "#252423"},
        "boldLabel": {"fontSize": 10, "fontFace": "Segoe UI Semibold", "color": "#252423"},
        "largeLabel": {"fontSize": 14, "fontFace": "Segoe UI", "color": "#252423"},
        "largeLightLabel": {"fontSize": 14, "fontFace": "Segoe UI Light", "color": "#605E5C"},
        "lightLabel": {"fontSize": 10, "fontFace": "Segoe UI Light", "color": "#605E5C"},
        "semiboldLabel": {"fontSize": 10, "fontFace": "Segoe UI Semibold", "color": "#252423"},
        "smallLabel": {"fontSize": 9, "fontFace": "Segoe UI", "color": "#605E5C"},
        "smallLightLabel": {"fontSize": 9, "fontFace": "Segoe UI Light", "color": "#605E5C"},
        "smallDataLabel": {"fontSize": 9, "fontFace": "Segoe UI", "color": "#252423"},
    },
    # Extended foreground/background tokens
    "foregroundLight": "#B3B0AD",
    "foregroundDark": "#252423",
    "foregroundNeutralLight": "#C8C6C4",
    "foregroundNeutralDark": "#323130",
    "foregroundNeutralSecondary": "#605E5C",
    "foregroundNeutralSecondaryAlt": "#6B6B6B",
    "foregroundNeutralSecondaryAlt2": "#8A8886",
    "foregroundNeutralTertiary": "#A19F9D",
    "foregroundNeutralTertiaryAlt": "#B3B0AD",
    "foregroundSelected": "#118DFF",
    "foregroundButton": "#FFFFFF",
    # Extended background tokens
    "backgroundLight": "#F3F2F1",
    "backgroundNeutral": "#C8C6C4",
    "backgroundDark": "#252423",
    # Interaction / misc tokens
    "accent": "#118DFF",
    "hyperlink": "#118DFF",
    "visitedHyperlink": "#744EC2",
    "shapeStroke": "#252423",
    "disabledText": "#B3B0AD",
    "mapPushpin": "#118DFF",
    "visualStyles": {},
}

FONT_OPTIONS = [
    "Segoe UI", "Segoe UI Semibold", "Segoe UI Bold", "Segoe UI Light",
    "Arial", "Calibri", "Cambria", "Consolas", "Courier New",
    "DIN", "Georgia", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana",
]

VISUAL_TYPES = [
    # Chart visuals
    ("lineChart", "Line Chart"),
    ("clusteredBarChart", "Clustered Bar"),
    ("clusteredColumnChart", "Clustered Column"),
    ("barChart", "Stacked Bar"),
    ("columnChart", "Stacked Column"),
    ("hundredPercentStackedBarChart", "100% Stacked Bar"),
    ("hundredPercentStackedColumnChart", "100% Stacked Column"),
    ("areaChart", "Area Chart"),
    ("stackedAreaChart", "Stacked Area Chart"),
    ("hundredPercentStackedAreaChart", "100% Stacked Area"),
    ("lineClusteredColumnComboChart", "Line & Clustered Column Combo"),
    ("lineStackedColumnComboChart", "Line & Stacked Column Combo"),
    ("ribbonChart", "Ribbon Chart"),
    ("pieChart", "Pie Chart"),
    ("donutChart", "Donut Chart"),
    ("waterfallChart", "Waterfall"),
    ("funnel", "Funnel"),
    ("scatterChart", "Scatter Chart"),
    ("treemap", "Treemap"),
    # Maps
    ("map", "Map"),
    ("filledMap", "Filled Map"),
    ("shapeMap", "Shape Map"),
    ("azureMap", "Azure Map"),
    # KPI / data
    ("gauge", "Gauge"),
    ("kpi", "KPI"),
    ("card", "Card (Legacy)"),
    ("cardVisual", "Card (New)"),
    ("multiRowCard", "Multi-Row Card"),
    # Table / matrix
    ("tableEx", "Table"),
    ("pivotTable", "Matrix"),
    # Slicers
    ("slicer", "Slicer"),
    ("advancedSlicerVisual", "Advanced Slicer"),
    ("textSlicer", "Text Filter Slicer"),
    ("listSlicer", "List Slicer"),
    # AI / advanced visuals
    ("keyDriversVisual", "Key Influencers"),
    ("decompositionTreeVisual", "Decomposition Tree"),
    ("qnaVisual", "Q&A"),
    ("aiNarratives", "Smart Narrative"),
    ("scorecard", "Metrics"),
    # Script / paginated
    ("scriptVisual", "R Visual"),
    ("pythonVisual", "Python Visual"),
    ("rdlVisual", "Paginated Report"),
    # Navigation / layout
    ("actionButton", "Button"),
    ("bookmarkNavigator", "Bookmark Navigator"),
    ("pageNavigator", "Page Navigator"),
    # Static
    ("shape", "Shape"),
    ("image", "Image"),
    ("textbox", "Textbox"),
]

# Visual types that have category/value axes and data labels
AXIS_CHART_VISUALS = {
    "lineChart", "clusteredBarChart", "clusteredColumnChart", "barChart", "columnChart",
    "hundredPercentStackedBarChart", "hundredPercentStackedColumnChart",
    "areaChart", "stackedAreaChart", "hundredPercentStackedAreaChart",
    "lineClusteredColumnComboChart", "lineStackedColumnComboChart",
    "ribbonChart", "waterfallChart", "funnel", "scatterChart",
}

# Visual types that are pie/donut (radial, no standard axes)
PIE_CHART_VISUALS = {"pieChart", "donutChart", "treemap"}

# Slicer-type visuals
SLICER_VISUALS = {"slicer", "advancedSlicerVisual", "textSlicer", "listSlicer"}

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = deepcopy(DEFAULT_THEME)

theme = st.session_state.theme


# ─────────────────────────────────────────────
# Sidebar — Navigation + Import / Export / Reset
# ─────────────────────────────────────────────
NAV_ITEMS = [
    ("⚙️", "General"),
    ("🎨", "Colors"),
    ("🔤", "Typography"),
    ("📊", "Visuals"),
    ("📄", "JSON"),
    ("👁️", "Preview"),
]

if "current_page" not in st.session_state:
    st.session_state.current_page = "General"

with st.sidebar:
    st.title("🎨 Power BI Theme Builder")
    st.caption("Build, customize, and export Power BI theme JSON files.")

    st.divider()

    for _icon, _label in NAV_ITEMS:
        if st.session_state.current_page == _label:
            st.markdown(f'<div class="nav-active">{_icon}&nbsp;&nbsp;{_label}</div>', unsafe_allow_html=True)
        else:
            if st.button(f"{_icon}  {_label}", key=f"nav_{_label}", use_container_width=True):
                st.session_state.current_page = _label
                st.rerun()

    current_page = st.session_state.current_page

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




# ═══════════════════════════════════════════
# PAGE: General
# ═══════════════════════════════════════════
if current_page == "General":
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

    st.subheader("Extended Color Tokens")
    st.caption("Advanced tokens used by specific Power BI UI elements. "
               "Leave at defaults if unsure — these are resolved from the structural colors above.")

    with st.expander("🎨 Foreground Variants"):
        ev_col1, ev_col2, ev_col3, ev_col4 = st.columns(4)
        with ev_col1:
            theme["accent"] = st.color_picker("Accent", value=theme.get("accent", "#118DFF"), key="ext_accent")
            theme["foregroundLight"] = st.color_picker("Foreground Light", value=theme.get("foregroundLight", "#B3B0AD"), key="ext_fgLight")
            theme["foregroundDark"] = st.color_picker("Foreground Dark", value=theme.get("foregroundDark", "#252423"), key="ext_fgDark")
        with ev_col2:
            theme["foregroundNeutralLight"] = st.color_picker("Neutral Light", value=theme.get("foregroundNeutralLight", "#C8C6C4"), key="ext_fgNL")
            theme["foregroundNeutralDark"] = st.color_picker("Neutral Dark", value=theme.get("foregroundNeutralDark", "#323130"), key="ext_fgND")
            theme["foregroundNeutralSecondary"] = st.color_picker("Neutral Secondary", value=theme.get("foregroundNeutralSecondary", "#605E5C"), key="ext_fgNS")
        with ev_col3:
            theme["foregroundNeutralSecondaryAlt"] = st.color_picker("Neutral Secondary Alt", value=theme.get("foregroundNeutralSecondaryAlt", "#6B6B6B"), key="ext_fgNSA")
            theme["foregroundNeutralSecondaryAlt2"] = st.color_picker("Neutral Secondary Alt2", value=theme.get("foregroundNeutralSecondaryAlt2", "#8A8886"), key="ext_fgNSA2")
            theme["foregroundNeutralTertiary"] = st.color_picker("Neutral Tertiary", value=theme.get("foregroundNeutralTertiary", "#A19F9D"), key="ext_fgNT")
        with ev_col4:
            theme["foregroundNeutralTertiaryAlt"] = st.color_picker("Neutral Tertiary Alt", value=theme.get("foregroundNeutralTertiaryAlt", "#B3B0AD"), key="ext_fgNTA")
            theme["foregroundSelected"] = st.color_picker("Selected", value=theme.get("foregroundSelected", "#118DFF"), key="ext_fgSel")
            theme["foregroundButton"] = st.color_picker("Button Text", value=theme.get("foregroundButton", "#FFFFFF"), key="ext_fgBtn")

    with st.expander("🖼️ Background Variants & Interaction Colors"):
        bv_col1, bv_col2, bv_col3 = st.columns(3)
        with bv_col1:
            theme["backgroundLight"] = st.color_picker("Background Light", value=theme.get("backgroundLight", "#F3F2F1"), key="ext_bgLight")
            theme["backgroundNeutral"] = st.color_picker("Background Neutral", value=theme.get("backgroundNeutral", "#C8C6C4"), key="ext_bgNeutral")
            theme["backgroundDark"] = st.color_picker("Background Dark", value=theme.get("backgroundDark", "#252423"), key="ext_bgDark")
        with bv_col2:
            theme["hyperlink"] = st.color_picker("Hyperlink", value=theme.get("hyperlink", "#118DFF"), key="ext_hyperlink")
            theme["visitedHyperlink"] = st.color_picker("Visited Hyperlink", value=theme.get("visitedHyperlink", "#744EC2"), key="ext_visitedHyperlink")
        with bv_col3:
            theme["shapeStroke"] = st.color_picker("Shape Stroke", value=theme.get("shapeStroke", "#252423"), key="ext_shapeStroke")
            theme["disabledText"] = st.color_picker("Disabled Text", value=theme.get("disabledText", "#B3B0AD"), key="ext_disabledText")
            theme["mapPushpin"] = st.color_picker("Map Pushpin", value=theme.get("mapPushpin", "#118DFF"), key="ext_mapPushpin")




# ═══════════════════════════════════════════
# PAGE: Colors (Data Palette)
# ═══════════════════════════════════════════
if current_page == "Colors":
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
# PAGE: Typography
# ═══════════════════════════════════════════
if current_page == "Typography":
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
        ("largeTitle", "Large Title", "Large display title, often used for report-level headings."),
        ("dataTitle", "Data Title", "Semi-bold titles above data areas (e.g. slicer title, matrix header)."),
        ("boldLabel", "Bold Label", "Bold variant of the standard label class."),
        ("largeLabel", "Large Label", "Larger body text, e.g. axis tick labels at higher font sizes."),
        ("largeLightLabel", "Large Light Label", "Larger, lighter-weight variant — subtitles and secondary info."),
        ("lightLabel", "Light Label", "Light-weight body text for de-emphasised content."),
        ("semiboldLabel", "Semibold Label", "Slightly heavier than label but lighter than boldLabel."),
        ("smallLabel", "Small Label", "Smallest regular text — footnotes, small axis labels."),
        ("smallLightLabel", "Small Light Label", "Smallest light-weight text."),
        ("smallDataLabel", "Small Data Label", "Small text for inline data labels on charts."),
    ]:
        with st.expander(f"📝 {class_label}"):
            st.caption(description)
            if class_key not in tc:
                tc[class_key] = deepcopy(DEFAULT_THEME["textClasses"].get(
                    class_key, {"fontSize": 10, "fontFace": "Segoe UI", "color": "#252423"}))

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
# PAGE: Visual Styles
# ═══════════════════════════════════════════
if current_page == "Visuals":
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

        st.divider()

        # Visual Header
        st.markdown("**Visual Header**")
        vh_cfg = glob.get("visualHeader", [{}])[0] if "visualHeader" in glob else {}
        vh_col1, vh_col2, vh_col3 = st.columns(3)
        with vh_col1:
            vh_show = st.checkbox("Show header", value=vh_cfg.get("show", True), key="glob_vh_show")
        with vh_col2:
            vh_icon_color = st.color_picker(
                "Icon color",
                value=vh_cfg.get("foreground", {}).get("solid", {}).get("color", "#252423"),
                key="glob_vh_icon"
            )
        with vh_col3:
            vh_bg_color = st.color_picker(
                "Header background",
                value=vh_cfg.get("background", {}).get("solid", {}).get("color", "#FFFFFF"),
                key="glob_vh_bg"
            )

        glob["visualHeader"] = [{
            "show": vh_show,
            "foreground": color_fill(vh_icon_color),
            "background": color_fill(vh_bg_color),
        }]

        st.divider()

        # Drop Shadow
        st.markdown("**Drop Shadow**")
        ds_cfg = glob.get("dropShadow", [{}])[0] if "dropShadow" in glob else {}
        ds_col1, ds_col2, ds_col3, ds_col4 = st.columns(4)
        with ds_col1:
            ds_show = st.checkbox("Show shadow", value=ds_cfg.get("show", False), key="glob_ds_show")
        with ds_col2:
            ds_color = st.color_picker(
                "Shadow color",
                value=ds_cfg.get("color", {}).get("solid", {}).get("color", "#000000"),
                key="glob_ds_color"
            )
        with ds_col3:
            ds_preset_opts = ["BottomRight", "Bottom", "BottomLeft", "CenterRight", "Center",
                              "CenterLeft", "TopRight", "Top", "TopLeft", "Custom"]
            ds_preset_val = ds_cfg.get("preset", "BottomRight")
            ds_preset_idx = ds_preset_opts.index(ds_preset_val) if ds_preset_val in ds_preset_opts else 0
            ds_preset = st.selectbox("Preset", ds_preset_opts, index=ds_preset_idx, key="glob_ds_preset")
        with ds_col4:
            ds_blur = st.number_input("Blur", 0, 50, value=int(ds_cfg.get("shadowBlur", 4)), key="glob_ds_blur")

        glob["dropShadow"] = [{
            "show": ds_show,
            "color": color_fill(ds_color),
            "preset": ds_preset,
            "shadowBlur": ds_blur,
        }]

        st.divider()

        # Padding
        st.markdown("**Visual Padding**")
        pad_cfg = glob.get("padding", [{}])[0] if "padding" in glob else {}
        pad_col1, pad_col2, pad_col3, pad_col4 = st.columns(4)
        with pad_col1:
            pad_top = st.number_input("Top", 0, 50,
                                      value=int(pad_cfg.get("top", 8)), key="glob_pad_top")
        with pad_col2:
            pad_right = st.number_input("Right", 0, 50,
                                        value=int(pad_cfg.get("right", 8)), key="glob_pad_right")
        with pad_col3:
            pad_bottom = st.number_input("Bottom", 0, 50,
                                         value=int(pad_cfg.get("bottom", 8)), key="glob_pad_bottom")
        with pad_col4:
            pad_left = st.number_input("Left", 0, 50,
                                       value=int(pad_cfg.get("left", 8)), key="glob_pad_left")

        glob["padding"] = [{"top": pad_top, "right": pad_right, "bottom": pad_bottom, "left": pad_left}]

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

            # ── Axis chart common fields ──
            if vis_key in AXIS_CHART_VISUALS:
                st.markdown("**Category Axis (override)**")
                cat_cfg = vis_cfg.get("categoryAxis", [{}])[0] if "categoryAxis" in vis_cfg else {}
                ca2_c1, ca2_c2, ca2_c3, ca2_c4 = st.columns(4)
                with ca2_c1:
                    ca2_show = st.checkbox("Show axis", value=cat_cfg.get("show", True),
                                           key=f"{vis_key}_ca2_show")
                with ca2_c2:
                    ca2_color = st.color_picker(
                        "Label color",
                        value=cat_cfg.get("labelColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                        key=f"{vis_key}_ca2_color"
                    )
                with ca2_c3:
                    ca2_size = st.number_input("Font size", 6, 24,
                                               value=cat_cfg.get("fontSize", 10),
                                               key=f"{vis_key}_ca2_size")
                with ca2_c4:
                    ca2_grid = st.checkbox("Show gridlines",
                                           value=cat_cfg.get("gridlineShow", False),
                                           key=f"{vis_key}_ca2_grid")

                vis_cfg["categoryAxis"] = [{
                    "show": ca2_show,
                    "labelColor": color_fill(ca2_color),
                    "fontSize": ca2_size,
                    "fontFamily": "Segoe UI",
                    "gridlineShow": ca2_grid,
                }]

                st.markdown("**Value Axis (override)**")
                val2_cfg = vis_cfg.get("valueAxis", [{}])[0] if "valueAxis" in vis_cfg else {}
                va2_c1, va2_c2, va2_c3, va2_c4 = st.columns(4)
                with va2_c1:
                    va2_show = st.checkbox("Show axis", value=val2_cfg.get("show", True),
                                           key=f"{vis_key}_va2_show")
                with va2_c2:
                    va2_color = st.color_picker(
                        "Label color",
                        value=val2_cfg.get("labelColor", {}).get("solid", {}).get("color", "#6B6B6B"),
                        key=f"{vis_key}_va2_color"
                    )
                with va2_c3:
                    va2_grid = st.checkbox("Show gridlines",
                                           value=val2_cfg.get("gridlineShow", True),
                                           key=f"{vis_key}_va2_grid")
                with va2_c4:
                    va2_grid_color = st.color_picker(
                        "Gridline color",
                        value=val2_cfg.get("gridlineColor", {}).get("solid", {}).get("color", "#E0E0E0"),
                        key=f"{vis_key}_va2_grid_color"
                    )

                vis_cfg["valueAxis"] = [{
                    "show": va2_show,
                    "labelColor": color_fill(va2_color),
                    "fontFamily": "Segoe UI",
                    "gridlineShow": va2_grid,
                    "gridlineColor": color_fill(va2_grid_color),
                }]

                st.markdown("**Data Labels**")
                dl_cfg = vis_cfg.get("dataLabels", [{}])[0] if "dataLabels" in vis_cfg else {}
                dl_c1, dl_c2, dl_c3, dl_c4 = st.columns(4)
                with dl_c1:
                    dl_show = st.checkbox("Show data labels",
                                          value=dl_cfg.get("show", False),
                                          key=f"{vis_key}_dl_show")
                with dl_c2:
                    dl_color = st.color_picker(
                        "Label color",
                        value=dl_cfg.get("color", {}).get("solid", {}).get("color", "#252423"),
                        key=f"{vis_key}_dl_color"
                    )
                with dl_c3:
                    dl_size = st.number_input("Font size", 6, 24,
                                              value=dl_cfg.get("fontSize", 9),
                                              key=f"{vis_key}_dl_size")
                with dl_c4:
                    dl_font_val = dl_cfg.get("fontFamily", "Segoe UI")
                    dl_font_idx = FONT_OPTIONS.index(dl_font_val) if dl_font_val in FONT_OPTIONS else 0
                    dl_font = st.selectbox("Font", FONT_OPTIONS, index=dl_font_idx,
                                           key=f"{vis_key}_dl_font")

                vis_cfg["dataLabels"] = [{
                    "show": dl_show,
                    "color": color_fill(dl_color),
                    "fontSize": dl_size,
                    "fontFamily": dl_font,
                }]

            # ── Pie / Donut / Treemap data labels ──
            if vis_key in PIE_CHART_VISUALS:
                st.markdown("**Data Labels**")
                pdl_cfg = vis_cfg.get("dataLabels", [{}])[0] if "dataLabels" in vis_cfg else {}
                pdl_c1, pdl_c2, pdl_c3 = st.columns(3)
                with pdl_c1:
                    pdl_show = st.checkbox("Show data labels",
                                           value=pdl_cfg.get("show", False),
                                           key=f"{vis_key}_pdl_show")
                with pdl_c2:
                    pdl_color = st.color_picker(
                        "Label color",
                        value=pdl_cfg.get("color", {}).get("solid", {}).get("color", "#252423"),
                        key=f"{vis_key}_pdl_color"
                    )
                with pdl_c3:
                    pdl_size = st.number_input("Font size", 6, 24,
                                               value=pdl_cfg.get("fontSize", 9),
                                               key=f"{vis_key}_pdl_size")

                vis_cfg["dataLabels"] = [{
                    "show": pdl_show,
                    "color": color_fill(pdl_color),
                    "fontSize": pdl_size,
                    "fontFamily": "Segoe UI",
                }]

            # ── Gauge specific ──
            if vis_key == "gauge":
                st.markdown("**Gauge Colors**")
                gd_cfg = vis_cfg.get("dataPoint", [{}])[0] if "dataPoint" in vis_cfg else {}
                gd_c1, gd_c2 = st.columns(2)
                with gd_c1:
                    gd_fill = st.color_picker(
                        "Fill color",
                        value=gd_cfg.get("fill", {}).get("solid", {}).get("color", "#118DFF"),
                        key="gauge_fill"
                    )
                with gd_c2:
                    gd_target = st.color_picker(
                        "Target color",
                        value=gd_cfg.get("target", {}).get("solid", {}).get("color", "#252423"),
                        key="gauge_target"
                    )

                vis_cfg["dataPoint"] = [{"fill": color_fill(gd_fill), "target": color_fill(gd_target)}]

                st.markdown("**Callout Value**")
                gcv_cfg = vis_cfg.get("calloutValue", [{}])[0] if "calloutValue" in vis_cfg else {}
                gcv_c1, gcv_c2, gcv_c3 = st.columns(3)
                with gcv_c1:
                    gcv_show = st.checkbox("Show callout value",
                                           value=gcv_cfg.get("show", True), key="gauge_cv_show")
                with gcv_c2:
                    gcv_color = st.color_picker(
                        "Color",
                        value=gcv_cfg.get("color", {}).get("solid", {}).get("color", "#252423"),
                        key="gauge_cv_color"
                    )
                with gcv_c3:
                    gcv_size = st.number_input("Font size", 6, 45,
                                               value=gcv_cfg.get("fontSize", 27),
                                               key="gauge_cv_size")

                vis_cfg["calloutValue"] = [{"show": gcv_show, "color": color_fill(gcv_color),
                                            "fontSize": gcv_size}]

            # ── KPI specific ──
            if vis_key == "kpi":
                st.markdown("**KPI Indicator**")
                kpi_cfg = vis_cfg.get("*", [{}])[0] if "*" in vis_cfg else {}
                kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
                with kpi_c1:
                    kpi_dir_opts = ["Positive", "Negative"]
                    kpi_dir_val = kpi_cfg.get("direction", "Positive")
                    kpi_dir_idx = kpi_dir_opts.index(kpi_dir_val) if kpi_dir_val in kpi_dir_opts else 0
                    kpi_dir = st.selectbox("Direction", kpi_dir_opts, index=kpi_dir_idx,
                                           key="kpi_direction",
                                           help="'High is good' or 'Low is good'")
                with kpi_c2:
                    kpi_font_color = st.color_picker(
                        "Value color",
                        value=kpi_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                        key="kpi_font_color"
                    )
                with kpi_c3:
                    kpi_icon_show = st.checkbox("Show icon",
                                                value=kpi_cfg.get("showIcon", True),
                                                key="kpi_icon_show")

                vis_cfg["*"] = [{
                    "direction": kpi_dir,
                    "fontColor": color_fill(kpi_font_color),
                    "showIcon": kpi_icon_show,
                }]

            # ── Slicer specific ──
            if vis_key in SLICER_VISUALS:
                st.markdown("**Slicer Header**")
                slh_cfg = vis_cfg.get("title", [{}])[0] if "title" in vis_cfg else {}
                slh_c1, slh_c2, slh_c3 = st.columns(3)
                with slh_c1:
                    slh_show = st.checkbox("Show header",
                                           value=slh_cfg.get("show", True),
                                           key=f"{vis_key}_slh_show")
                with slh_c2:
                    slh_color = st.color_picker(
                        "Header color",
                        value=slh_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                        key=f"{vis_key}_slh_color"
                    )
                with slh_c3:
                    slh_size = st.number_input("Header size", 6, 24,
                                               value=slh_cfg.get("fontSize", 10),
                                               key=f"{vis_key}_slh_size")

                vis_cfg["title"] = [{"show": slh_show, "fontColor": color_fill(slh_color),
                                     "fontSize": slh_size, "fontFamily": "Segoe UI Semibold"}]

                st.markdown("**Slicer Items**")
                sli_cfg = vis_cfg.get("data", [{}])[0] if "data" in vis_cfg else {}
                sli_c1, sli_c2 = st.columns(2)
                with sli_c1:
                    sli_color = st.color_picker(
                        "Item font color",
                        value=sli_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                        key=f"{vis_key}_sli_color"
                    )
                with sli_c2:
                    sli_size = st.number_input("Item font size", 6, 24,
                                               value=sli_cfg.get("textSize", 10),
                                               key=f"{vis_key}_sli_size")

                vis_cfg["data"] = [{"fontColor": color_fill(sli_color), "textSize": sli_size}]

            # ── Multi-Row Card specific ──
            if vis_key == "multiRowCard":
                st.markdown("**Card Title**")
                mrc_t_cfg = vis_cfg.get("cardTitle", [{}])[0] if "cardTitle" in vis_cfg else {}
                mrc_c1, mrc_c2, mrc_c3 = st.columns(3)
                with mrc_c1:
                    mrc_t_color = st.color_picker(
                        "Title color",
                        value=mrc_t_cfg.get("fontColor", {}).get("solid", {}).get("color", "#252423"),
                        key="mrc_title_color"
                    )
                with mrc_c2:
                    mrc_t_size = st.number_input("Title size", 6, 24,
                                                 value=mrc_t_cfg.get("fontSize", 12),
                                                 key="mrc_title_size")
                with mrc_c3:
                    mrc_t_font_val = mrc_t_cfg.get("fontFamily", "Segoe UI Semibold")
                    mrc_t_font_idx = FONT_OPTIONS.index(mrc_t_font_val) if mrc_t_font_val in FONT_OPTIONS else 1
                    mrc_t_font = st.selectbox("Title font", FONT_OPTIONS, index=mrc_t_font_idx,
                                              key="mrc_title_font")

                vis_cfg["cardTitle"] = [{"fontColor": color_fill(mrc_t_color),
                                         "fontSize": mrc_t_size, "fontFamily": mrc_t_font}]

                st.markdown("**Data Labels**")
                mrc_d_cfg = vis_cfg.get("dataLabels", [{}])[0] if "dataLabels" in vis_cfg else {}
                mrc_d1, mrc_d2 = st.columns(2)
                with mrc_d1:
                    mrc_d_color = st.color_picker(
                        "Value color",
                        value=mrc_d_cfg.get("color", {}).get("solid", {}).get("color", "#118DFF"),
                        key="mrc_dl_color"
                    )
                with mrc_d2:
                    mrc_d_size = st.number_input("Value size", 6, 45,
                                                 value=mrc_d_cfg.get("fontSize", 18),
                                                 key="mrc_dl_size")

                vis_cfg["dataLabels"] = [{"color": color_fill(mrc_d_color), "fontSize": mrc_d_size}]


# ═══════════════════════════════════════════
# PAGE: JSON Output
# ═══════════════════════════════════════════
if current_page == "JSON":
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
# PAGE: Preview
# ═══════════════════════════════════════════
if current_page == "Preview":
    st.header("Theme Preview")
    st.caption("Approximate preview of how your theme will look in Power BI.")

    page_bg = theme.get("background", "#FFFFFF")
    data_colors = theme.get("dataColors", ["#118DFF"])
    fg = theme.get("foreground", "#252423")
    second_el = theme.get("secondLevelElements", "#605E5C")
    third_el = theme.get("thirdLevelElements", "#F3F2F1")
    accent = theme.get("tableAccent", data_colors[0] if data_colors else "#118DFF")

    # ── Helpers ──────────────────────────────────────────────────────────────
    def get_vis_prop(vis_key, card_name, prop_name, default):
        vs_data = theme.get("visualStyles", {})
        for key in [vis_key, "*"]:
            node = vs_data.get(key, {}).get("*", {})
            if card_name in node:
                items = node[card_name]
                if isinstance(items, list) and len(items) > 0:
                    val = items[0].get(prop_name)
                    if val is not None:
                        return val
        return default

    def get_vis_fill(vis_key, card_name, prop_name, default_color):
        raw = get_vis_prop(vis_key, card_name, prop_name, None)
        if isinstance(raw, dict):
            return raw.get("solid", {}).get("color", default_color)
        return default_color

    def get_title_props(vis_key):
        color = get_vis_fill(vis_key, "title", "fontColor", fg)
        size = get_vis_prop(vis_key, "title", "fontSize", 14)
        font = get_vis_prop(vis_key, "title", "fontFamily", "Segoe UI Semibold")
        return color, size, font

    def get_subtitle_props(vis_key):
        color = get_vis_fill(vis_key, "subTitle", "fontColor", second_el)
        size = get_vis_prop(vis_key, "subTitle", "fontSize", 11)
        return color, size

    def get_container_style(vis_key):
        bg_show = get_vis_prop(vis_key, "background", "show", False)
        bg_color = get_vis_fill(vis_key, "background", "color", page_bg)
        bd_show = get_vis_prop(vis_key, "border", "show", False)
        bd_color = get_vis_fill(vis_key, "border", "color", "#E0E0E0")
        bd_radius = get_vis_prop(vis_key, "border", "radius", 4)
        eff_bg = bg_color if bg_show else "#FFFFFF"
        eff_border = f"1px solid {bd_color}" if bd_show else f"1px solid {third_el}"
        return eff_bg, eff_border, bd_radius

    def get_axis_props(vis_key):
        va_grid_show = get_vis_prop(vis_key, "valueAxis", "gridlineShow", True)
        va_grid_color = get_vis_fill(vis_key, "valueAxis", "gridlineColor", third_el)
        ax_label_color = get_vis_fill(vis_key, "categoryAxis", "labelColor", second_el)
        ax_font_size = get_vis_prop(vis_key, "categoryAxis", "fontSize", 10)
        va_label_color = get_vis_fill(vis_key, "valueAxis", "labelColor", second_el)
        return va_grid_show, va_grid_color, ax_label_color, ax_font_size, va_label_color

    def pbi_tile(title, subtitle, content_svg, width_flex=1, height=240):
        """Render a Power BI-style visual tile (white card with header + SVG content)."""
        t_color, t_size, _ = get_title_props("*")
        s_color, s_size = get_subtitle_props("*")
        header = (
            f'<div style="padding:10px 12px 4px 12px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
            f'<div>'
            f'<div style="font-size:{min(t_size,14)}px;font-weight:600;color:{t_color};'
            f'font-family:Segoe UI,sans-serif;line-height:1.3;">{title}</div>'
            f'{"<div style=\\"font-size:11px;color:" + s_color + ";font-family:Segoe UI,sans-serif;margin-top:1px;\\">" + subtitle + "</div>" if subtitle else ""}'
            f'</div>'
            f'<div style="display:flex;gap:4px;opacity:0.35;margin-top:2px;">'
            f'<svg width="14" height="14" viewBox="0 0 16 16" fill="{second_el}"><circle cx="3" cy="8" r="1.5"/><circle cx="8" cy="8" r="1.5"/><circle cx="13" cy="8" r="1.5"/></svg>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        return (
            f'<div style="flex:{width_flex};background:#FFFFFF;border:1px solid {third_el};'
            f'border-radius:4px;display:flex;flex-direction:column;overflow:hidden;min-height:{height}px;">'
            f'{header}'
            f'<div style="flex:1;padding:0 8px 8px 8px;">{content_svg}</div>'
            f'</div>'
        )

    # ── Data colors and palette swatches ─────────────────────────────────────
    st.subheader("Data Color Palette")
    render_swatch_row(data_colors)
    col_struct, col_sem = st.columns(2)
    with col_struct:
        st.markdown("**Structural Colors**")
        render_swatch_row(
            [theme.get("firstLevelElements", "#252423"), theme.get("secondLevelElements", "#605E5C"),
             theme.get("thirdLevelElements", "#F3F2F1"), theme.get("fourthLevelElements", "#B3B0AD"),
             theme.get("background", "#FFFFFF"), theme.get("secondaryBackground", "#C8C6C4"),
             theme.get("tableAccent", "#118DFF")],
            ["1st", "2nd", "3rd", "4th", "Bg", "2nd Bg", "Accent"]
        )
    with col_sem:
        st.markdown("**Semantic & Gradient**")
        render_swatch_row(
            [theme.get("good", "#2E8B57"), theme.get("neutral", "#D9B300"), theme.get("bad", "#D64554"),
             theme.get("maximum", "#118DFF"), theme.get("center", "#D9B300"), theme.get("minimum", "#DEEFFF")],
            ["Good", "Neutral", "Bad", "Max", "Center", "Min"]
        )

    st.divider()

    # ── Report Canvas ─────────────────────────────────────────────────────────
    color1 = data_colors[0] if len(data_colors) > 0 else "#118DFF"
    color2 = data_colors[1] if len(data_colors) > 1 else "#12239E"
    color3 = data_colors[2] if len(data_colors) > 2 else "#E66C37"
    color4 = data_colors[3] if len(data_colors) > 3 else "#6B007B"
    color5 = data_colors[4] if len(data_colors) > 4 else "#E044A7"

    card_key = "cardVisual" if "cardVisual" in theme.get("visualStyles", {}) else "card"
    if card_key == "cardVisual":
        cv_val_color = get_vis_fill("cardVisual", "value", "fontColor", fg)
        cv_val_size = get_vis_prop("cardVisual", "value", "fontSize", 28)
        cv_lbl_color = get_vis_fill("cardVisual", "label", "fontColor", second_el)
        cv_lbl_size = get_vis_prop("cardVisual", "label", "fontSize", 11)
    else:
        cv_val_color = get_vis_fill("card", "labels", "color", fg)
        cv_val_size = get_vis_prop("card", "labels", "fontSize", 28)
        cv_lbl_color = get_vis_fill("card", "categoryLabels", "color", second_el)
        cv_lbl_size = get_vis_prop("card", "categoryLabels", "fontSize", 11)
    cv_val_display = min(cv_val_size, 30)

    # ── Row 1: KPI Cards ──────────────────────────────────────────────────────
    kpi_data = [
        ("REVENUE", "$2,297,201", color1),
        ("PROFIT", "$286,397", color2),
        ("ORDERS", "5,009", color3),
        ("CUSTOMERS", "793", color4),
        ("QUANTITY", "37,873", color5),
    ]

    kpi_tiles = ""
    for kpi_label, kpi_val, kpi_color in kpi_data:
        icon_svg = (
            f'<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="32" height="32" rx="6" fill="{kpi_color}" opacity="0.15"/>'
            f'<rect x="9" y="13" width="14" height="10" rx="1.5" fill="{kpi_color}"/>'
            f'<rect x="12" y="10" width="8" height="3" rx="1" fill="{kpi_color}" opacity="0.7"/>'
            f'</svg>'
        )
        kpi_tiles += (
            f'<div style="flex:1;background:#FFFFFF;border:1px solid {third_el};border-radius:4px;'
            f'padding:14px 16px;display:flex;align-items:center;gap:12px;">'
            f'{icon_svg}'
            f'<div>'
            f'<div style="font-size:10px;font-weight:600;color:{second_el};font-family:Segoe UI,sans-serif;'
            f'letter-spacing:0.05em;text-transform:uppercase;">{kpi_label}</div>'
            f'<div style="font-size:{cv_val_display}px;font-weight:400;color:{cv_val_color};'
            f'font-family:Segoe UI,sans-serif;line-height:1.2;margin-top:2px;">{kpi_val}</div>'
            f'</div>'
            f'</div>'
        )

    # ── Row 2a: Stacked Column Chart SVG ─────────────────────────────────────
    col_grid_show, col_grid_color, col_ax_color, col_ax_size, col_va_color = get_axis_props("stackedColumnChart")
    col_title_color, col_title_size, _ = get_title_props("stackedColumnChart")

    months_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    col_data = [
        [22000, 18000, 12000],
        [18000, 14000, 9000],
        [30000, 24000, 16000],
        [26000, 20000, 13000],
        [24000, 19000, 12000],
        [20000, 16000, 11000],
        [28000, 22000, 14000],
        [25000, 20000, 13000],
        [32000, 26000, 17000],
        [29000, 23000, 15000],
        [35000, 28000, 19000],
        [31000, 25000, 16000],
    ]
    col_segment_colors = [color1, color2, color3]
    col_max = max(sum(m) for m in col_data)

    sc_w, sc_h = 560, 190
    sc_l, sc_t, sc_r, sc_b = 42, 10, 550, 155
    sc_cw = sc_r - sc_l
    sc_ch = sc_b - sc_t
    n_cols = len(col_data)
    grp_w = sc_cw / n_cols
    bar_w = grp_w * 0.6

    col_svg = f'<svg viewBox="0 0 {sc_w} {sc_h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Segoe UI,sans-serif;width:100%;height:100%;">'

    # Y gridlines + labels
    for tick_pct in [0, 25, 50, 75, 100]:
        tick_val = int(col_max * tick_pct / 100)
        y = sc_b - (tick_pct / 100) * sc_ch
        if col_grid_show and tick_pct > 0:
            col_svg += f'<line x1="{sc_l}" y1="{y}" x2="{sc_r}" y2="{y}" stroke="{col_grid_color}" stroke-width="0.8" stroke-dasharray="3,3"/>'
        label_str = f"${tick_val//1000}K" if tick_val >= 1000 else str(tick_val)
        col_svg += f'<text x="{sc_l - 4}" y="{y + 4}" text-anchor="end" font-size="9" fill="{col_va_color}">{label_str}</text>'

    # Stacked bars
    for i, vals in enumerate(col_data):
        cx = sc_l + i * grp_w + grp_w / 2
        x = cx - bar_w / 2
        y_cursor = sc_b
        for j, v in enumerate(vals):
            bh = (v / col_max) * sc_ch
            y_cursor -= bh
            col_svg += f'<rect x="{x:.1f}" y="{y_cursor:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{col_segment_colors[j % 3]}"/>'
        col_svg += f'<text x="{cx:.1f}" y="{sc_b + 12}" text-anchor="middle" font-size="9" fill="{col_ax_color}">{months_short[i]}</text>'

    # Legend
    for j, seg_label in enumerate(["Consumer", "Corporate", "Home Office"]):
        lx = sc_l + j * 105
        col_svg += f'<rect x="{lx}" y="{sc_b + 22}" width="8" height="8" rx="1.5" fill="{col_segment_colors[j]}"/>'
        col_svg += f'<text x="{lx + 12}" y="{sc_b + 30}" font-size="9" fill="{col_ax_color}">{seg_label}</text>'

    col_svg += '</svg>'

    bar_tile = pbi_tile("Sales Performance", "by Segment", col_svg, width_flex=2, height=260)

    # ── Row 2b: Donut Chart SVG ───────────────────────────────────────────────
    donut_data = [("Office Supplies", 2800, color1), ("Furniture", 1300, color2), ("Technology", 900, color3)]
    donut_total = sum(v for _, v, _ in donut_data)

    dn_w, dn_h = 260, 190
    cx_d, cy_d = 110, 95
    r_outer, r_inner = 75, 45
    start_angle = -math.pi / 2

    donut_svg = f'<svg viewBox="0 0 {dn_w} {dn_h}" xmlns="http://www.w3.org/2000/svg" style="font-family:Segoe UI,sans-serif;width:100%;height:100%;">'

    angle = start_angle
    for seg_label, seg_val, seg_color in donut_data:
        sweep = (seg_val / donut_total) * 2 * math.pi
        x1o = cx_d + r_outer * math.cos(angle)
        y1o = cy_d + r_outer * math.sin(angle)
        x1i = cx_d + r_inner * math.cos(angle)
        y1i = cy_d + r_inner * math.sin(angle)
        angle += sweep
        x2o = cx_d + r_outer * math.cos(angle)
        y2o = cy_d + r_outer * math.sin(angle)
        x2i = cx_d + r_inner * math.cos(angle)
        y2i = cy_d + r_inner * math.sin(angle)
        large = 1 if sweep > math.pi else 0
        path = (
            f"M {x1o:.2f} {y1o:.2f} "
            f"A {r_outer} {r_outer} 0 {large} 1 {x2o:.2f} {y2o:.2f} "
            f"L {x2i:.2f} {y2i:.2f} "
            f"A {r_inner} {r_inner} 0 {large} 0 {x1i:.2f} {y1i:.2f} Z"
        )
        donut_svg += f'<path d="{path}" fill="{seg_color}" stroke="white" stroke-width="2"/>'

    # Centre label
    donut_svg += f'<text x="{cx_d}" y="{cy_d - 6}" text-anchor="middle" font-size="9" fill="{second_el}">ORDERS</text>'
    donut_svg += f'<text x="{cx_d}" y="{cy_d + 12}" text-anchor="middle" font-size="18" font-weight="600" fill="{fg}">{donut_total:,}</text>'

    # Legend
    for j, (seg_label, seg_val, seg_color) in enumerate(donut_data):
        ly = 22 + j * 18
        donut_svg += f'<circle cx="{dn_w - 80}" cy="{ly}" r="5" fill="{seg_color}"/>'
        donut_svg += f'<text x="{dn_w - 72}" y="{ly + 4}" font-size="9" fill="{second_el}">{seg_label}</text>'

    donut_svg += '</svg>'

    donut_tile = pbi_tile("Orders by Category", "", donut_svg, width_flex=1, height=260)

    # ── Row 3: Table ──────────────────────────────────────────────────────────
    tbl_accent = theme.get("tableAccent", accent)
    tbl_header_bg = tbl_accent
    tbl_row_alt = third_el

    table_rows = [
        ("CA-2014-100006", "07 Sep 2014", "DK-13375", "Dennis Kane",    "Standard Class", "United States", "New York City", "New York",    "East",  "3",  "$378"),
        ("CA-2014-100090", "08 Jul 2014", "EB-13705", "Ed Braxton",     "Standard Class", "United States", "San Francisco", "California",  "West",  "9",  "$699"),
        ("CA-2014-100293", "14 Mar 2014", "NF-18475", "Neil Franzósisch","Standard Class","United States", "Jacksonville", "Florida",     "South", "6",  "$91"),
        ("CA-2014-100328", "28 Jan 2014", "JC-15340", "Jasper Cacioppo","Standard Class", "United States", "New York City", "New York",    "East",  "1",  "$4"),
    ]
    tbl_cols = ["Order ID", "Order Date", "Customer ID", "Customer Name", "Ship Mode", "Country", "City", "State", "Region", "Qty", "Sales"]

    def _tc(txt, bg, color, bold=False, align="left"):
        fw = "600" if bold else "400"
        return (
            f'<td style="padding:5px 8px;background:{bg};color:{color};font-size:10px;'
            f'font-weight:{fw};text-align:{align};font-family:Segoe UI,sans-serif;'
            f'border-bottom:1px solid {third_el};white-space:nowrap;">{txt}</td>'
        )

    tbl_html = (
        f'<div style="overflow-x:auto;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr>'
    )
    for col_name in tbl_cols:
        tbl_html += f'<th style="padding:6px 8px;background:{tbl_header_bg};color:#FFFFFF;font-size:10px;font-weight:600;text-align:left;font-family:Segoe UI,sans-serif;white-space:nowrap;">{col_name}</th>'
    tbl_html += '</tr></thead><tbody>'
    for ri, row in enumerate(table_rows):
        row_bg = tbl_row_alt if ri % 2 == 1 else "#FFFFFF"
        tbl_html += '<tr>'
        for ci, cell in enumerate(row):
            tbl_html += _tc(cell, row_bg, fg, align="right" if ci >= 9 else "left")
        tbl_html += '</tr>'
    tbl_html += '</tbody></table></div>'

    table_tile = pbi_tile("Order Log", "", tbl_html, width_flex=1, height=180)

    # ── Assemble the report canvas ────────────────────────────────────────────
    vs = theme.get("visualStyles", {})
    page_vis = vs.get("page", {}).get("*", {})
    page_bg_items = page_vis.get("background", [{}])
    if isinstance(page_bg_items, list) and page_bg_items:
        canvas_bg_raw = page_bg_items[0].get("color", {})
        if isinstance(canvas_bg_raw, dict):
            canvas_bg = canvas_bg_raw.get("solid", {}).get("color", page_bg)
        else:
            canvas_bg = page_bg
    else:
        canvas_bg = page_bg

    report_html = f"""
<div style="background:{canvas_bg};padding:16px;border-radius:4px;border:1px solid {third_el};font-family:Segoe UI,sans-serif;">
  <!-- KPI row -->
  <div style="display:flex;gap:10px;margin-bottom:10px;">
    {kpi_tiles}
  </div>
  <!-- Charts row -->
  <div style="display:flex;gap:10px;margin-bottom:10px;">
    {bar_tile}
    {donut_tile}
  </div>
  <!-- Table row -->
  <div style="display:flex;gap:10px;">
    {table_tile}
  </div>
</div>
"""
    st.markdown(report_html, unsafe_allow_html=True)

    st.divider()

    # ── Typography & gradient ─────────────────────────────────────────────────
    col_typo, col_grad = st.columns([1, 1])
    with col_typo:
        st.subheader("Typography Classes")
        for cls_key, cls_label in [("callout", "Callout"), ("title", "Title"), ("header", "Header"), ("label", "Label")]:
            tc_item = theme.get("textClasses", {}).get(cls_key, {})
            font = tc_item.get("fontFace", "Segoe UI")
            size = tc_item.get("fontSize", 10)
            color = tc_item.get("color", "#252423")
            preview_size = min(size, 36)
            st.markdown(
                f'<div style="font-family:{font},sans-serif;font-size:{preview_size}px;color:{color};'
                f'padding:2px 0;">{cls_label}: {font} {size}pt</div>',
                unsafe_allow_html=True,
            )
    with col_grad:
        st.subheader("Conditional Formatting Gradient")
        grad_colors = [theme.get("minimum", "#DEEFFF"), theme.get("center", "#D9B300"), theme.get("maximum", "#118DFF")]
        grad_html = (
            f'<div style="height:28px;border-radius:6px;margin-top:8px;'
            f'background:linear-gradient(to right, {grad_colors[0]}, {grad_colors[1]}, {grad_colors[2]});'
            f'border:1px solid {third_el};"></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:10px;color:{second_el};">'
            f'<span>Minimum</span><span>Center</span><span>Maximum</span></div>'
        )
        st.markdown(grad_html, unsafe_allow_html=True)
