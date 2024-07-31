import csv
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind, f_oneway
import statistics

species_data = []
adjusted_values = []
group_data = None
species_d13c_value = {}


def read_csv(file_path):
    data = []
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            row = {key.strip(): value for key, value in row.items()}
            data.append(row)
    return data


def glucose_average(data):
    glucose_values = []
    for i, row in enumerate(data):
        if i < 3:
            glucose_values.append(float(row["Delta CRDS"]))
    average = sum(glucose_values) / len(glucose_values)
    return average


def adjusted_delta(data, average):
    adjustment = average + 11.768
    adjusted_values = []
    print("\nCarbon Isotope Composition Report\n")
    for i, row in enumerate(data):
        if i >= 3:
            delta_raw = float(row["Delta CRDS"])
            adjusted_value = delta_raw - adjustment
            sample_id = row["Sample Id"].strip()
            print(
                f"Sample ID: {sample_id}, Adjusted Delta value = {adjusted_value:.3f}"
            )
            adjusted_values.append((sample_id, adjusted_value))
    return adjusted_values


def load_isotopic_data():
    global adjusted_values
    file_path = filedialog.askopenfilename(
        title="Select Isotopic Data CSV File",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
    )
    if not file_path:
        return

    try:
        isotopic_data = read_csv(file_path)
        average_glucose = glucose_average(isotopic_data)
        adjusted_values[:] = adjusted_delta(isotopic_data, average_glucose)

        messagebox.showinfo(
            "Info", "Processed isotopic data and calculated adjusted delta values."
        )
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_path}' not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    prompt_for_species()


def load_species_data():
    global species_data
    file_path = "leaf13C_database.csv"
    try:
        species_data = read_csv(file_path)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_path}' not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def search_species():
    global species_d13c_value

    while True:
        species_name = entry.get().strip().lower()
        if not species_name:
            messagebox.showinfo("Info", "Please enter a species name.")
            return

        if not species_data:
            messagebox.showwarning("Warning", "Species data not loaded yet.")
            return
        if species_name is not None:
            if any(species_name.lower() == k.lower() for k in species_d13c_value):
                messagebox.showinfo("Result", f"'{species_name}' already searched.")

                if not messagebox.askyesno(
                    "Search Another", "Do you want to search for another species?"
                ):
                    ask_for_statistical_analysis()
                    return
                else:
                    entry.delete(0, tk.END)
                    continue

        found = False
        for row in species_data:
            if row["species"].strip().lower() == species_name:
                little_d13_org = row["little.d13.org"]
                species_name = row["species"]
                if little_d13_org == "NA":
                    messagebox.showinfo(
                        "Result",
                        f"'{species_name}' leaf delta 13C value was not found.",
                    )
                    species_d13c_value[species_name] = None
                else:
                    messagebox.showinfo(
                        "Result",
                        f"'{species_name}' leaf delta 13C value is: {little_d13_org}",
                    )
                    species_d13c_value[species_name] = float(little_d13_org)
                    print(
                        f"'{species_name}' literature leaf delta 13C value is: {little_d13_org}"
                    )
                found = True
                break

        if not found:
            messagebox.showinfo(
                "Result", f"'{species_name}' not found in the database."
            )
            species_d13c_value[species_name] = None

        if not messagebox.askyesno(
            "Search Another", "Do you want to search for another species?"
        ):
            ask_for_statistical_analysis()
            return

        entry.delete(0, tk.END)


def ask_for_statistical_analysis():
    if not adjusted_values:
        messagebox.showwarning(
            "Warning", "No isotopic data available for statistical analysis."
        )
        return

    perform_stat_analysis = messagebox.askyesno(
        "Statistical Analysis", "Do you want to perform statistical analysis?"
    )
    if perform_stat_analysis:
        group_data, report = statistical_analysis(adjusted_values)
        if report:
            offer_to_plot_data(group_data, species_d13c_value)


def offer_to_plot_data(group_data, species_d13c_value):
    if messagebox.askyesno("Plot Data", "Do you want to plot the data?"):
        if species_d13c_value and any(species_d13c_value.values()):
            include_species_d13c = messagebox.askyesno(
                "Include Delta 13C",
                "Do you want to include the leaf delta 13C value from the database in the plotting?",
            )
        else:
            include_species_d13c = False
        plot_adjusted_data(
            adjusted_values,
            species_d13c_value if include_species_d13c else None,
            group_data,
        )


