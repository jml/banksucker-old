
## TODO

* Transform Lloyds to spending plan format
* Transform AMEX to spending plan format
* Create new spending plan
* Append new spending plan data to existing format
* Automatic download of Lloyds statements
* Automatic download of AMEX statements
* Filtering of duplicates
* Automatic category assignment


## Lloyds transform

1. Delete top row (headers)
2. Delete C & D (account, sort)
3. Delete F & G (running balance, ???)
4. Extract credits for review
   * Interest
   * Transfers for purchasing big-spend savings
   * Transfers for unexpected expenses
5. Delete E (credits)
6. Paste into Spending Plan


## Amex transform

1. Delete E, F
2. Replace all entries in B with "AMEX"
3. Extract credits
4. Swap C & D
5. Paste into Spending Plan


## Spending plan update

1. Reformat Date column (A) as date
2. Reformat Value column (D) as pounds
3. Sort by Value
4. Sort by Date
5. Delete any entries from before the period that are not in previous period
6. Delete any duplicate entries
7. Copy "Combined" and "Valid Category" helpers down to all new rows
8. Delete any entries that are purchases from big spends or special expenses
9. Fill in the field


## Close off spending plan



## New spending plan

1. Copy existing spending plan to YYYY-MM Spending Plan
2. Clear data from expenses (Col A:G, Row 2:END)
3. Enter "Money to spend"
   * jml's salary + Joliette's salary + interest
