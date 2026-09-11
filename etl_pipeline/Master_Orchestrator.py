import schedule
import time
import os

# Updated to match the new Title Case Python filenames
from Football_Pipeline import run_football_pipeline
from Tennis_Pipeline import run_tennis_pipeline
from F1_Pipeline import run_f1_pipeline
from Golf_Pipeline import run_golf_pipeline
from Rugby_Pipeline import run_rugby_pipeline

os.environ['TZ'] = 'Europe/London'
time.tzset()

schedule.every().day.at("23:00").do(run_football_pipeline)

schedule.every(15).minutes.do(run_f1_pipeline)
schedule.every(15).minutes.do(run_golf_pipeline)
schedule.every(15).minutes.do(run_tennis_pipeline)
schedule.every(15).minutes.do(run_rugby_pipeline)

if __name__ == "__main__":
    print("Master pipeline orchestrator initialized.")
    print("Executing initial verification check across all sport pipelines...")
    
    run_football_pipeline()
    run_tennis_pipeline()
    run_f1_pipeline()
    run_golf_pipeline()
    run_rugby_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(30)