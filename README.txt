******************************************************************************
* Summer Internship Project: UK Sports Viewership Data Collection & Analysis *
* Intern: Samuel Dunn | Supervisor: Dr. Peter Dawson                         *
******************************************************************************

* 1. OVERVIEW *
This directory contains the Python scripts utilized to extract live concurrent
viewer figures and event metadata from the BBC Sport digital infrastructure.
Data extraction targets the window.__INITIAL_DATA__ JSON payload embedded within
the webpage source.

* 2. FILE STRUCTURE *
Master_Orchestrator.py   -> Coordinates all individual sport scripts using
                            the 'schedule' library.
Football_Pipeline.py     -> Calculates fixture times and executes snapshots
                            at targeted match intervals.
Tennis_Pipeline.py       -> Polling script for live Wimbledon coverage.
F1_Pipeline.py           -> Polling script for Formula 1 Grand Prix sessions.
Golf_Pipeline.py         -> Polling script for The Open Championship.
Rugby_Pipeline.py        -> Polling script for Nations Championship fixtures.
Parser_General.py        -> Parses HTML files, performs data cleaning, and
                            merges pre-match betting odds from Betting_Odds.xlsx.
Parser_Wimbledon.py      -> Maps aggregate Wimbledon digital viewer metrics
                            specifically to active marquee court matches.
Wimbledon_Cleaner.py     -> Filters uninformative snapshots resulting from
                            weather delays.

* 3. REPLICATION PROCEDURE *
To execute the automated extraction pipeline:
   $ python Master_Orchestrator.py

To process saved HTML snapshots into the final panel dataset:
   $ python Parser_General.py

Notes: Due to file size and storage constraints, the complete archive of 1,025 
raw HTML snapshots has been processed into 'Final_Merged_Internship_Dataset.csv'.