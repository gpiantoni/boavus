from shutil import rmtree
from nipype import Workflow, Node, config, logging
from nipype.interfaces.freesurfer import ReconAll
from nipype.interfaces.utility import IdentityInterface

from .fmri import workflow_fmri
from .ieeg import workflow_ieeg
from ..corr import (function_corr,
                    function_corr_summary,
                    )


def workflow_corr_ieeg_fmri(PARAMETERS, FREESURFER_PATH):

    bids.iterables = ('subject', SUBJECTS)

    node_reconall = Node(ReconAll(), name='freesurfer')
    node_reconall.inputs.subjects_dir = str(FREESURFER_PATH)
    node_reconall.inputs.flags = ['-cw256', ]

    node_corr = Node(function_corr, name='corr_fmri_ecog')
    node_corr.inputs.pvalue = PARAMETERS['corr']['pvalue']

    node_corr_summary = JoinNode(
        function_corr_summary,
        name='corr_fmri_ecog_summary',
        joinsource='bids',
        joinfield=('in_files', 'ecog_files', 'fmri_files'),
        )

    w_fmri = workflow_fmri(PARAMETERS['fmri'])
    w_ieeg = workflow_ieeg(PARAMETERS['ieeg'])

    w = Workflow('grvx')

    if PARAMETERS['fmri']['graymatter']:
        w.connect(bids, 'subject', node_reconall, 'subject_id')  # we might use freesurfer for other stuff too
        w.connect(bids, 'anat', node_reconall, 'T1_files')
        w.connect(node_reconall, 'ribbon', w_fmri, 'graymatter.ribbon')

    w.connect(bids, 'ieeg', w_ieeg, 'read.ieeg')
    w.connect(bids, 'elec', w_ieeg, 'read.electrodes')

    w.connect(bids, 'anat', w_fmri, 'bet.in_file')
    w.connect(bids, 'func', w_fmri, 'feat_design.func')

    w.connect(bids, 'elec', w_fmri, 'at_elec.electrodes')

    w.connect(w_ieeg, 'ecog_compare.tsv_compare', node_corr, 'ecog_file')
    w.connect(w_fmri, 'at_elec.fmri_vals', node_corr, 'fmri_file')

    w.connect(node_corr, 'out_file', node_corr_summary, 'in_files')
    w.connect(w_ieeg, 'ecog_compare.tsv_compare', node_corr_summary, 'ecog_files')
    w.connect(w_fmri, 'at_elec.fmri_vals', node_corr_summary, 'fmri_files')

    return w
