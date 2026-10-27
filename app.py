
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse

st.set_page_config(
    page_title="CampusPulse | Student Portal",
    page_icon="🎓",
    layout="wide",
)

# Espresso-only palette
BG = "#17110F"
SURFACE = "rgba(57, 39, 31, 0.72)"
SURFACE2 = "rgba(73, 51, 41, 0.62)"
TEXT = "#F7EEE5"
MUTED = "#C7B3A4"
BORDER = "rgba(226, 199, 177, 0.18)"
ACCENT = "#D6A783"
ACCENT_HOVER = "#E2B997"
ACCENT_TEXT = "#241610"
INPUT = "#2B1E18"

st.markdown(f"""
<style>
:root {{
  color-scheme: dark;
  --primary-color: {ACCENT} !important;
  --st-primary-color: {ACCENT} !important;
}}

.stApp {{
  background:
    radial-gradient(ellipse at 8% 4%, #302019 0%, transparent 38%),
    radial-gradient(ellipse at 92% 20%, #493126 0%, transparent 32%),
    {BG};
  color: {TEXT};
}}

[data-testid="stHeader"],
[data-testid="stToolbar"] {{
  background: transparent !important;
}}

.block-container {{
  max-width: 1080px;
  padding-top: 1.4rem;
  padding-bottom: 3rem;
}}

h1, h2, h3, p, label,
[data-testid="stMarkdownContainer"] {{
  color: {TEXT};
}}

[data-testid="stCaptionContainer"] {{
  color: {MUTED} !important;
}}

.cp-hero {{
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding: clamp(1.5rem, 5vw, 3rem);
  border: 1px solid rgba(255,255,255,.16);
  border-radius: 28px;
  background: linear-gradient(125deg, #211511 0%, #493126 48%, #76513C 100%);
  box-shadow: 0 20px 55px rgba(0,0,0,.28);
  margin: .4rem 0 1.5rem;
}}

.cp-hero::after {{
  content: "";
  position: absolute;
  z-index: -1;
  width: 240px;
  height: 240px;
  right: -65px;
  top: -105px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.17);
  box-shadow: 0 0 0 28px rgba(255,255,255,.045),
              0 0 0 58px rgba(255,255,255,.035);
}}

.cp-eyebrow {{
  color: #F4DCC8;
  font-size: .75rem;
  letter-spacing: .19em;
  font-weight: 800;
  text-transform: uppercase;
}}

.cp-hero-title {{
  color: #FFF8F1 !important;
  font-size: clamp(2.4rem, 7vw, 4rem);
  line-height: 1.04;
  font-weight: 850;
  letter-spacing: -.045em;
  margin: .7rem 0;
}}

.cp-hero-copy {{
  color: #F7E8DC !important;
  max-width: 650px;
  font-size: 1.02rem;
  line-height: 1.8;
}}

.cp-hero-chip {{
  display: inline-block;
  margin-top: .7rem;
  padding: .5rem .85rem;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: 999px;
  background: rgba(255,255,255,.09);
  color: #FFF8F1;
  font-size: .82rem;
}}

.cp-panel {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 20px;
  padding: clamp(1rem, 3vw, 1.6rem);
  box-shadow: 0 14px 35px rgba(0,0,0,.18);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  margin: .6rem 0 1rem;
}}

.cp-label {{
  color: {MUTED};
  font-size: .73rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: .35rem;
}}

.cp-value {{
  color: {TEXT};
  background: {SURFACE2};
  border: 1px solid {BORDER};
  padding: .7rem .85rem;
  border-radius: 12px;
  overflow-wrap: anywhere;
}}

.cp-muted {{
  color: {MUTED};
  text-align: center;
  font-size: .82rem;
  line-height: 1.7;
  padding: 1.2rem .5rem;
}}

/* Tabs and active underline: force the mocha accent. */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
  gap: .45rem !important;
  border-bottom: 1px solid {BORDER} !important;
}}

[data-testid="stTabs"] button[data-baseweb="tab"] {{
  color: {MUTED} !important;
  border-radius: 12px 12px 0 0 !important;
  font-weight: 700 !important;
  border-bottom: 2px solid transparent !important;
  box-shadow: none !important;
}}

[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
  color: {ACCENT} !important;
  background: rgba(214,167,131,.10) !important;
  border-bottom: 2px solid {ACCENT} !important;
  box-shadow: inset 0 -2px 0 {ACCENT} !important;
}}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"],
[data-testid="stTabs"] [data-baseweb="tab-list"] > div[role="presentation"] {{
  background: {ACCENT} !important;
  background-color: {ACCENT} !important;
  border-color: {ACCENT} !important;
  color: {ACCENT} !important;
}}

[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
  padding-top: 1.3rem;
}}

/* Primary buttons */
[data-testid="stFormSubmitButton"] button,
[data-testid="stLinkButton"] a,
.stButton button[kind="primary"],
button[kind="primary"] {{
  background: {ACCENT} !important;
  background-color: {ACCENT} !important;
  color: {ACCENT_TEXT} !important;
  border: 1px solid {ACCENT} !important;
  border-radius: 12px !important;
  font-weight: 750 !important;
  min-height: 2.8rem;
  box-shadow: 0 6px 18px rgba(0,0,0,.16);
  transition: background .18s ease, transform .18s ease;
}}

[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stLinkButton"] a:hover,
.stButton button[kind="primary"]:hover,
button[kind="primary"]:hover {{
  background: {ACCENT_HOVER} !important;
  background-color: {ACCENT_HOVER} !important;
  color: {ACCENT_TEXT} !important;
  border-color: {ACCENT_HOVER} !important;
  transform: translateY(-1px);
}}

[data-testid="stFormSubmitButton"] button p,
[data-testid="stLinkButton"] a p,
button[kind="primary"] p {{
  color: {ACCENT_TEXT} !important;
}}

/* Inputs and forms */
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
[data-baseweb="select"] > div {{
  background: {INPUT} !important;
  border-color: {BORDER} !important;
  border-radius: 12px !important;
}}

[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {{
  color: {TEXT} !important;
}}

[data-testid="stForm"] {{
  background: {SURFACE};
  border: 1px solid {BORDER} !important;
  border-radius: 18px;
  padding: clamp(.8rem, 2.5vw, 1.4rem);
}}

[data-testid="stAlert"] {{
  border-radius: 13px;
}}

hr {{
  border-color: {BORDER} !important;
}}

::selection {{
  background: {ACCENT};
  color: {ACCENT_TEXT};
}}

@media (max-width: 640px) {{
  .block-container {{
    padding: .8rem .8rem 2rem;
  }}
  .cp-hero {{
    border-radius: 20px;
  }}
  .cp-hero-copy {{
    font-size: .94rem;
  }}
  [data-testid="stTabs"] [data-baseweb="tab-list"] {{
    gap: .05rem !important;
  }}
  [data-testid="stTabs"] button[data-baseweb="tab"] {{
    padding-left: .45rem;
    padding-right: .45rem;
    font-size: .78rem;
  }}
}}
</style>
""", unsafe_allow_html=True)


