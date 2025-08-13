#!/usr/bin/env python3

import re
import csv
from bs4 import BeautifulSoup

def extract_link_info(html_file, csv_file):
    """
    Extract information from HTML links and save to CSV file.
    
    Args:
        html_file: Path to input HTML file
        csv_file: Path to output CSV file
    """
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links with href containing "/secrets/"
    links = soup.find_all('a', href=re.compile(r'/secrets/\d+/'))
    
    # List to store extracted data
    extracted_data = []
    
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Extract number from href (e.g: "/secrets/14021/general" -> 14021)
        number_match = re.search(r'/secrets/(\d+)/', href)
        number = number_match.group(1) if number_match else ''
        
        # Extract IP from text (format: x.x.x.x)
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text)
        ip = ip_match.group(1) if ip_match else ''
        
        # Extract server name (after "- " and before "\" or end)
        name_match = re.search(r' - ([^\\]+)', text)
        name = name_match.group(1).strip() if name_match else ''
        
        if number and ip and name:
            extracted_data.append([number, ip, name])
    
    # Write to CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Numero', 'IP', 'Nombre'])
        writer.writerows(extracted_data)
    
    print(f"Extracted {len(extracted_data)} elements and saved to {csv_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python extract_links.py <html_file> <csv_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    csv_file = sys.argv[2]
    
    extract_link_info(html_file, csv_file)