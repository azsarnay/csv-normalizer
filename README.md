# CSV Normalizer

Python script that normalizes CSV data according to specific formatting requirements. The script reads CSV data from standard input and outputs normalized CSV data to standard output.

## Usage

```bash
source venv/bin/activate
python3 normalizer.py < input.csv > output.csv
```

## Requirements

- Python 3.6+
- Virtual environment

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## What It Does

The normalizer performs the following transformations on CSV data:

### Timestamp Conversion
- Converts timestamps from US/Pacific to US/Eastern timezone
- Formats timestamps in RFC3339 format
- Handles various date formats found in the input data

### ZIP Code Formatting
- Ensures all ZIP codes are exactly 5 digits
- Pads shorter codes with leading zeros
- Removes any non-digit characters

### Name Normalization
- Converts FullName column to uppercase
- Handles international characters properly

### Duration Conversion
- Converts HH:MM:SS.MS format durations to total seconds
- Handles cases with hours > 99 (e.g., 111:23:32.123)
- Calculates TotalDuration as sum of FooDuration and BarDuration

### UTF-8 Handling
- Ensures all text is properly UTF-8 encoded
- Replaces invalid UTF-8 characters with Unicode Replacement Character ()
- Drops rows if invalid characters make data unparseable

### Address and Notes
- Address field is passed through unchanged (except UTF-8 cleaning)
- Notes field is passed through unchanged (except UTF-8 cleaning)
- Properly handles quoted fields containing commas

## Error Handling

- Invalid timestamps cause the row to be dropped with a warning to stderr
- Invalid UTF-8 characters are replaced with the Unicode Replacement Character
- Rows that cannot be processed are dropped with warnings
- All warnings are written to stderr, so they don't interfere with the CSV output

## Implementation Notes

The script uses Python's built-in `csv` module for CSV parsing that handles quoted fields correctly. Timezone conversions use the `pytz` library for accurate timezone handling.

## Future Improvements

### Data Validation
- Add column header validation to ensure expected columns are present and in correct order
- Implement data type validation for each column (e.g., verify ZIP contains only digits)
- Add range validation for timestamps and durations
- Validate that required fields are not empty

### Containerization
- Create Dockerfile for easy deployment and consistent environment
- Add docker-compose.yml for local development
- Publish container image for distribution

### Robustness Enhancements
- Add support for multiple timestamp formats (ISO, Unix timestamps, etc.)
- Implement configurable timezone conversion (not hardcoded to US/Pacific → US/Eastern)
- Add CSV dialect detection for different separators and quote styles
- Support for streaming large files with memory-efficient processing
- Add progress indicators for large file processing
- Implement retry logic for transient errors
- Add comprehensive logging with configurable levels
- Support for different output formats (JSON, XML, etc.)
- Add unit tests and integration tests
- Implement data quality metrics and reporting
- Add command-line argument parsing for configuration options
- Support for batch processing multiple files
- Add data profiling and statistics output

