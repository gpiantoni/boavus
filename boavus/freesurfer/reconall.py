from nipype import Node
from nipype.interfaces.freesurfer import ReconAll

from os import setpgrp
from subprocess import Popen

from bidso import file_Core
from bidso.find import find_in_bids

from ..utils import ENVIRON


node_reconall = Node(ReconAll(), name='reconall')
# node_reconall.inputs.subjects_dir
# node_reconall.inputs.subject_id
# node_reconall.inputs.T1_files
node_reconall.inputs.flags = ['-cw256', ]
node_reconall.inputs.directive = 'all'
