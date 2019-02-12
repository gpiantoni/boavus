from nipype import Node
from boavus.mri.neuropythy import function_neuropythy_atlas

from .paths import ANALYSIS_PATH, FREESURFER_PATH


def test_neuropythy_atlas():

    n = Node(function_neuropythy_atlas, 'atlas')
    n.base_dir = str(ANALYSIS_PATH)
    n.inputs.subject_id = 'sub-delft'
    n.inputs.subjects_dir = str(FREESURFER_PATH)
    n.run()
