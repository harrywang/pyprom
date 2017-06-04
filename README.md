# What is PyProM?
PyProM is a Python-based, open-source process mining package.

# About Event Logs

The example logs (in /logs folder) are from the ProM site (http://www.promtools.org). Each line is a case with a sequence of activities.

TODO: Logs should be stored in a csv file with columns, such as Case ID, Activity, Start Time, End Time, Agent, Role, and Data. This format is used in Disco (https://fluxicon.com/disco/)

# Setup Instructions
Intall graphviz - we use graphviz to visualize the process in petri net format
```
brew install graphviz
```
Setup virtual environment and activate it:
```
virtualenv venv
source venv/bin/activate
```
Install packages: `pip install -r requirements.txt`

Run the program with different log files to generate the petri net images and related dot files in the output folder
```
python pyprom.py exercise1.txt
```

# References
- PyPM: https://github.com/tdi/pypm: I referred to this project to start PyProM - many thanks to the author.
- ProM: http://www.promtools.org
- Disco: https://fluxicon.com/disco/
