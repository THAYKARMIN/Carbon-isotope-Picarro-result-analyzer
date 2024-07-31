import pytest
import tempfile
import os
from unittest import mock
from data_analyze import (
    read_csv,
    glucose_average,
    adjusted_delta,
    load_isotopic_data,
    load_species_data,
    statistical_analysis,
    plot_adjusted_data,
    ask_for_statistical_analysis,
    adjusted_values,
    offer_to_plot_data,
)

# Sample data for testing
isotopic_data = """Sample Id,Peak Number,Description,Start Time,End Time,Max 12CO2 (ppm),12CO2 Integral,13CO2 Integral,Delta CRDS,12CO2 Baseline,13CO2 Baseline,Threshold,Number of data points,Time interval (seconds)
1,1,,2024/07/03 11:04:36,2024/07/03 11:12:50,2915.843,560350.144,6259.660,-6.743,1.998,0.055,70.000,461,494.242
2,1,,2024/07/03 11:20:01,2024/07/03 11:27:45,3811.591,708664.534,7918.663,-6.803,17.034,0.223,70.000,431,463.462
3,1,,2024/07/03 11:35:33,2024/07/03 11:43:12,3626.345,674690.960,7539.528,-6.741,3.941,0.076,70.000,427,459.138
4,1,,2024/07/03 11:51:04,2024/07/03 11:58:42,3526.403,653342.882,7273.750,-10.310,3.853,0.076,70.000,427,457.261
5,1,,2024/07/03 12:06:36,2024/07/03 12:14:04,3223.784,592697.817,6603.579,-9.451,3.870,0.077,70.000,418,447.916
"""


def test_read_csv():
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", encoding="utf-8"
    ) as temp_file:
        temp_file.write(isotopic_data)
        temp_file_path = temp_file.name

    try:
        expected_output = [
            {
                "Sample Id": "1",
                "Peak Number": "1",
                "Description": "",
                "Start Time": "2024/07/03 11:04:36",
                "End Time": "2024/07/03 11:12:50",
                "Max 12CO2 (ppm)": "2915.843",
                "12CO2 Integral": "560350.144",
                "13CO2 Integral": "6259.660",
                "Delta CRDS": "-6.743",
                "12CO2 Baseline": "1.998",
                "13CO2 Baseline": "0.055",
                "Threshold": "70.000",
                "Number of data points": "461",
                "Time interval (seconds)": "494.242",
            },
            {
                "Sample Id": "2",
                "Peak Number": "1",
                "Description": "",
                "Start Time": "2024/07/03 11:20:01",
                "End Time": "2024/07/03 11:27:45",
                "Max 12CO2 (ppm)": "3811.591",
                "12CO2 Integral": "708664.534",
                "13CO2 Integral": "7918.663",
                "Delta CRDS": "-6.803",
                "12CO2 Baseline": "17.034",
                "13CO2 Baseline": "0.223",
                "Threshold": "70.000",
                "Number of data points": "431",
                "Time interval (seconds)": "463.462",
            },
            {
                "Sample Id": "3",
                "Peak Number": "1",
                "Description": "",
                "Start Time": "2024/07/03 11:35:33",
                "End Time": "2024/07/03 11:43:12",
                "Max 12CO2 (ppm)": "3626.345",
                "12CO2 Integral": "674690.960",
                "13CO2 Integral": "7539.528",
                "Delta CRDS": "-6.741",
                "12CO2 Baseline": "3.941",
                "13CO2 Baseline": "0.076",
                "Threshold": "70.000",
                "Number of data points": "427",
                "Time interval (seconds)": "459.138",
            },
            {
                "Sample Id": "4",
                "Peak Number": "1",
                "Description": "",
                "Start Time": "2024/07/03 11:51:04",
                "End Time": "2024/07/03 11:58:42",
                "Max 12CO2 (ppm)": "3526.403",
                "12CO2 Integral": "653342.882",
                "13CO2 Integral": "7273.750",
                "Delta CRDS": "-10.310",
                "12CO2 Baseline": "3.853",
                "13CO2 Baseline": "0.076",
                "Threshold": "70.000",
                "Number of data points": "427",
                "Time interval (seconds)": "457.261",
            },
            {
                "Sample Id": "5",
                "Peak Number": "1",
                "Description": "",
                "Start Time": "2024/07/03 12:06:36",
                "End Time": "2024/07/03 12:14:04",
                "Max 12CO2 (ppm)": "3223.784",
                "12CO2 Integral": "592697.817",
                "13CO2 Integral": "6603.579",
                "Delta CRDS": "-9.451",
                "12CO2 Baseline": "3.870",
                "13CO2 Baseline": "0.077",
                "Threshold": "70.000",
                "Number of data points": "418",
                "Time interval (seconds)": "447.916",
            },
        ]
        assert read_csv(temp_file_path) == expected_output
    finally:
        os.remove(temp_file_path)


