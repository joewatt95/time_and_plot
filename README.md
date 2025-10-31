# Time and Plot

A command-line utility to run a command with different input values, measure its execution time, and plot the results. It provides a real-time Text User Interface (TUI) to monitor the progress of the jobs.

## Features

- **Command Timing**: Time any command-line tool with various inputs.
- **Parallel Execution**: Run multiple jobs in parallel to speed up the timing process.
- **TUI Dashboard**: An interactive TUI to monitor the status of each job, including progress, mean/median times, and min/max values, powered by [Rich](https://rich.readthedocs.io/en/stable/).
- **Console Fallback**: If the TUI is not supported or disabled, it falls back to a simple console logger.
- **Plotting**: Generates a plot of the results using `matplotlib`.
- **Data Export**: Save the timing statistics to a CSV file.

## Installation

This project uses Poetry for dependency management.

First, install Poetry by following the instructions on the [official website](https://python-poetry.org/docs/#installation).

Then, from this directory, install the dependencies:

```bash
poetry install
```

To include the optional plotting dependencies, use:

```bash
poetry install --with plot
```

## Usage

The tool is run from the command line using `poetry run`, which executes the command within the project's virtual environment. You need to provide a command template and a list of values to substitute into it.

### Basic Usage

```bash
poetry run python -m time_and_plot "command_template {}" value1 value2 value3
```

- `command_template {}`: The command to run, with `{}` as a placeholder for the value.
- `value1 value2 value3`: A list of values to be used in the command.

### Examples

**Example 1: Time the `sleep` command**

Time the `sleep` command with different durations (0.1s, 0.2s, 0.5s, 1.0s).

```bash
poetry run python -m time_and_plot "sleep {}" 0.1 0.2 0.5 1.0
```

**Example 2: Time an application with multiple repetitions**

Time a program `my_app` with different input values for the `-n` flag, running 10 repetitions for each value and using up to 4 parallel processes.

```bash
poetry run python -m time_and_plot -r 10 -p 4 "my_app -n {}" 100 500 1000 5000
```

**Example 3: Save the plot to a file**

Run the `sleep` command and save the resulting plot to `my_plot.svg`.

```bash
poetry run python -m time_and_plot --output-plot my_plot.svg "sleep {}" 0.1 0.2
```

**Example 4: Show the plot interactively**

```bash
poetry run python -m time_and_plot --show-plot "sleep {}" 0.1 0.2
```

**Example 5: Save statistics to a CSV file**

```bash
poetry run python -m time_and_plot --output-stats stats.csv "sleep {}" 0.1 0.2
```

**Example 6: Increase logging verbosity**

```bash
poetry run python -m time_and_plot -v "sleep {}" 0.1
poetry run python -m time_and_plot -vv "sleep {}" 0.1
```

### Command-line options

- `command`: The command template to run.
- `values`: One or more values to substitute into the command.
- `-r, --reps`: Number of repetitions for each value. Default: 5.
- `-p, --parallel`: Maximum number of parallel processes. Default: all available cores.
- `--show-plot`: Show the plot interactively.
- `--output-plot`: Output filename for the plot.
- `--output-stats`: Output filename for the statistics in CSV format.
- `--no-tui`: Disable the TUI and use simple console logging.
- `-v, --verbose`: Increase verbosity (e.g., -v, -vv, -vvv).

## Output

The tool can generate two types of output:

1.  **Plot**: A plot of the input values vs. execution time. It can be displayed interactively or saved to a file.
2.  **CSV File**: A CSV file containing the timing statistics (mean, median, min, max) for each input value.
