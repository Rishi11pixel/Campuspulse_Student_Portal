import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse
from datetime import datetime

st.set_page_config(
    page_title="CampusPulse | Student Portal",
    page_icon="🎓",
    layout="centered",
)

# CampusPulse Espresso & Persimmon palette

def get_setting(section, key, default=""):
    try:
        return st.secrets[section].get(key, default)
    except Exception:
        return default

def get_gspread_client():
    try:
        service_account_info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        return gspread.authorize(credentials)
    except KeyError as exc:
        raise RuntimeError(
            "Google Sheets credentials are not configured. Add the [gcp_service_account] "
            "section to Streamlit secrets."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            "Could not initialise Google Sheets access. Check the service-account secrets."
        ) from exc

def clean(value):
    if value is None:
        return ""
    return str(value).strip()

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
        aliases=("Ticket ID", "TicketID", "ticket_id", "ID")
    )
    if not ticket_col:
        raise RuntimeError(
            "Could not find the ticket ID column. Set [columns].ticket_id in Streamlit secrets "
            "to the exact header in your Tickets worksheet."
        )

    matches = [
        row for row in rows
        if clean(row.get(ticket_col)).casefold() == ticket_id.casefold()
    ]
    if not matches:
        return None

    # If duplicate IDs exist, return the first matching row and flag a configuration issue.
    return matches[0], headers, len(matches)

def safe_field(row, headers, configured_name, aliases=()):
    col = find_header(headers, configured_name, aliases)
    return clean(row.get(col)) if col else ""

def status_colour(status):
    s = status.lower()
    if "resolv" in s or "clos" in s or "complet" in s:
        return "#356B4A"
    if "critical" in s or "urgent" in s or "escalat" in s:
        return "#B42318"
    if "progress" in s or "acknow" in s or "review" in s:
        return "#95664F"
    return "#81756D"

st.markdown('<div class="cp-brand">CampusPulse</div>', unsafe_allow_html=True)
st.markdown('<div class="cp-tagline">Your Campus. Your Voice.</div>', unsafe_allow_html=True)
st.write("Report a campus issue or check the latest status of an existing complaint.")

try:
    form_url = st.secrets["google_sheets"]["google_form_url"]
except Exception:
    form_url = ""

track_tab, register_tab = st.tabs(["🔎 Track my complaint", "📝 Register new complaint"])

with track_tab:
    st.markdown('<div class="cp-card">', unsafe_allow_html=True)
    st.subheader("Track my complaint")
    st.caption("Enter the ticket ID you received after submitting your complaint.")
    with st.form("ticket_lookup", clear_on_submit=False):
        ticket_id = st.text_input(
            "Ticket ID",
            placeholder="e.g. TEST-CP-0001",
            help="Enter the complete ticket ID exactly as shown in your acknowledgement email."
        ).strip()
        submitted = st.form_submit_button("Search ticket", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not ticket_id:
            st.warning("Please enter a ticket ID.")
        else:
            try:
                with st.spinner("Looking up your ticket..."):
                    result = read_ticket(ticket_id)
                if result is None:
                    st.error("We couldn't find a complaint with that ticket ID. Check the ID and try again.")
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

                    st.markdown('<div class="cp-card">', unsafe_allow_html=True)
                    st.subheader("Complaint details")
                    actual_status = safe_field(row, headers, columns.get("status", "Status"), ("Current Status", "Ticket Status"))
                    if actual_status:
                        colour = status_colour(actual_status)
                        st.markdown(
                            f'<span style="display:inline-block;background:{colour};color:#fff;'
                            f'padding:0.35rem 0.75rem;border-radius:999px;font-weight:700;">'
                            f'{actual_status}</span>',
                            unsafe_allow_html=True
                        )
                        st.write("")
                    else:
                        st.info("A status field is not currently available in the configured worksheet.")

                    visible = []
                    for label, configured_name, aliases in display_fields:
                        value = safe_field(row, headers, configured_name, aliases)
                        if value:
                            visible.append((label, value))
                    summary = safe_field(
                        row, headers, columns.get("summary", "Summary"),
                        ("Complaint Summary", "Description", "Report Text", "Complaint")
                    )
                    update_note = safe_field(
                        row, headers, columns.get("resolution_note", "Resolution_Note"),
                        ("Resolution Note", "Latest Update", "Admin Note")
                    )

                    if summary:
                        st.markdown("**Complaint summary**")
                        st.write(summary)
                    left, right = st.columns(2)
                    for index, (label, value) in enumerate(visible):
                        with (left if index % 2 == 0 else right):
                            st.markdown(f'<div class="cp-label">{label}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="cp-value">{value}</div>', unsafe_allow_html=True)
                            st.write("")
                    if update_note:
                        st.markdown("**Latest update**")
                        st.write(update_note)
                    if match_count > 1:
                        st.warning("More than one row has this ticket ID. Please ask the administrator to check the sheet.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.caption("Only fields configured for student display are shown.")
            except Exception as exc:
                st.error("Ticket lookup could not be completed.")
                st.caption(str(exc))
                st.info("Check the worksheet name, column mappings, Google Sheet sharing, and Streamlit secrets.")

with register_tab:
    st.markdown('<div class="cp-card">', unsafe_allow_html=True)
    st.subheader("Register a new complaint")
    st.write("Use the official CampusPulse complaint form. After submission, keep the ticket ID from your acknowledgement email.")
    if form_url and urlparse(form_url).scheme == "https":
        st.link_button("Open complaint form ↗", form_url, type="primary", use_container_width=True)
    else:
        st.warning("The Google Form URL has not been configured yet.")
        st.caption("Add google_form_url under [google_sheets] in Streamlit secrets.")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.markdown(
    '<div class="cp-muted">CampusPulse · Student portal · For urgent or immediate safety risks, '
    'contact campus authorities directly.</div>',
    unsafe_allow_html=True
)
