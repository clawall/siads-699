# SIADS-699:  Team 12: Effects of social media from influential people into the Stock Market
Shared repository for team 12: `This is Fine` project on SIADS-699.

This repository contains a subset of available packages on the Coursera repository and is meant to ease the collaboration between the team as well as help track our progress.

## Team members
- Roy Spencer - roylt
- César Silveira - clawall
- Darienne Sautter - dsautter

## Data Citation
Wharton Research Data Services. "WRDS" wrds.wharton.upenn.edu, accessed 2025-04-07.

## Pre-requisities
- Python 3
- Python virtualenv

### About Virtualenv
Virtualenv is an amazing tool that helps us isolate our environment.  By containing our libraries within its folder structure, we avoid the use of libraries installed on our local OS and can easily share the exact environment amongst the team members.

You can have as many virtual environments as you want but it's a good idea to use a single environment for a specific project.  Each time we add a new library, we need to save it's name (following the pattern`library-name==version`) on a file called `requirements.txt`.  If we ever need to recreate an environment, we can just use the commands specified on the next session to create it.

Please refer to its [documentation](https://docs.python.org/3/library/venv.html) for more instructions and a how-to-use guide.

## Installation
By having Python 3 and Virtualenv installed (please refer to the guides for your operating system within their respective docs) we just need to start our virtual environment and install the libraries contained within our requirements file.

Warning:  The first command on the shell bellow assumes that your Python3 binary is called "python3" and is accessible on the OS path.  Please update this accordingly.

```console
# 1. Creates a new environment with the python executable "python3" on the folder "./.env"
virtualenv -p python3 .env

# 2. Activates the newly created virtual environment
source .env/bin/activate

# 3. Installs the libraries indicated on the "requirements.txt" file
pip install -r requirements.txt

# 4. Running parts of the project:

## 4.1. If you want to edit/run the Notebooks:  Starts Jupyter Lab so we can work (it will be opened on a browser)
jupyter lab

## 4.2. If you want to run the ML Pipeline and create fresh CSV files to train the Models
make
```

## Folder structure
- ./ --> Project settings
- ./notebooks/ --> Notebooks for the project
- ./src --> Python files (utilities)
- ./test --> Unit tests

## Machine Learning Pipeline
A pipeline was constructed to prepare and clean data in preparation for the Models to be trained.  It can be triggered by running the `make` command and will run a series of targets:
1. Read from the list of Twitter handles, scrapes Politiweet and conver them to a list of user IDs;
2. Scrapers Politiweet for all tweets from the list of user IDs;
3. Splits the CSV file generated in the previous steps into smaller chunks so they can be persisted in GitHub;
4. Cleans up and merges the splitted CSV files into a single one to be read and processed in Notebooks;

### Extra target
There's also an extra step that's not part of the main Pipeline, which converts the really large TAQ files (about 60Gb per file, corresponding to 1 year) into splitted compressed parquet files that can be stored in GitHub while also allowing us to load them directly into Pandas DataFrames.

## Running Unit Tests  

This project includes unit tests to ensure the correctness of utility functions. The tests are written using `pytest` and can be found in the `tests/` directory.  

### **Prerequisites**  
Make sure you have test libraries installed. If it's not installed, you can add it using:  

```bash
pip install -r requirements-test.txt
```

### Running All Tests
To run all unit tests, navigate to the root directory of the project and execute:

```bash
pytest
```

### Running Tests for a Specific File
If you want to run tests from a specific file, use:

```bash
pytest tests/test_utils.py
````

### Running a Specific Test Case
To run an individual test case, use the -k option with a part of the test name:

```bash
pytest -k "test_basic_functionality"
```

### Running Tests with Detailed Output
For more verbose output, use the -v flag:

```bash
pytest -v
```

### Checking Test Coverage
If you want to check test coverage using pytest-cov, install it first:

```bash
pip install pytest-cov
```

Then run:

```bash
pytest --cov=src
```
This will display a coverage report for the src/ directory.

## Code Style and Linting

We use `pylint` to enforce PEP 8 coding standards in this project.

### Installing the Linter
Ensure you have `pylint` installed. If not, install it using:
```bash
pip install -r requirements-test.txt
```

### Running the Linter
To check for PEP 8 violations, run the following command in the project's root directory:

```bash
pylint --fail-under=8 $(git ls-files 'src/*.py')
```
This will scan all Python files inside the src/ directory.

### Ignoring Files and Folders
If you want to ignore specific files or folders, you can configure .pylintrc in the project's root.

Example `.pylintrc` Configuration:
```ini
[MAIN]
ignore-paths=src/.ipynb_checkpoints
ignore-patterns=^\.#
```
This will exclude the notebooks/, migrations/, tests/, and some_folder/ directories from linting.

## GitHub Actions: Lint & Test Workflow
This project uses GitHub Actions to automate code quality checks. The workflow includes two jobs:

Lint - Runs pylint to check for code quality and formatting issues.
Test - Runs unit tests using pytest.

### Workflow Configuration
The GitHub Actions workflow is defined in .github/workflows/pylint.yml and runs automatically on every push and pull request.

### How It Works
- On push or pull request, GitHub Actions:
1. Installs Python dependencies.
2. Runs Pylint (--fail-under=8 ensures a minimum score of 8).
3. If linting succeeds, it proceeds to unit tests with pytest.

### Passing Criteria
- Linting must pass (score ≥ 8).
- Tests must pass with pytest.
