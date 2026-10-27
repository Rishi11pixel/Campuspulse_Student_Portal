
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from html import escape
from urllib.parse import urlparse

st.set_page_config(
    page_title="CampusPulse | Student Portal",
    page_icon="🎓",
    layout="wide",
)

# Espresso-only palette
BG = "#17110F"
SURFACE = "rgba(57, 39, 31, 0.72)"
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
    radial-gradient(ellipse at 18% 22%, rgba(108, 65, 43, .48), transparent 38%),
    radial-gradient(ellipse at 78% 18%, rgba(105, 70, 50, .32), transparent 34%),
    radial-gradient(ellipse at 72% 78%, rgba(74, 48, 38, .4), transparent 40%),
    radial-gradient(ellipse at 14% 82%, rgba(57, 38, 31, .45), transparent 35%),
    {BG};
  background-size: 140% 140%, 140% 140%, 140% 140%, 140% 140%, auto;
  background-position: 0% 0%, 100% 0%, 100% 100%, 0% 100%, center;
  background-attachment: fixed;
  animation: cp-ambient-drift 32s ease-in-out infinite alternate;
  color: {TEXT};
}}

@keyframes cp-ambient-drift {{
  from {{ background-position: 0% 0%, 100% 0%, 100% 100%, 0% 100%, center; }}
  to {{ background-position: 8% 6%, 92% 8%, 92% 92%, 8% 94%, center; }}
}}

[data-testid="stHeader"],
[data-testid="stToolbar"] {{
  background: transparent !important;
}}

.block-container {{
  max-width: 1160px;
  padding-top: 1.8rem;
  padding-bottom: 3.5rem;
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
  background:
    radial-gradient(ellipse at 90% 15%, rgba(238, 196, 159, .2), transparent 32%),
    linear-gradient(125deg, rgba(33,21,17,.96) 0%, rgba(73,49,38,.96) 50%, rgba(104,70,51,.96) 100%);
  box-shadow: 0 24px 64px rgba(0,0,0,.32);
  margin: .5rem 0 1.8rem;
}}

.cp-hero::before {{
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  opacity: .14;
  background-image: radial-gradient(rgba(255,244,232,.55) .7px, transparent .7px);
  background-size: 18px 18px;
  mask-image: linear-gradient(115deg, transparent 10%, #000 100%);
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
  animation: cp-orbit-breathe 12s ease-in-out infinite alternate;
  will-change: transform;
}}

@keyframes cp-orbit-breathe {{
  from {{ transform: translate3d(0, 0, 0) scale(.96); opacity: .72; }}
  to {{ transform: translate3d(-10px, 8px, 0) scale(1.04); opacity: 1; }}
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
  margin: .65rem 0 .55rem;
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

.cp-section-kicker {{
  color: {ACCENT};
  font-size: .72rem;
  font-weight: 800;
  letter-spacing: .14em;
  text-transform: uppercase;
  margin: 0 0 .25rem;
}}

.cp-trust-note {{
  display: flex;
  align-items: flex-start;
  gap: .65rem;
  padding: .8rem 1rem;
  border: 1px solid {BORDER};
  border-radius: 14px;
  background: rgba(255,255,255,.035);
  color: {MUTED};
  font-size: .86rem;
  line-height: 1.6;
  margin: .85rem 0 0;
}}

.cp-result-card {{
  padding: 1.2rem;
  border: 1px solid {BORDER};
  border-radius: 18px;
  background: linear-gradient(145deg, rgba(73,51,41,.52), rgba(43,30,24,.55));
  margin: .75rem 0 1rem;
}}

.cp-result-heading {{
  color: {TEXT};
  font-size: 1.08rem;
  font-weight: 750;
  margin: 0 0 .9rem;
}}

.cp-result-topline {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: .75rem;
  margin-bottom: .85rem;
}}

.cp-result-topline .cp-result-heading {{
  margin: 0;
}}

.cp-status-pill {{
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  padding: .38rem .72rem;
  border-radius: 999px;
  color: #fff;
  font-size: .79rem;
  font-weight: 750;
  line-height: 1.35;
}}

.cp-result-copy {{
  color: {MUTED};
  line-height: 1.7;
  overflow-wrap: anywhere;
}}

.cp-result-copy strong {{
  display: block;
  color: {TEXT};
  font-size: .76rem;
  letter-spacing: .08em;
  margin: 1rem 0 .35rem;
  text-transform: uppercase;
}}

.cp-field-grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .7rem;
  margin-top: 1rem;
}}

.cp-field {{
  min-width: 0;
  padding: .85rem .95rem;
  border: 1px solid {BORDER};
  border-radius: 13px;
  background: rgba(255,255,255,.035);
}}

.cp-field .cp-label {{
  margin-bottom: .4rem;
}}

.cp-value {{
  color: {TEXT};
  line-height: 1.5;
  overflow-wrap: anywhere;
}}

