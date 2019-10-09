import argparse

from igclib.model.race import Race


def argument_parser():
    parser = argparse.ArgumentParser(description='igclib - race exporter')
    parser.add_argument('--task', required=True, type=str, help='Task file path')    
    parser.add_argument('--flights', required=True, type=str, help='IGC tracks directory path')
    parser.add_argument('--export_path', required=True, type=str, help='Path to save the race')
    parser.add_argument('--n_jobs', type=int, default=-1, help='Number of cores used (-1 to use all cores)')

    return parser

if __name__ == '__main__':

    # parse arguments
    parser = argument_parser()
    args = parser.parse_args()

    TASK_FILE = args.task
    TRACKS_DIR = args.flights
    N_JOBS = args.n_jobs
    RACE_PATH = args.export_path
    
    r =  Race(TRACKS_DIR, TASK_FILE, N_JOBS)
    r.save(RACE_PATH)
