# UK House Prices Since 1953: Nominal vs Real

Python (pandas, matplotlib) analysis of 72 years of UK house prices, adjusted for inflation using CPI.

## Questions
1. How far have prices risen since 1953 in nominal terms and after inflation?
2. Which decades saw the strongest and weakest real growth?
3. Which property type grew fastest?
4. When were the sharpest real-terms falls?

## Data
- Nationwide house price series: [datasets/house-prices-uk](https://github.com/datasets/house-prices-uk)
- UK CPI annual price index: [datasets/cpi-uk](https://github.com/datasets/cpi-uk)
- Both are public and openly licensed. The script downloads them when it runs.

## Method
1. Averaged the quarterly prices into one value per year.
2. Joined them to annual CPI and converted every price into 2025 money.
3. Calculated compound annual growth (CAGR) overall, by decade and by property type.
4. Found the largest year-on-year falls in real prices.

## Key findings
- The average price rose from about £1,900 in 1953 to about £272,000 in 2025, which is 144x in nominal terms but only 3.7x after inflation (about 1.8% a year in real terms).
- Real growth was strongest in the 2000s (about 5.0% a year) and 1980s (about 4.9%). It was flat or negative in the 1990s (-0.7%) and 2010s (0.1%).
- On a like-for-like period (1953 to 2015), new homes grew fastest in nominal terms at about 7.6% a year, ahead of older (7.4%) and modern (6.8%) homes.
- Real prices peaked in 2007 at about £354,000 (in 2025 money). They are about 23% below that peak today.
- The sharpest real-terms annual falls were in 1990 (-14%), 1975 (-13%), 2023 (-11%), 1991 (-11%) and 2008 (-10%).

## How to run
```
pip install pandas matplotlib
python uk_house_prices_analysis.py
```
- This is a national average, so it hides big regional differences.
- Nominal growth is not adjusted for changes in the type or quality of homes sold.
