This repository contains a Python-based desktop application designed to load CSV files and generate basic statistical summaries through a graphical user interface (GUI). 
The project is structured to clearly separate user-interface functionality from data-processing logic, promoting maintainability, modularity, and testability.

Project Structure
├── gui.py
├── logic.py
└── testlogic.py

gui.py

Implements the Tkinter-based graphical interface that enables users to:

Load a CSV dataset.
Automatically detect numeric and categorical variables.
Generate numerical summaries (e.g., mean, median, standard deviation).
Generate categorical summaries (e.g., value counts).
Apply basic filters and aggregates for later visualisation.

All user interactions occur through this module, which acts as the presentation layer of the application.

logic.py

Contains the core data-processing functions used by the GUI, including:

CSV loading and validation.
Detection of numeric and categorical columns.
Filtering and aggregation utilities.
Functions to compute numerical and categorical summaries.

This module acts as the application’s “business logic,” fully decoupled from any interface code.

testlogic.py

Implements automated unit tests using pytest, ensuring:

All key functions in logic.py behave correctly.
Edge cases (empty data, missing columns, type inconsistencies) are handled appropriately.
This promotes reliability and supports regression testing as the project evolves.

