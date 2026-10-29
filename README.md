<div align="center">

# 💸 Saudi Card Payments 🌴

### Weekly card (point-of-sale) payments in Saudi Arabia: sectors, cities and seasonal patterns

**May 2020 – July 2025** · 17 sectors · 11 cities · 7,830 weekly records

[🚀 **Live Dashboard**](https://YOUR-APP-NAME.streamlit.app) · [📓 Notebook](Final_Project_Unit3_Saudi_Card_Payments.ipynb)

</div>

---

## 🇸🇦 About the project

An interactive Streamlit dashboard that explores how people in Saudi Arabia pay by card, week by week. It shows which sectors and cities lead, how payments grew between 2021 and 2024, and how Ramadan, Eid and salary weeks change spending.

This is the final project of **Unit 3: Data Exploration & Dashboard Development**.

## 📊 The data

| | |
|---|---|
| **Dataset** | Point of Sale Transactions by Sector and City |
| **Source** | [KAPSARC Data Portal](https://data.kapsarc.org/explore/dataset/point-of-sale-transactions-by-sector-and-city/) (weekly series from the Saudi Central Bank, SAMA) |
| **Period** | May 2020 – July 2025 (weekly) |
| **Raw file** | 31,262 rows, 5 columns |
| **Clean file** | `clean_data.csv`, 7,830 rows × 13 columns |

**Measures per week**

- 💰 **Spending value** (SAR thousands)
- 🧾 **Number of transactions** (thousands)
- 🏷️ **Average payment** (SAR) = value ÷ transactions
- 📈 **Weekly change %** for value and transactions

**Levels.** Each row belongs to one of three levels: `national` (270 rows), `sector` (4,590 rows) or `city` (2,970 rows). The levels are never added together. The source has no sector-by-city breakdown, so a sector cannot be filtered by city.

**Added columns:** `year`, `month`, `week_of_year`, `is_ramadan`, `is_salary_week`.

## 🧭 Dashboard pages

| Page | What you see |
|---|---|
| 🏠 **Overview** | KPI cards, spending over time, spending by year, busiest months, key takeaways |
| 🛍️ **Sectors** | Ranking, month-pattern heatmap, growth 2021 vs 2024, average payment, selected sectors over time |
| 🏙️ **Cities** | Ranking, average payment, growth, share, single or multiple city comparison |
| 🌙 **Seasonal Insights** | Ramadan, pay weeks, Eid al-Fitr and monthly pattern (national, by sector, by city) |
| 📋 **Data & Methodology** | Data preview, CSV download, summary statistics, definitions and limitations |

**Sidebar controls:** year range slider, measure selector (value / transactions / average payment), smoothing, Ramadan shading.

## 🔍 Main findings

- 💳 Weekly spending grew from **9.1 bn SAR (2021)** to **12.8 bn SAR (2024)**, and weekly payments doubled from **99 m to 199 m**.
- 🏷️ The average payment fell from **91 to 64 SAR**: people pay by card for smaller purchases.
- 🌙 In Ramadan, total spending rises **+5.6%** while the number of payments falls **7.8%**.
- 💵 Salary weeks have about **13% higher** spending than other weeks.
- 🕌 The week before Eid al-Fitr is the peak: **+28%** nationally, **+191%** in clothing.
- 🏙️ Riyadh has **32%** of city spending and Jeddah **15%**.

## 🛠️ Tech stack

`Python` · `pandas` · `Plotly` · `Streamlit`

## ▶️ Run locally

```bash
git clone https://github.com/nnnoufff/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Repository structure

```
├── app.py                 # Streamlit dashboard
├── clean_data.csv         # Cleaned dataset
├── requirements.txt       # Python packages
├── .streamlit/
│   └── config.toml        # Theme (Saudi green)
└── README.md
```

## ⚠️ Limitations

- Card (point-of-sale) payments only: cash and online payments are not included.
- No sector-by-city breakdown in the source.
- 2020 and 2025 are partial years, so yearly comparisons use 2021–2024.
- "Other cities" and "Other sector" are grouped categories in the source.

## 👩‍💻 Author

**Nouf** · GitHub: [@nnnoufff](https://github.com/nnnoufff)

---

<div align="center">

Data: KAPSARC Data Portal (SAMA weekly series) · Built with Streamlit 💚

</div>
