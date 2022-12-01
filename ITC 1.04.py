import yfinance as yf
import numpy as np
from datetime import date, timedelta
import scipy.stats as st
from yahoo_fin.stock_info import *
import math


def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:
        adate -= timedelta(days=1)
    return adate


index = '^NSEI'
stock = 'ITC.NS'
ticker = [index, stock]
stk = yf.Ticker(stock)
OutstandingShares = stk.info['sharesOutstanding']
BusinessSummary = stk.info['longBusinessSummary']

# Important Variables
RequiredRate = 0.0425  # Risk Free Rate
TerminalRate = 0.03  # Terminal Growth Rate
EquityRiskPremium = 0.07  # Equity Risk Premium taken from (https://incwert.com/india-equity-risk-premium-2020/)
Optimism = 0.15  # Your expectation for the years 6-10
Numerals = 10_00_000  # Lakhs or Crore?
DebtWeight = 0.00
DebtInterest = 0.00
Tax = 0.25
PropertyPlantAndEquipmentCurrentYear = 19153.94  # Balance Sheet
PropertyPlantAndEquipmentPreviousYear = 19632.92  # Balance Sheet
DepreciationAndAmortisation = 1641  # Income Statement
CashFlowFromOperations1 = 12527  # Cash Flow Statement
CashFlowFromOperations2 = 14690  # Cash Flow Statement
CashFlowFromOperations3 = 12583  # Cash Flow Statement
CashFlowFromOperations = (CashFlowFromOperations1 + CashFlowFromOperations2 + CashFlowFromOperations3) / 3

start = '2016-08-01'
today = prev_weekday(date.today())
p = get_live_price(stock)

df = pd.DataFrame(yf.download(ticker, start, today))
df = df['Adj Close'].pct_change(1) + 1
df = df.dropna()
df_stock = df[stock] - 1

sd_index = np.std(df[index])
sd_stock = np.std(df[stock])
Correlation = df[stock].corr(df[index])
Beta = float(Correlation) * float(sd_index) / float(sd_stock)
PriceGrowth = float(st.gmean(df[stock]) - 1) * 365 * 100

CostofEquity = RequiredRate + (Beta * EquityRiskPremium) * (1 - DebtWeight)
CostofDebt = DebtWeight * DebtInterest * (1 - Tax)

WACC_1to5 = CostofEquity + CostofDebt
WACC_6to10 = WACC_1to5 * (1 + Optimism)

CAPEX = PropertyPlantAndEquipmentCurrentYear - PropertyPlantAndEquipmentPreviousYear + DepreciationAndAmortisation
FreeCashFlow = CashFlowFromOperations - CAPEX

# Free Cash Flow
FCF_1 = FreeCashFlow * (1 + WACC_1to5)
FCF_2 = FCF_1 * (1 + WACC_1to5)
FCF_3 = FCF_2 * (1 + WACC_1to5)
FCF_4 = FCF_3 * (1 + WACC_1to5)
FCF_5 = FCF_4 * (1 + WACC_1to5)
FCF_6 = FCF_5 * (1 + WACC_6to10)
FCF_7 = FCF_6 * (1 + WACC_6to10)
FCF_8 = FCF_7 * (1 + WACC_6to10)
FCF_9 = FCF_8 * (1 + WACC_6to10)
FCF_10 = FCF_9 * (1 + WACC_6to10)
PV_1 = FCF_1 / ((1 + float(RequiredRate)) ** 1)
PV_2 = FCF_2 / ((1 + float(RequiredRate)) ** 2)
PV_3 = FCF_3 / ((1 + float(RequiredRate)) ** 3)
PV_4 = FCF_4 / ((1 + float(RequiredRate)) ** 4)
PV_5 = FCF_5 / ((1 + float(RequiredRate)) ** 5)
PV_6 = FCF_6 / ((1 + float(RequiredRate)) ** 6)
PV_7 = FCF_7 / ((1 + float(RequiredRate)) ** 7)
PV_8 = FCF_8 / ((1 + float(RequiredRate)) ** 8)
PV_9 = FCF_9 / ((1 + float(RequiredRate)) ** 9)
PV_10 = FCF_10 / ((1 + float(RequiredRate)) ** 10)
PVTotal = PV_1 + PV_2 + PV_3 + PV_4 + PV_5 + PV_6 + PV_7 + PV_8 + PV_9 + PV_10

TerminalYear = FCF_10 * (1 + TerminalRate)
PVCashFlows = PVTotal
TerminalValue = (TerminalYear / (RequiredRate - TerminalRate)) / ((1 + RequiredRate) ** 10)
TotalPVCashFlows = PVCashFlows + TerminalValue

DCFPrice = float(TotalPVCashFlows * Numerals / OutstandingShares)

var = df_stock.quantile(0.05)
var_1 = float(var * math.sqrt(10)) * 100
stock_price = float(abs(var_1) * p / 100)

# Output
print('Ticker: ' + stock + '\nAnalysis Date: ' + str(today))
print('Price Annual Growth Rate (5YRS): ' + str(round(PriceGrowth, 2)) + '%')
print('10 Day VaR: ' + str(round(var_1, 2)) + '%, ₹' + str(round(stock_price, 2)))
print('Discounted Cash Flow Model: ₹' + str(round(DCFPrice, 2)) + '\nCurrent Price: ₹' + str(round(p, 2)))
print('\nPPE This Year: ₹{0} \nPPE Last Year: ₹{1}'.format(PropertyPlantAndEquipmentCurrentYear, PropertyPlantAndEquipmentPreviousYear))
print('Depreciation & Amortisation: ₹{0} \nCashFlowFromOperations: ₹{1}'.format(DepreciationAndAmortisation, CashFlowFromOperations))