
import pandas as pd
import numpy as np
import os

# Columns to sum up
columns_to_sum = ["NLoadEos", "PLoadEos", "SLoadEos", "NLoadEor", "PLoadEor", "SLoadEor", "NLoadEot", "PLoadEot", "SLoadEot"]

# Read the pareto_front.txt file
pareto_front = pd.read_csv('pareto_front.txt', header=None, delim_whitespace=True)

# Prepare a list to collect rows for the final output
output_data = []

# Iterate over the CSV files
for i in range(len(pareto_front)):
    file_name = f"{i}_reportloads.csv"
    
    # Check if file exists
    if os.path.exists(file_name):
        # Read the CSV file
        df = pd.read_csv(file_name, usecols=columns_to_sum)
        
        # Calculate the sum of the specified columns
        sums = df[columns_to_sum].sum()

        # Combine with the corresponding value from pareto_front
        row = [pareto_front.iloc[i, 0]] + sums.tolist()
        output_data.append(row)

# Define the header
header = ['Cost'] + columns_to_sum

# Create a DataFrame from the output data
output_df = pd.DataFrame(output_data, columns=header)

# Save the DataFrame to a new CSV file
output_df.to_csv('output.csv', index=False)
