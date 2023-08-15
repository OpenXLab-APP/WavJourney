import time
import argparse

import pipeline

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--full', action='store_true', help='Go through the full process')
parser.add_argument('--input-text', type=str, default='', help='input text or text file')
parser.add_argument('--session-id', type=str, default='', help='session id, if set to empty, system will allocate an id')
args = parser.parse_args()

if args.full:
    input_text = args.input_text

    start_time = time.time()
    session_id = pipeline.init_session(args.session_id)
    
    print(f"Session {session_id} is created.")

    pipeline.full_steps(session_id, input_text)
    end_time = time.time()

    print(f"WavJourney took {end_time - start_time:.2f} seconds to complete.")