# ── Google Sheets helpers ───────────────────────────────────
def get_setting(section, key, default=""):
    try:
        return st.secrets[section].get(key, default)
    except Exception:
        return default


def get_gspread_client():
    try:
        service_account_info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        credentials = Credentials.from_service_account_info(
            service_account_info, scopes=scopes
        )
        return gspread.authorize(credentials)
    except KeyError as exc:
        raise RuntimeError(
            "Google Sheets credentials are not configured. Add the "
            "[gcp_service_account] section to Streamlit secrets."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            "Could not initialise Google Sheets access. Check the service-account secrets."
        ) from exc


def clean(value):
    return "" if value is None else str(value).strip()


def normalise_header(value):
    return "".join(ch.lower() for ch in clean(value) if ch.isalnum())


def find_header(headers, configured_name, aliases=()):
    wanted = [configured_name, *aliases]
    normalised = {normalise_header(h): h for h in headers}
    for name in wanted:
        if name and normalise_header(name) in normalised:
            return normalised[normalise_header(name)]
    return None


def read_ticket(ticket_id):
    spreadsheet_id = get_setting("google_sheets", "spreadsheet_id")
    worksheet_name = get_setting("google_sheets", "worksheet_name", "Tickets")

    if not spreadsheet_id:
        raise RuntimeError("Missing google_sheets.spreadsheet_id in Streamlit secrets.")

    client = get_gspread_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    rows = worksheet.get_all_records()

    if not rows:
        return None

    headers = list(rows[0].keys())
    configured = st.secrets.get("columns", {})
    ticket_col = find_header(
        headers,
        configured.get("ticket_id", "Ticket_ID"),
        aliases=("Ticket ID", "TicketID", "ticket_id", "ID"),
    )

    if not ticket_col:
        raise RuntimeError(
            "Could not find the ticket ID column. Set [columns].ticket_id "
            "in Streamlit secrets to the exact header in your Tickets worksheet."
        )

    matches = [
        row for row in rows
        if clean(row.get(ticket_col)).casefold() == ticket_id.casefold()
    ]

    if not matches:
        return None

    return matches[0], headers, len(matches)


def safe_field(row, headers, configured_name, aliases=()):
    col = find_header(headers, configured_name, aliases)
    return clean(row.get(col)) if col else ""


def status_colour(status):
    s = status.lower()
    if any(word in s for word in ("resolv", "clos", "complet")):
        return "#356B4A"
    if any(word in s for word in ("critical", "urgent", "escalat")):
        return "#9F493D"
    if any(word in s for word in ("progress", "acknow", "review")):
        return "#95664F"
    return "#81756D"