.cp-label {{
  color: {MUTED};
  font-size: .73rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: .35rem;
}}

.cp-muted {{
  color: {MUTED};
  text-align: center;
  font-size: .82rem;
  line-height: 1.7;
  padding: 1.2rem .5rem;
}}

[data-testid="stDecoration"] {{
  display: none !important;
}}

/* Primary buttons */
[data-testid="stButton"] button {{
  min-height: 3rem;
  border-radius: 14px !important;
  font-weight: 750 !important;
  transition: background .18s ease, border-color .18s ease, transform .18s ease;
}}

[data-testid="stButton"] button:not([kind="primary"]) {{
  color: {TEXT} !important;
  background: rgba(57, 39, 31, .76) !important;
  border: 1px solid {BORDER} !important;
  box-shadow: 0 8px 22px rgba(0,0,0,.12);
}}

[data-testid="stButton"] button:not([kind="primary"]):hover {{
  color: {ACCENT_HOVER} !important;
  background: rgba(73, 51, 41, .9) !important;
  border-color: rgba(226,199,177,.34) !important;
}}

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
[data-testid="stButton"] button[kind="primary"]:hover,
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
[data-testid="stButton"] button[kind="primary"] p,
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

[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within,
[data-baseweb="select"] > div:focus-within {{
  border-color: {ACCENT} !important;
  box-shadow: 0 0 0 2px rgba(214,167,131,.2) !important;
}}

[data-testid="stButton"] button:focus-visible,
[data-testid="stFormSubmitButton"] button:focus-visible,
[data-testid="stLinkButton"] a:focus-visible,
button:focus-visible {{
  outline: 3px solid {ACCENT_HOVER} !important;
  outline-offset: 3px !important;
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
  .cp-field-grid {{
    grid-template-columns: 1fr;
  }}
  [data-testid="stButton"] button {{
    min-height: 3.2rem;
    font-size: .9rem;
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  *,
  *::before,
  *::after {{
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    will-change: auto !important;
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
def select_portal_section(section):
    st.session_state["portal_section"] = section


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

if "portal_section" not in st.session_state:
    st.session_state["portal_section"] = "track"

nav_track, nav_register = st.columns(2, gap="small")
with nav_track:
    st.button(
        "🔎  Track my complaint",
        key="track_section_button",
        type="primary" if st.session_state["portal_section"] == "track" else "secondary",
        use_container_width=True,
        on_click=select_portal_section,
        args=("track",),
    )
with nav_register:
    st.button(
        "📝  Register a complaint",
        key="register_section_button",
        type="primary" if st.session_state["portal_section"] == "register" else "secondary",
        use_container_width=True,
        on_click=select_portal_section,
        args=("register",),
    )

if st.session_state["portal_section"] == "track":
    st.markdown('<div class="cp-section-kicker">Your report, at a glance</div>', unsafe_allow_html=True)
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

    st.markdown(
        '<div class="cp-trust-note"><span>🔒</span><span>Your lookup only shows '
        'student-facing details for the matching ticket. Keep your ticket ID private.</span></div>',
        unsafe_allow_html=True,
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

                    actual_status = safe_field(
                        row, headers, columns.get("status", "Status"),
                        ("Current Status", "Ticket Status"),
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

                    status_html = ""
                    if actual_status:
                        status_html = (
                            f'<span class="cp-status-pill" style="background:{status_colour(actual_status)}">'
                            f'{escape(actual_status)}</span>'
                        )

                    fields_html = "".join(
                        '<div class="cp-field">'
                        f'<div class="cp-label">{escape(label)}</div>'
                        f'<div class="cp-value">{escape(value)}</div>'
                        '</div>'
                        for label, value in visible
                    )
                    summary_html = (
                        f'<div class="cp-result-copy"><strong>Complaint summary</strong>'
                        f'{escape(summary)}</div>'
                        if summary else ""
                    )
                    update_html = (
                        f'<div class="cp-result-copy"><strong>Latest update</strong>'
                        f'{escape(update_note)}</div>'
                        if update_note else ""
                    )
                    status_note_html = (
                        '<div class="cp-result-copy">A status field is not currently '
                        'available in the configured worksheet.</div>'
                        if not actual_status else ""
                    )
                    st.markdown(
                        '<div class="cp-result-card">'
                        '<div class="cp-result-topline">'
                        '<div class="cp-result-heading">Complaint details</div>'
                        f'{status_html}</div>'
                        f'{status_note_html}'
                        f'{summary_html}'
                        f'<div class="cp-field-grid">{fields_html}</div>'
                        f'{update_html}'
                        '</div>',
                        unsafe_allow_html=True,
                    )

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

else:
    st.markdown('<div class="cp-section-kicker">Make campus better</div>', unsafe_allow_html=True)
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
    '<div class="cp-muted">CampusPulse · Student portal</div>',
    unsafe_allow_html=True,
)
