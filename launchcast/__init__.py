"""launchcast: terminal-only launch forecaster for in-licensed / MOU pharma assets.

Given a country and an asset it prints the inputs (epidemiology, reimbursement,
competing therapies, pricing references), a worked 10-year forecast, a launch
verdict with the rules that produced it, a side-by-side against a comparator
country, and a bridge showing where the model disagrees with the originator's
own numbers. Everything is deterministic and runs offline from the JSON in
./data; every number carries an evidence grade and a source.
"""

__version__ = "0.1.0"
