from nipype import Workflow, Node
from nipype.interfaces.utility import IdentityInterface

from .fmri import workflow_fmri
from .ieeg import workflow_ieeg
from ..corr import function_corr


def workflow_corr_ieeg_fmri(PARAMETERS, FREESURFER_PATH):

    input = Node(IdentityInterface(fields=['subject', 'T1w', 'bold', 'ieeg', 'electrodes']), name='input')

    node_corr = Node(function_corr, name='corr_fmri_ecog')
    node_corr.inputs.pvalue = PARAMETERS['corr']['pvalue']

    w_fmri = workflow_fmri(PARAMETERS['fmri'], FREESURFER_PATH)
    w_ieeg = workflow_ieeg(PARAMETERS['ieeg'])

    w = Workflow('grvx')

    w.connect(input, 'ieeg', w_ieeg, 'input.ieeg')
    w.connect(input, 'electrodes', w_ieeg, 'input.electrodes')

    w.connect(input, 'subject', w_fmri, 'input.subject')
    w.connect(input, 'T1w', w_fmri, 'input.T1w')
    w.connect(input, 'bold', w_fmri, 'input.bold')
    w.connect(input, 'electrodes', w_fmri, 'input.electrodes')

    w.connect(w_ieeg, 'ecog_compare.tsv_compare', node_corr, 'ecog_file')
    w.connect(w_fmri, 'at_elec.fmri_vals', node_corr, 'fmri_file')

    return w
