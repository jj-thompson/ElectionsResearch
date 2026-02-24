import requests
from bs4 import BeautifulSoup
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# This is a basic web scraper, which retrieves election data from the specified URL, extracts relevant information about candidates and technical data, and saves it to a CSV file. The code is designed to handle potential errors gracefully, such as HTTP errors or issues with parsing the HTML content. It uses concurrent requests to speed up the scraping process by utilizing multiple threads. The candidate names and technical data labels are defined directly in the code for easier maintenance and readability.
# For loops creating number code based on the original URL structure, which is http://www.cne.gob.ve/resultado_presidencial_2012/r/1/reg_01010101.html, where the numbers represent different regions and subregions. The code constructs URLs based on this pattern to scrape data from multiple pages efficiently.
# As of 2024, these websites are no longer in use, for reasons unknown

# Url changed for 2012 election data, but the structure of the website is the same as 2018, so the code should work with minor adjustments to the candidate names and technical data labels.
url = f"http://www.cne.gob.ve/resultado_presidencial_2012/r/"
#url = f"http://www.cne.gob.ve/resultado_presidencial_2018/r/"
path = "/Users/james/Desktop/ElectionsResearch"



def scrape_election_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.
        soup = BeautifulSoup(response.content, 'html.parser')
        data = {}

        # Remove prefixes from location names
        toRemove = ['DDTO. ', 'DDTO.', 'CE. ', 'CE.', 'PQ. ', 'PQ.', 'CM. ', 'CM.', 'MP. ', 'MP.', 'EDO. ', 'EDO.']
        location_bar = soup.find('div', {'id': 'locationBar'})
        if location_bar:
            links = location_bar.find_all('a', {'id': 'region_ref'})
            if len(links) >= 3:
                estado = links[1].text.strip().split(":")[-1].strip().upper()
                municipio = links[2].text.strip().split(":")[-1].strip().upper()
                parroquia = links[3].text.strip().split(":")[-1].strip().upper()
                
                for word in toRemove:
                    estado = estado.replace(word, '')
                    municipio = municipio.replace(word, '')
                    parroquia = parroquia.replace(word, '').replace('#', 'n')

                data['Estado'] = estado.lower().title()
                data['Municipio'] = municipio.lower().title()
                data['Parroquia'] = parroquia.replace('#', 'n').lower().title()

            else:
                data['Estado'] = 'N/A'
                data['Municipio'] = 'N/A'
                data['Parroquia'] = 'N/A'
        else:
            data['Estado'] = 'N/A'
            data['Municipio'] = 'N/A'
            data['Parroquia'] = 'N/A'

        # Define the candidate names directly
        candidate_names = {
            'HUGO CHAVEZ': 'Hugo Chavez',
            'HENRIQUE CAPRILES RADONSKI': 'Henrique Capriles Radonski',
            'REINA SEQUERA': 'Reina Sequera',
            'MARIA BOLIVAR': 'Maria Bolivar',
            'LUIS REYES': 'Luis Reyes',
            'ORLANDO CHIRINO': 'Orlando Chirino'
        }

        # Initialize candidate votes to 'N/A'
        for candidate in candidate_names.values():
            data[candidate] = 'N/A'

        # Extract candidate votes
        candidates = soup.find_all('tr', {'class': 'tbsubtotalrow'})
        for candidate in candidates:
            columns = candidate.find_all('td')
            if len(columns) >= 3:
                name = columns[2].text.strip().replace('\n', '').replace('Adjudicado', '')
                votes = columns[3].text.strip().replace('.', '')  # Remove dots from numbers
                if votes == 'Adjudicado':
                    votes = columns[4].text.strip().replace('.', '')

                if name in candidate_names:
                    data[candidate_names[name]] = votes

        # Extract technical data

        data['Valid votes'] = "N/A"
        data['Null votes'] = "N/A"            
        
        technical_table = soup.find('div', {'id': 'fichaTecnica'})
        if technical_table:
            rows = technical_table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 3:
                    label = columns[0].text.strip()
                    value = columns[2].text.strip().replace('.', '')  # Remove dots from numbers
                    if 'VOTOS VÁLIDOS' in label.upper():
                        data['Valid votes'] = value
                    elif 'VOTOS NULOS' in label.upper():
                        data['Null votes'] = value

        return data
    except requests.exceptions.HTTPError as e:
        print(f"404 Error for URL: {url}")
        return None
    except (requests.RequestException, AttributeError) as e:
        print(f"Error retrieving or parsing {url}: {e}")
        return None

def save_to_csv(data, path, csv_filename):
    fieldnames = ['Estado', 'Municipio', 'Parroquia', 'Hugo Chavez', 'Henrique Capriles Radonski', 'Reina Sequera', 'Maria Bolivar', 'Luis Reyes', 'Orlando Chirino', 'Valid votes', 'Null votes']
    full_path = os.path.join(path, csv_filename)
    with open(full_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if row:  # Check if the row is not None
                writer.writerow(row)

def construct_urls():
    urls = []
    for h in range(1, 5):
        for i in range(1, 26):
            for j in range(1, 30):
                for k in range(1, 30):
                    h_str = f"{h}"
                    i_str = f"{i:02}"
                    j_str = f"{j:02}"
                    k_str = f"{k:02}"
                    url = f"http://www.cne.gob.ve/resultado_presidencial_2012/r/{h_str}/reg_{i_str}{j_str}{k_str}.html"
                    urls.append(url)
    return urls

def main():
    all_data = []
    urls = construct_urls()
    startTime = time.time()
    # Using ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_election_data, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                election_data = future.result()
                if election_data:
                    all_data.append(election_data)
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

    # Specify the path where you want to save the CSV file on macOS
    csv_filename = 'election_data.csv'
    save_to_csv(all_data, path, csv_filename)
    # Print time to complete and done

    print(f"Time taken to scrape and save data: {time.time() - startTime} seconds")
    print("Done")
    #print(all_data)


if __name__ == "__main__":
    main()

