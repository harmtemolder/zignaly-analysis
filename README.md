# Zignaly Analysis

## Install dependencies:
```
pip install bs4 matplotlib numpy pandas
```

## How to run this:
I get this error when downloading CSVs:

```
{"error":{"code":18,"msg":"No positions found"}}
```

So instead:
1. Save the entire page as HTML in your browser
2. Feel free to delete the matching "*_files" folder to save drive space
3. Point `input_file` in `zignaly_analysis.py` to the HTML file
