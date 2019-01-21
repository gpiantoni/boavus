from nipype import Node
from boavus.mri.neuropythy import function_neuropythy_atlas

from .paths import ANALYSIS_PATH


def test_neuropythy_atlas():
    n = Node(function_neuropythy_atlas, 'atlas')
    n.base_dir = str(ANALYSIS_PATH / 'neuropythy')
    n.inputs.subject_id = 'sub-delft'
    n.run()