def test_glucose_average():
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", encoding="utf-8"
    ) as temp_file:
        temp_file.write(isotopic_data)
        temp_file_path = temp_file.name

    try:
        data = read_csv(temp_file_path)
        expected_average = (-6.743 - 6.803 - 6.741) / 3
        assert glucose_average(data) == pytest.approx(expected_average, rel=1e-5)
    finally:
        os.remove(temp_file_path)


def test_adjusted_delta():
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", encoding="utf-8"
    ) as temp_file:
        temp_file.write(isotopic_data)
        temp_file_path = temp_file.name

    try:
        data = read_csv(temp_file_path)
        average = glucose_average(data)
        adjustment = average + 11.768
        expected_adjusted_values = [
            ("4", -10.310 - adjustment),
            ("5", -9.451 - adjustment),
        ]
        result = adjusted_delta(data, average)
        for (sample_id, adjusted_value), (expected_id, expected_value) in zip(
            result, expected_adjusted_values
        ):
            assert sample_id == expected_id
            assert adjusted_value == pytest.approx(expected_value, rel=1e-5)
    finally:
        os.remove(temp_file_path)


@mock.patch("data_analyze.filedialog.askopenfilename")
@mock.patch("data_analyze.messagebox.showinfo")
@mock.patch("data_analyze.read_csv")
@mock.patch("data_analyze.glucose_average")
def test_load_isotopic_data(
    mock_glucose_average,
    mock_read_csv,
    mock_showinfo,
    mock_askopenfilename,
):
    mock_askopenfilename.return_value = "/fake/path/to/file.csv"

    load_isotopic_data()

    mock_askopenfilename.assert_called_once()
    mock_read_csv.assert_called_once_with("/fake/path/to/file.csv")
    assert mock_showinfo.call_count == 2
    mock_showinfo.assert_any_call(
        "Info", "Processed isotopic data and calculated adjusted delta values."
    )
    mock_showinfo.assert_any_call(
        "Info", "Please enter the plant species in the provided field"
    )


@pytest.fixture
def mock_read_csv():
    with mock.patch("data_analyze.read_csv") as m:
        yield m


@pytest.fixture
def mock_showerror():
    with mock.patch("data_analyze.messagebox.showerror") as m:
        yield m


def test_load_species_data(mock_read_csv, mock_showerror):

    load_species_data()
    mock_read_csv.assert_called_once_with("leaf13C_database.csv")
    mock_showerror.assert_not_called()


@mock.patch("data_analyze.simpledialog.askinteger")
def test_statistical_analysis_one_group(mock_askinteger):
    test_data = [
        ("4", -15.315666666666669),
        ("5", -14.456666666666667),
        ("6", -14.710666666666668),
        ("7", -14.739666666666668),
        ("8", -15.247666666666667),
        ("9", -15.341666666666669),
        ("10", -14.851666666666667),
        ("11", -15.735666666666667),
        ("12", -14.621666666666666),
        ("13", -14.685666666666666),
    ]

    mock_askinteger.side_effect = [1]
    group_data, report = statistical_analysis(test_data)
    expected_group_data = {1: test_data}

    expected_report = """\
Group 1: Mean = -14.971, Standard Deviation = 0.411, Median = -14.796
Only one group found. No t-test or ANOVA performed."""

    assert group_data == expected_group_data
    assert report.strip() == expected_report.strip()


@mock.patch("data_analyze.simpledialog.askinteger")
def test_statistical_analysis_two_groups(mock_askinteger):

    test_data = [
        ("1", -15.315666666666669),
        ("2", -14.456666666666667),
        ("3", -14.710666666666668),
        ("4", -14.739666666666668),
        ("5", -15.247666666666667),
        ("6", -15.341666666666669),
        ("7", -14.851666666666667),
        ("8", -15.735666666666667),
        ("9", -14.621666666666666),
        ("10", -14.685666666666666),
    ]

    side_effect_list = [2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 2]

    mock_askinteger.side_effect = side_effect_list

    group_data, report = statistical_analysis(test_data)

    group1_data = [
        val for i, val in enumerate(test_data) if side_effect_list[i + 1] == 1
    ]
    group2_data = [
        val for i, val in enumerate(test_data) if side_effect_list[i + 1] == 2
    ]

    expected_group_data = {1: group1_data, 2: group2_data}

    expected_report = """\
Group 1: Mean = -14.867, Standard Deviation = 0.346, Median = -14.781
Group 2: Mean = -15.126, Standard Deviation = 0.504, Median = -15.041
T-Test: T-statistic = 0.9703632432437701, P-value = 0.36028493501805753"""

    assert group_data == expected_group_data
    assert report.strip() == expected_report.strip()


