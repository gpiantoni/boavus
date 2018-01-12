from pathlib import Path

TEST_PATH = Path(__file__).resolve().parent
DATA_PATH = TEST_PATH / 'data'
BIDS_PATH = DATA_PATH / 'bids'
BIDS_PATH.mkdir(parents=True, exist_ok=True)
DERIVATIVES_PATH = DATA_PATH / 'derivatives'
FREESURFER_PATH = DERIVATIVES_PATH / 'freesurfer'
FEAT_PATH = DERIVATIVES_PATH / 'feat'
FEAT_PATH.mkdir(parents=True, exist_ok=True)
