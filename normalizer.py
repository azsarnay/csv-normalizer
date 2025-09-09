#!/usr/bin/env python3
"""
CSV Normalizer

A tool that reads CSV data from stdin and outputs normalized CSV data to stdout.
Handles UTF-8 encoding, timestamp conversion, ZIP code formatting, and other
data transformations as specified.
"""

import csv
import sys
import re
from datetime import datetime
import pytz
from typing import List, Optional, Tuple


def clean_utf8_text(text: str) -> str:
    """Clean UTF-8 text by replacing invalid characters with Unicode Replacement Character."""
    try:
        # Try to encode and decode to catch invalid UTF-8
        text.encode('utf-8').decode('utf-8')
        return text
    except UnicodeDecodeError:
        # Replace invalid characters with Unicode Replacement Character
        return text.encode('utf-8', errors='replace').decode('utf-8')


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string and convert from US/Pacific to US/Eastern timezone."""
    # Timestamp format found in the sample data
    format_str = '%m/%d/%y %I:%M:%S %p'  # e.g., 4/1/11 11:00:00 AM
    
    pacific_tz = pytz.timezone('US/Pacific')
    eastern_tz = pytz.timezone('US/Eastern')
    
    try:
        # Parse as naive datetime first
        naive_dt = datetime.strptime(timestamp_str, format_str)
        # Localize to Pacific timezone
        pacific_dt = pacific_tz.localize(naive_dt)
        # Convert to Eastern timezone
        eastern_dt = pacific_dt.astimezone(eastern_tz)
        return eastern_dt
    except ValueError:
        return None


def format_timestamp_rfc3339(dt: datetime) -> str:
    """Format datetime object as RFC3339 string."""
    return dt.isoformat()


def format_zip_code(zip_str: str) -> str:
    """Format ZIP code as 5 digits with leading zeros if needed."""
    # Remove any non-digit characters
    digits_only = re.sub(r'\D', '', zip_str)
    # Pad with leading zeros to make it 5 digits
    return digits_only.zfill(5)


def convert_duration_to_seconds(duration_str: str) -> float:
    """Convert HH:MM:SS.MS format to total seconds."""
    try:
        # Handle cases where hours might be more than 2 digits (e.g., 111:23:32.123)
        parts = duration_str.split(':')
        if len(parts) != 3:
            return 0.0
        
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    except (ValueError, IndexError):
        return 0.0


def normalize_row(row: List[str]) -> Optional[List[str]]:
    """Normalize a single CSV row according to the specifications."""
    if len(row) < 8:
        return None
    
    try:
        # Clean UTF-8 for all fields
        cleaned_row = [clean_utf8_text(field) for field in row]
        
        # Parse and convert timestamp (index 0)
        timestamp_str = cleaned_row[0]
        dt = parse_timestamp(timestamp_str)
        if dt is None:
            print(f"Warning: Could not parse timestamp '{timestamp_str}', dropping row", file=sys.stderr)
            return None
        cleaned_row[0] = format_timestamp_rfc3339(dt)
        
        # Address (index 1) - pass through as is, already cleaned for UTF-8
        # ZIP code (index 2) - format as 5 digits
        cleaned_row[2] = format_zip_code(cleaned_row[2])
        
        # FullName (index 3) - convert to uppercase
        cleaned_row[3] = cleaned_row[3].upper()
        
        # Convert durations to seconds (indices 4 and 5)
        foo_duration_seconds = convert_duration_to_seconds(cleaned_row[4])
        bar_duration_seconds = convert_duration_to_seconds(cleaned_row[5])
        
        cleaned_row[4] = str(foo_duration_seconds)
        cleaned_row[5] = str(bar_duration_seconds)
        
        # Calculate TotalDuration (index 6) as sum of FooDuration and BarDuration
        total_duration = foo_duration_seconds + bar_duration_seconds
        cleaned_row[6] = str(total_duration)
        
        # Notes (index 7) - pass through as is, already cleaned for UTF-8
        
        return cleaned_row
        
    except Exception as e:
        print(f"Warning: Error processing row: {e}, dropping row", file=sys.stderr)
        return None


def main():
    """Read CSV from stdin and output normalized CSV to stdout."""
    try:
        # Read raw input and clean UTF-8 before CSV parsing
        raw_input = sys.stdin.buffer.read()
        try:
            # Try to decode as UTF-8 first
            clean_input = raw_input.decode('utf-8')
        except UnicodeDecodeError:
            # If that fails, decode with error replacement
            clean_input = raw_input.decode('utf-8', errors='replace')
        
        # Create CSV reader from cleaned string
        import io
        reader = csv.reader(io.StringIO(clean_input))
        writer = csv.writer(sys.stdout)
        
        # Process header row
        header = next(reader)
        if len(header) == 8:
            writer.writerow(header)
        else:
            print(f"Warning: Expected 8 columns, found {len(header)}, skipping header", file=sys.stderr)
            return
        
        # Process data rows
        for row in reader:
            normalized_row = normalize_row(row)
            if normalized_row is not None:
                writer.writerow(normalized_row)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