@mock.patch("data_analyze.simpledialog.askinteger")
def test_statistical_analysis_three_groups(mock_askinteger):

    test_data = [
        ("1", -15.315666666666669),
        ("2", -14.456666666666667),
        ("3", -14.710666666666668),
        ("4", -14.739666666666668),
        ("5", -15.247666666666667),
        ("6", -15.341666666666669),
        ("7", -14.851666666666667),
        ("8", -15.735666666666667),
        ("9", -14.621666666666666),
        ("10", -14.685666666666666),
    ]

    side_effect_list = [3, 1, 2, 2, 3, 1, 3, 1, 2, 3, 1]
    mock_askinteger.side_effect = side_effect_list
    group_data, report = statistical_analysis(test_data)
    group1_data = [
        val for i, val in enumerate(test_data) if side_effect_list[i + 1] == 1
    ]
    group2_data = [
        val for i, val in enumerate(test_data) if side_effect_list[i + 1] == 2
    ]
    group3_data = [
        val for i, val in enumerate(test_data) if side_effect_list[i + 1] == 3
    ]

    expected_group_data = {1: group1_data, 2: group2_data, 3: group3_data}

    expected_report = """\
Group 1: Mean = -15.025, Standard Deviation = 0.305, Median = -15.050
Group 2: Mean = -14.968, Standard Deviation = 0.677, Median = -14.711
Group 3: Mean = -14.901, Standard Deviation = 0.386, Median = -14.740
ANOVA: F-statistic = 0.061986908850186824, P-value = 0.9404052364659001"""

    assert group_data == expected_group_data
    assert report.strip() == expected_report.strip()


@pytest.fixture
def mock_plotting():
    with mock.patch("matplotlib.pyplot.show") as mock_show:
        yield mock_show


def test_plot_adjusted_data(mock_plotting):
    mock_show = mock_plotting

    adjusted_values = [("Sample1", -15.0), ("Sample2", -14.5), ("Sample3", -14.8)]
    species_d13c_value = {"Species1": -14.7, "Species2": -15.0}

    group_data = {1: [("Sample1", -15.0), ("Sample2", -14.5)], 2: [("Sample3", -14.8)]}

    with mock.patch("data_analyze.simpledialog.askinteger") as mock_askinteger:
        with mock.patch("data_analyze.simpledialog.askstring") as mock_askstring:
            with mock.patch("data_analyze.messagebox.askyesno") as mock_askyesno:
                mock_askinteger.side_effect = [2, 1, 2, 1]
                mock_askstring.side_effect = ["Name1", "Name2", "Name3"]
                mock_askyesno.side_effect = [True, True]

                plot_adjusted_data(
                    adjusted_values, species_d13c_value, group_data=group_data
                )

                mock_show.assert_called_once()


@pytest.fixture(autouse=True)
def clear_adjusted_values():
    adjusted_values.clear()
    yield
    adjusted_values.clear()


@mock.patch("data_analyze.messagebox.showwarning")
@mock.patch("data_analyze.messagebox.askyesno")
@mock.patch("data_analyze.statistical_analysis")
@mock.patch("data_analyze.offer_to_plot_data")
def test_ask_for_statistical_analysis(
    mock_offer_to_plot_data, mock_statistical_analysis, mock_askyesno, mock_showwarning
):

    adjusted_values[:] = [(1, 2.3), (2, 3.4)]
    mock_askyesno.return_value = True
    mock_statistical_analysis.return_value = (
        {"group1": [(1, 2.3)], "group2": [(2, 3.4)]},
        "Report",
    )

    ask_for_statistical_analysis()

    mock_showwarning.assert_not_called()
    mock_askyesno.assert_called_once_with(
        "Statistical Analysis", "Do you want to perform statistical analysis?"
    )
    mock_statistical_analysis.assert_called_once_with(adjusted_values)
    mock_offer_to_plot_data.assert_called_once()


@mock.patch("data_analyze.plot_adjusted_data")
@mock.patch("data_analyze.messagebox.askyesno")
def test_offer_to_plot_data(mock_askyesno, mock_plot_adjusted_data):

    mock_askyesno.side_effect = [True, True]
    group_data = {"group1": [("Sample1", -15.0)], "group2": [("Sample2", -14.5)]}
    species_d13c_value = {"Species1": -14.7}

    offer_to_plot_data(group_data, species_d13c_value)

    mock_askyesno.assert_any_call("Plot Data", "Do you want to plot the data?")
    mock_askyesno.assert_any_call(
        "Include Delta 13C",
        "Do you want to include the leaf delta 13C value from the database in the plotting?",
    )
    mock_plot_adjusted_data.assert_called_once_with(
        adjusted_values, species_d13c_value, group_data
    )
