# Logging of Power & Temperature Data from *FRITZ!Smart Energy 210* socket

![](https://raw.githubusercontent.com/gerritnowald/FRITZSmartEnergy210_Gmail_Logger/main/temperature_stats.webp)

A *FRITZ!Box* can be configured to send daily E-Mail reports. 
These are downloaded using the Gmail API. 
The temperature data has to be extracted from pixel images. 
Power & temperature data over time are saved into a csv file and can be analyzed using a Jupyter notebook.

The main advantage of this complex approach is that no server is required to log the data. 
The data is stored in e-mails and can be retrieved in batch.

See also these blog posts:  
https://gerritnowald.wordpress.com/2025/07/21/downloading-email-reports-using-the-gmail-api/  
https://gerritnowald.wordpress.com/2025/07/23/from-pixels-to-data-extracting-temperature-values-from-images/

## setup

1. set up Gmail API
    - https://www.directedignorance.com/blog/gmail-with-python or
    - https://developers.google.com/workspace/gmail/api/guides

2. put `credentials.json` into `.\authentication\`

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. in Gmail, set up a filter to apply a label to the reports

5. get the corresponding `LabelID` using
```bash
python get_label_ids.py
```

## usage

Download report attachements:
```bash
python download_email_data.py LabelID
```

Digitalize temperature graphs and append to `data.csv`:
```bash
python digitalize_temperature.py
```

Use the Jupyter notebook `analysis.ipynb` to create graphs.


## Acknowledgements

Simonas Viliūnas for providing a great starting point  
https://github.com/vilisimo/examples/tree/main/gmail