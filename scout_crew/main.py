#!/usr/bin/env python
import sys
import warnings

from src.crew import ScoutCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """

    inputs = {
        'topic': 'I need a right-back who is defensive-minded but can also support play creation through the middle of the field'
    }
    ScoutCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()