def statistical_analysis(data):
    global group_data
    if not data:
        messagebox.showerror("Error", "No data available for statistical analysis.")
        return None, None

    num_groups = simpledialog.askinteger(
        "Number of Groups", "How many groups does your data have?"
    )
    if num_groups is None:
        return None, None

    group_data = {}
    if num_groups in (0, 1):
        group_data[1] = data
    else:
        for i in range(num_groups):
            group_data[i + 1] = []
        for val in data:
            group_number = simpledialog.askinteger(
                "Group Assignment", f"Enter the group number for Sample {val[0]}:"
            )
            if group_number in group_data:
                group_data[group_number].append(val)

    if any(len(group) == 0 for group in group_data.values()):
        messagebox.showerror("Error", "Not enough data for statistical analysis.")
        return None, None

    report = []
    for group_number, group in group_data.items():
        group_values = [item[1] for item in group]
        mean = statistics.mean(group_values)
        stdev = statistics.stdev(group_values)
        median = statistics.median(group_values)
        report.append(
            f"Group {group_number}: Mean = {mean:.3f}, Standard Deviation = {stdev:.3f}, Median = {median:.3f}"
        )

    if num_groups == 2:
        group_1_values = [item[1] for item in group_data[1]]
        group_2_values = [item[1] for item in group_data[2]]
        t_stat, p_value = ttest_ind(group_1_values, group_2_values)
        report.append(f"T-Test: T-statistic = {t_stat}, P-value = {p_value}")
    elif num_groups > 2:
        group_values_list = [
            [item[1] for item in group] for group in group_data.values()
        ]
        f_stat, p_value = f_oneway(*group_values_list)
        report.append(f"ANOVA: F-statistic = {f_stat}, P-value = {p_value}")
    else:
        report.append("Only one group found. No t-test or ANOVA performed.")

    statistical_report = "\n".join(report)
    print(statistical_report)
    return group_data, statistical_report


def plot_adjusted_data(adjusted_values, species_d13c_value, group_data=None):
    if group_data is None:
        if species_d13c_value and any(species_d13c_value.values()):
            messagebox.askyesno(
                "Include Species Data",
                "Do you want to include the leaf delta 13C value from the database in the plotting?",
            )

        num_groups = simpledialog.askinteger(
            "Number of Groups", "How many groups do you have?"
        )
        if num_groups is None:
            num_groups = 0

        group_data = {}
        if num_groups in (0, 1):
            group_data[1] = adjusted_values
        if num_groups >= 2:
            for i in range(num_groups):
                group_data[i + 1] = []

            for sample_id in [val[0] for val in adjusted_values]:
                group_number = simpledialog.askinteger(
                    "Group Assignment",
                    f"Enter the group number for sample '{sample_id}':",
                )
                if group_number in group_data:
                    group_data[group_number].append(sample_id)

        if any(len(group) == 0 for group in group_data.values()):
            messagebox.showerror("Error", "Not enough data for plotting.")
            return
    else:
        group_data = group_data

    give_sample_names = messagebox.askyesno(
        "Sample Names", "Do you want to give the samples names?"
    )

    sample_ids = [val[0] for val in adjusted_values]
    adjusted_deltas = [val[1] for val in adjusted_values]

    if give_sample_names:
        sample_names = [
            simpledialog.askstring("Sample Name", f"Enter name for sample {sample_id}:")
            for sample_id in sample_ids
        ]
    else:
        sample_names = sample_ids

    x = np.arange(len(sample_names))

    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    bars = ax.bar(np.arange(len(sample_names)), adjusted_deltas)

    ax.set_xlabel("Sample")
    ax.set_ylabel("Delta 13C")
    ax.set_title("Leaf Delta 13C")

    ax.set_xticks(np.arange(len(sample_names)))
    ax.set_xticklabels(sample_names, rotation=45, ha="right")

    if species_d13c_value and any(species_d13c_value.values()):
        for idx, (species, value) in enumerate(species_d13c_value.items()):
            if value is not None:
                plt.axhline(
                    y=value,
                    color="black",
                    linestyle="--",
                    label=f"{value} ({species} leaf delta\n13C literature value)",
                )
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    if group_data:
        group_data = {
            group_number: (
                [entry[0] for entry in group] if isinstance(group[0], tuple) else group
            )
            for group_number, group in group_data.items()
        }

        cmap = plt.get_cmap("tab10")
        colors = [cmap(i) for i in range(cmap.N)]

        group_colors = {
            group_number: colors[group_number % len(colors)]
            for group_number in group_data.keys()
        }

        for group_number, group in group_data.items():
            color = group_colors[group_number]
            for sample_id in group:
                if sample_id in sample_ids:
                    index = sample_ids.index(sample_id)
                    bars[index].set_color(color)

    plt.tight_layout()
    plt.show()


def prompt_for_species():
    messagebox.showinfo("Info", "Please enter the plant species in the provided field")


def show_initial_message():
    messagebox.showinfo("Info", "Please load the isotopic data file")


if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.title("Isotopic Data Analysis")

    # Create and position widgets
    load_isotopic_data_button = tk.Button(
        root, text="Load Isotopic Data", command=load_isotopic_data
    )
    load_isotopic_data_button.pack(pady=10)

    label = tk.Label(root, text="Enter Plant Species:")
    label.pack()

    entry = tk.Entry(root)
    entry.pack(pady=5)

    search_species_button = tk.Button(
        root, text="Search Species", command=search_species
    )
    search_species_button.pack(pady=10)

    plot_button = tk.Button(
        root,
        text="statistical analysis",
        command=lambda: statistical_analysis(adjusted_values),
    )
    plot_button.pack(pady=10)

    plot_button = tk.Button(
        root,
        text="Plot Data",
        command=lambda: plot_adjusted_data(
            adjusted_values, species_d13c_value, group_data
        ),
    )
    plot_button.pack(pady=10)

    show_initial_message()

    load_species_data()

    root.mainloop()
