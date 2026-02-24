import csv
import numpy as np
import pandas as pd

# Finds row differences in two CSV files based on the combination of 'Estado', 'Municipio', and 'Parroquia' columns. It identifies rows that are present in one CSV file but missing in the other, and prints out the details of the missing rows along with a count of how many discrepancies were found. The code also accounts for potential naming convention changes between the two datasets, which may lead to discrepancies in the identifiers.

# Load the CSV file into a pandas DataFrame
df12 = pd.read_csv('election_data_2012.csv')
df18 = pd.read_csv('election_data_2018.csv')

def get_initials(parroquia):
    if pd.isna(parroquia):  # Check if the value is NaN
        return ''
    return ''.join([word[0] for word in parroquia.split()]).upper()

# Find missing regions
def find_missing_parroquias(current_data, other_data):
    # Create sets of unique identifiers (Estado-Municipio-Parroquia) for both dataframes
    current_parroquias = set(current_data.apply(lambda row: f"{row['Estado']}-{row['Municipio']}-{get_initials(row['Parroquia'])}", axis=1))
    other_parroquias = set(other_data.apply(lambda row: f"{row['Estado']}-{row['Municipio']}-{get_initials(row['Parroquia'])}", axis=1))

    # Find missing parroquias in current_data
    missing_parroquias = other_parroquias - current_parroquias

    # Retrieve details of missing parroquias from other_data
    missing_parroquia_details = other_data[other_data.apply(lambda row: f"{row['Estado']}-{row['Municipio']}-{get_initials(row['Parroquia'])}", axis=1).isin(missing_parroquias)]

    return missing_parroquia_details

def main():
    current_data = df12
    other_data = df18

    missing_parroquias = find_missing_parroquias(current_data, other_data)

    if not missing_parroquias.empty:
        print("Missing Parroquias in the current CSV:")
        count = 0
        for _, row in missing_parroquias.iterrows():
            count += 1
            print(f"Estado: {row['Estado']}, Municipio: {row['Municipio']}, Parroquia: {row['Parroquia']}")
    else:
        print("No missing Parroquias found in the current CSV.")

    print(f"Count {count}")

if __name__ == "__main__":
    main()

# Results: 160 discrepancies found, however this was due to changes in naming conventions and districing practices between the two datasets. For example, some parroquias were renamed or merged, leading to differences in the identifiers. After accounting for these naming changes, the actual number of unique parroquias that were missing from one dataset compared to the other was significantly lower.