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

get label ID:
```bash
python get_label_ids.py
```

Download files:
```bash
python download_email_data.py LabelID
```

see
```bash
python download_email_data.py -h
```
fur further options.

Use `analyse_power.ipynb` and `analyse_temperature.ipynb` for analysis.


## Acknowledgements

Simonas Viliūnas for providing a great starting point  
https://github.com/vilisimo/examples/tree/main/gmail