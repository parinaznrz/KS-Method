
import os
from appscanner.preprocessor import Preprocessor
from random import sample
import csv

###########################################################################
#              read text files_ generate representative flows             #
###########################################################################
# Function to read and process files
def read_and_process_files(file_paths):
    raw_dataset = {}
    for file_path in file_paths:
        with open(file_path, "r") as file:
            lines = file.readlines()

        raw_dataset[file_path] = {
            "packet_sizes": [list(map(int, line.split(","))) for line in lines]
        }
    return raw_dataset


################################################################################
#                          Select Random Flows from Text Files                 #
################################################################################
def select_random_flows(raw_dataset, num_flows=10):
    selected_flows = {}
    for file_path, data in raw_dataset.items():
        # Extract the filename without the full path and extension
        filename = os.path.basename(file_path)  # Get filename with extension
        filename_without_extension = os.path.splitext(filename)[0]  # Remove extension

        # Filter flows to include only those with more than 5 elements
        flows_with_more_than_five = [flow for flow in data["packet_sizes"] if len(flow) > 5]

        if len(flows_with_more_than_five) >= num_flows:
            # If there are enough flows with more than 5 elements, select from these
            selected_indices = sample(range(len(flows_with_more_than_five)), num_flows)
            selected_flows[filename_without_extension] = [flows_with_more_than_five[i] for i in selected_indices]
        else:
            # If not enough flows with more than 5 elements, select from all available flows
            selected_indices = sample(range(len(data["packet_sizes"])), min(num_flows, len(data["packet_sizes"])))
            selected_flows[filename_without_extension] = [data["packet_sizes"][i] for i in selected_indices]

    return selected_flows


flows_directory = "text_file_address"
file_paths = [os.path.join(flows_directory, file) for file in os.listdir(flows_directory)]
raw_dataset = read_and_process_files(file_paths)
selected_flows = select_random_flows(raw_dataset)
print(selected_flows)
########################################################################
#                              Read data                               #
########################################################################
def files_labels(directory):
    files = []
    labels = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            files.append(os.path.abspath(os.path.join(dirpath, f)))
            labels.append(f.split('_')[0])
    return files, labels

########################################################################
#                             Handle input                             #
########################################################################
# Get file paths and labels
# Create Flows and labels
pth = input("Enter the path of the folder containing pcap files:")
save_name = input("Enter a name to save flows in a pickle file:") + ".p"
my_files, my_labels = files_labels(pth)
# Create Preprocessor object
preprocessor = Preprocessor(verbose=True)
# Create Flows and labels
X, y = preprocessor.process(files=my_files, labels=my_labels, selected_flows=selected_flows)
# Save flows and labels to file
preprocessor.save(save_name, X, y)

# Save flows and labels to CSV file
csv_save_name = input("Enter a name to save flows in a CSV file:") + ".csv"
with open(csv_save_name, mode='w', newline='') as file:
    writer = csv.writer(file)
    for features, label in zip(X, y):
        row = list(features) + [label]  # Combine features and label
        writer.writerow(row)
