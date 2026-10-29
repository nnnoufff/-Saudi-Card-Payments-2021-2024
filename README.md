# Saudi Card Payments Dashboard

Streamlit dashboard for weekly point-of-sale (card) payments in Saudi Arabia, May 2020 - July 2025
(KAPSARC Data Portal, SAMA weekly series).

## Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` - the dashboard
- `clean_data.csv` - cleaned dataset (7,830 rows)
- `requirements.txt`, `.streamlit/config.toml`

## Tabs
- **Overview / Sectors / Cities** - one tab per dataset, with its own selection and "Show as" control (over time, year by year, busiest months)
- **Key findings** - Ramadan, pay cycle, Makkah, Eid al-Fitr
- **Data and notes** - preview, summary statistics, CSV download, limitations
