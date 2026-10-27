# CampusPulse Student Portal (Streamlit)

This small app provides:
- Ticket lookup by ticket ID from a private Google Sheet.
- A link to the existing Google Form for new complaints.
- A minimal responsive student-facing interface using Espresso & Persimmon colours.

## 1. Important before launch
The app is read-only for Google Sheets. It does not modify your n8n workflows or write to the spreadsheet.
It only displays a small set of fields from a matching ticket. Review the fields before exposing the app publicly.
A ticket ID is not proof of ownership. Do not expose student email addresses, private notes, or sensitive complaint text.

## 2. Run locally
Use Python 3.11 or 3.12.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` by copying `secrets.example.toml` into that location, then fill in the real values. Do not commit secrets to Git.

Run:
```bash
streamlit run app.py
```

## 3. Google Sheets setup
1. In Google Cloud Console, create/select a project.
2. Enable the Google Sheets API.
3. Create a service account and generate a JSON key.
4. Share the existing `CampusPulse_Database` spreadsheet with the service account's `client_email` as a Viewer.
5. Put the spreadsheet ID (the value between `/d/` and `/edit` in its URL) into `spreadsheet_id`.
6. Set `worksheet_name` to the exact ticket worksheet name, usually `Tickets`.
7. Map every field under `[columns]` to the exact headers in the worksheet.
8. Paste the service-account fields into `[gcp_service_account]` in `secrets.toml`.

Use read-only access only for the student app. Do not make the spreadsheet public.

## 4. Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and this README to a private or public GitHub repository.
2. Do not push `.streamlit/secrets.toml`, the downloaded service-account JSON key, or any credentials.
3. Create the Streamlit app and set its Secrets using the contents of your local secrets file.
4. Test a real ticket ID and a non-existent ticket ID.
5. Confirm the app does not display emails or other private fields.

## 5. Exact headers matter
The default mappings are examples. Change them to match the actual header row of the `Tickets` worksheet. The code attempts common aliases, but the exact mapping is the safest choice.

## Troubleshooting
- `SpreadsheetNotFound`: the spreadsheet ID is wrong, or the spreadsheet was not shared with the service account.
- Worksheet not found: set the exact worksheet tab name.
- Ticket ID column not found: update `columns.ticket_id`.
- Ticket not found: confirm the ID exists in the configured worksheet and has no unexpected whitespace.
- Secrets error: ensure all required service-account fields are present and valid.