# ── Hero ────────────────────────────────────────────────────
st.markdown("""
<div class="cp-hero">
  <div class="cp-eyebrow">Student support · Campus community</div>
  <div class="cp-hero-title">CampusPulse</div>
  <p class="cp-hero-copy">
    Your campus. Your voice. A clearer way to report an issue,
    follow its progress, and help make campus life better.
  </p>
  <span class="cp-hero-chip">☕ Thoughtful support, one report at a time</span>
</div>
""", unsafe_allow_html=True)

try:
    form_url = st.secrets["google_sheets"]["google_form_url"]
except Exception:
    form_url = ""

track_tab, register_tab = st.tabs([
    "🔎 Track my complaint",
    "📝 Register new complaint",
])

with track_tab:
    st.subheader("Track your complaint")
    st.caption("Enter the ticket ID you received after submitting your complaint.")

    with st.form("ticket_lookup", clear_on_submit=False):
        ticket_id = st.text_input(
            "Ticket ID",
            placeholder="e.g. TEST-CP-0001",
            help="Enter the complete ticket ID exactly as shown in your acknowledgement email.",
        ).strip()

        submitted = st.form_submit_button(
            "Search ticket", type="primary", use_container_width=True
        )

    if submitted:
        if not ticket_id:
            st.warning("Please enter a ticket ID.")
        else:
            try:
                with st.spinner("Looking up your ticket..."):
                    result = read_ticket(ticket_id)

                if result is None:
                    st.error(
                        "We couldn't find a complaint with that ticket ID. "
                        "Check the ID and try again."
                    )
                else:
                    row, headers, match_count = result
                    columns = st.secrets.get("columns", {})

                    display_fields = [
                        ("Ticket ID", columns.get("ticket_id", "Ticket_ID"), ("Ticket ID", "TicketID", "ID")),
                        ("Status", columns.get("status", "Status"), ("Current Status", "Ticket Status")),
                        ("Category", columns.get("category", "Category"), ("Complaint Category",)),
                        ("Severity", columns.get("severity", "Severity"), ("Severity Level",)),
                        ("Location", columns.get("location", "Location"), ("Campus Location",)),
                        ("Submitted", columns.get("submitted_at", "Timestamp"), ("Submitted At", "Submission Date", "Created At")),
                    ]

                    st.subheader("Complaint details")

                    actual_status = safe_field(
                        row, headers, columns.get("status", "Status"),
                        ("Current Status", "Ticket Status"),
                    )

                    if actual_status:
                        colour = status_colour(actual_status)
                        st.markdown(
                            f'<span style="display:inline-block;background:{colour};color:#fff;'
                            f'padding:.4rem .8rem;border-radius:999px;font-weight:700;">'
                            f'{actual_status}</span>',
                            unsafe_allow_html=True,
                        )
                        st.write("")
                    else:
                        st.info(
                            "A status field is not currently available in the configured worksheet."
                        )

                    visible = []
                    for label, configured_name, aliases in display_fields:
                        value = safe_field(row, headers, configured_name, aliases)
                        if value:
                            visible.append((label, value))

                    summary = safe_field(
                        row, headers, columns.get("summary", "Summary"),
                        ("Complaint Summary", "Description", "Report Text", "Complaint"),
                    )

                    update_note = safe_field(
                        row, headers, columns.get("resolution_note", "Resolution_Note"),
                        ("Resolution Note", "Latest Update", "Admin Note"),
                    )

                    if summary:
                        st.markdown("**Complaint summary**")
                        st.write(summary)

                    left, right = st.columns(2)
                    for index, (label, value) in enumerate(visible):
                        with (left if index % 2 == 0 else right):
                            st.markdown(
                                f'<div class="cp-label">{label}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="cp-value">{value}</div>',
                                unsafe_allow_html=True,
                            )
                            st.write("")

                    if update_note:
                        st.markdown("**Latest update**")
                        st.write(update_note)

                    if match_count > 1:
                        st.warning(
                            "More than one row has this ticket ID. "
                            "Please ask the administrator to check the sheet."
                        )

                    st.caption("Only fields configured for student display are shown.")

            except Exception as exc:
                st.error("Ticket lookup could not be completed.")
                st.caption(str(exc))
                st.info(
                    "Check the worksheet name, column mappings, Google Sheet sharing, "
                    "and Streamlit secrets."
                )

with register_tab:
    st.subheader("Raise a campus concern")
    st.write(
        "Share your concern through the official form. Once you submit it, keep the "
        "ticket ID from your acknowledgement email so you can follow its progress here."
    )

    if form_url and urlparse(form_url).scheme == "https":
        st.link_button(
            "Open complaint form ↗",
            form_url,
            type="primary",
            use_container_width=True,
        )
    else:
        st.warning("The Google Form URL has not been configured yet.")
        st.caption("Add google_form_url under [google_sheets] in Streamlit secrets.")

st.divider()
st.markdown(
    '<div class="cp-muted">CampusPulse · Student portal · '
    'For urgent or immediate safety risks, contact campus authorities directly.</div>',
    unsafe_allow_html=True,
)
