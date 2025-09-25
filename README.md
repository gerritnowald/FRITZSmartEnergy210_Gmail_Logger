Download *FRITZ!Smart Energy 210* reports using the Gmail API  
Digitalize temperature plots  
Analyze power & temperature


## setup

1. set up Gmail API
    - https://www.directedignorance.com/blog/gmail-with-python or
    - https://developers.google.com/workspace/gmail/api/guides

2. put `credentials.json` into `.\authentication\`

3. Install dependencies
```bash
pip install -r requirements.txt
```

## usage

In Gmail, a filter has to be setup to apply a label to the reports.

get `LabelID`:
```bash
python get_label_ids.py
```

Download report attachements:
```bash
python download_email_data.py LabelID
```

Digitalize temperature graphs and append to `data.csv`:
```bash
python digitalize_temperature.py
```

Use `analysis.ipynb` to create graphs.


## Acknowledgements

Simonas Viliūnas for providing a great starting point  
https://github.com/vilisimo/examples/tree/main/gmail