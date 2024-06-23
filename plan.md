### Desired result

Having a page with a table that contains rows by dates with columns that show difference between weather forecast and actual weather that day and hour.

| Date and time    | Actual | Diff -3h | Diff -12h | Diff -1d |
|------------------|--------|----------|-----------|----------|
| 2024-06-01 00:00 | +20    | 0        | -1        | +3       |
| 2024-06-01 03:00 | +19    | +1       | +2        | 0        |
|                  |        |          |           |          |

### Steps

- Let's start with only SMHI.se web-site.
- Download the data from the web-site page of weather for given city.
- Extract the needed data from the downloaded page.
- Transform the data into some type how you will store it. For example:
  - Sunny -> 5
  - Almost sunny -> 4
  - Cloudy -> 3
  - Small rain -> 2
- Store the data into a simple format.
- Setup regular data updates (download, transform, save).
- Set the database.
- Save results into the database.
- Get the historical information from the data stored for a period of time and create the data of difference between the target date and the time before.
- Prepare the table as above.
- Set a web server for showing the page with the table.

### Track of the progress

Call download_smhi.py in the terminal.
Next step is to write the code downloading the page directly to the folder in VS.
First thing first, we need to know what to download 
It can easily happen that the data we want is not from the official website (the main source); instead it can get from other sources like the data can be driven and dowloaded dynamically into Java script and send to the official webpage.
- we need to understand what is being downloaded --> we go to the official page -> F12 > Click Network (to know where we request the data) and clean the data using the not allowed sign --> refresh the page
- Then we will see the document file on top which is the same suffix of the html address, for example
- That file can be automatically downloaded some files which we want to focus on and not the whole thing.
- Find the file we want to open and right click > copy > copy URL. Then open the new tab and paste the address link 

#### Data extraction

- By having the JSON from the SMHI, need to prepare a row which will be placed in SQL.
- Probably, for the forecast table the columns will be:
  - Datetime
  - Actual temperature
  - Predicted temperature from    week before
  - Predicted temperature from 3  days before
  - Predicted temperature from 1  day before
  - Predicted temperature from 12 hours before
  - Predicted temperature from 6  hours before
  - Predicted temperature from 3  hours before

- Create prepare_rows.py which you would call like this:
      
      python3 prepare_rows.py raw_data/historical_20240615230233.json
  
  And it prints the rows of historical datetime (localDate) and temperature (t), like this:

      2024-06-16T10:00    17.3
      2024-06-16T11:00    19.0

- In prepare_rows.py, when you call it with `forecast` json like this:
      
      python3 prepare_rows.py raw_data/forecast_20240615230233.json
  
  It should print rows of:
  - forecast datetime (localDate)
  - difference from the time when the forecast was generated (referenceTime), in hours
  - temperature (t)
  
  Like this:

      2024-06-16T10:00    1h    17.3
      2024-06-16T11:00    2h    19.0
      2024-06-16T12:00    3h    21.0

- Then the next step is to generate the data from all historical without duplicates. For that, we need to find the files which starts with 'historical' name. So, store all the historical files as a list.

- Using that data, we need to prepare a dataset as tuples:

Like this:

      2024-06-16T18:00    20.4
      2024-06-16T17:00    20.9

- Collect all these tuples into a list of historical files