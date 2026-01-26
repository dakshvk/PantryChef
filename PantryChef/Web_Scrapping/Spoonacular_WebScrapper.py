import requests
from bs4 import BeautifulSoup
import csv
import os

# This will save it in the EXACT same folder as your script
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'spoonacular_endpoints_list.csv')

with open(file_path, 'w', newline='', encoding='utf-8') as f:

    def scrape_spoonacular_docs():
        url = "https://spoonacular.com"
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            api_data = []

            # Spoonacular uses <h3> or <h2> for specific endpoint titles
            # We look for all endpoint headings
            endpoints = soup.find_all(['h2', 'h3'])

            for endpoint in endpoints:
                endpoint_name = endpoint.text.strip()

                # Look for the parameter table immediately following this header
                # We look at the "next siblings" until we find a table or another header
                next_node = endpoint.find_next_sibling()

                while next_node and next_node.name not in ['h2', 'h3']:
                    if next_node.name == 'table':
                        rows = next_node.find_all('tr')[1:]  # Skip header row
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 4:
                                api_data.append({
                                    'Endpoint': endpoint_name,
                                    'Parameter Name': cols[0].text.strip(),
                                    'Type': cols[1].text.strip(),
                                    'Example': cols[2].text.strip(),
                                    'Description': cols[3].text.strip()
                                })
                        break  # Stop after finding the first table for this endpoint
                    next_node = next_node.find_next_sibling()

            # Save to CSV
            with open('spoonacular_parameters.csv', 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Endpoint', 'Parameter Name', 'Type', 'Example', 'Description']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(api_data)

            print(f"SUCCESS! Organized {len(api_data)} parameters by endpoint.")

        except Exception as e:
            print(f"Error: {e}")

        if __name__ == "__main__":
            scrape_spoonacular_docs()
