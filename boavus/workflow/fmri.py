from shutil import rmtree
from nipype import Workflow, Node, config, logging
from nipype.interfaces.fsl import FEAT, BET, FLIRT, Threshold
from numpy import arange

from ..fsl import function_prepare_design
from ..fmri import (function_fmri_compare,
                    function_fmri_atelec,
                    function_fmri_graymatter,
                    )

UPSAMPLE_RESOLUTION = 1
DOWNSAMPLE_RESOLUTION = 4
GRAYMATTER_THRESHOLD = 0.2


def workflow_fmri(NIPYPE_PATH, PARAMETERS, upsample, graymatter):
    """TODO: input and output"""

    LOG_PATH = NIPYPE_PATH / 'log'
    config.update_config({
        'logging': {
            'log_directory': LOG_PATH,
            'log_to_file': True,
            },
        'execution': {
            'crashdump_dir': LOG_PATH,
            'keep_inputs': 'false',
            'remove_unnecessary_outputs': 'false',
            },
        })

    node_bet = Node(BET(), name='bet')
    node_bet.inputs.frac = 0.5
    node_bet.inputs.vertical_gradient = 0
    node_bet.inputs.robust = True

    node_featdesign = Node(function_prepare_design, name='feat_design')

    node_feat = Node(FEAT(), name='feat')

    node_compare = Node(function_fmri_compare, name='fmri_compare')
    node_compare.inputs.measure = PARAMETERS['fmri_compare']['measure']
    node_compare.inputs.normalize_to_mean = PARAMETERS['fmri_compare']['normalize_to_mean']

    node_upsample = Node(FLIRT(), name='upsample')  # not perfect, there is a small offset
    node_upsample.inputs.apply_isoxfm = UPSAMPLE_RESOLUTION
    node_upsample.inputs.interp = 'nearestneighbour'

    node_downsample = Node(FLIRT(), name='downsample')  # not perfect, there is a small offset
    node_downsample.inputs.apply_xfm = True
    node_downsample.inputs.uses_qform = True
    # node_downsample.inputs.apply_isoxfm = DOWNSAMPLE_RESOLUTION
    node_downsample.inputs.interp = 'nearestneighbour'

    node_threshold = Node(Threshold(), name='threshold')
    node_threshold.inputs.thresh = GRAYMATTER_THRESHOLD
    node_threshold.inputs.args = '-bin'

    node_graymatter = Node(function_fmri_graymatter, name='graymatter')

    node_realign_gm = Node(FLIRT(), name='realign_gm')
    node_realign_gm.inputs.apply_xfm = True
    node_realign_gm.inputs.uses_qform = True

    kernel_sizes = arange(
        PARAMETERS['at_elec']['kernel_start'],
        PARAMETERS['at_elec']['kernel_end'],
        PARAMETERS['at_elec']['kernel_step'],
        )
    node_atelec = Node(function_fmri_atelec, name='at_elec')
    node_atelec.inputs.distance = PARAMETERS['at_elec']['distance']
    node_atelec.inputs.kernel_sizes = list(kernel_sizes)
    node_atelec.inputs.graymatter = graymatter

    w = Workflow('fmri')
    w.base_dir = str(NIPYPE_PATH)
    w.connect(node_bet, 'out_file', node_featdesign, 'anat')

    w.connect(node_featdesign, 'fsf_file', node_feat, 'fsf_file')
    w.connect(node_feat, 'feat_dir', node_compare, 'feat_path')

    if upsample:
        w.connect(node_compare, 'out_file', node_upsample, 'in_file')
        w.connect(node_compare, 'out_file', node_upsample, 'reference')
        w.connect(node_upsample, 'out_file', node_atelec, 'in_file')
    else:
        w.connect(node_compare, 'out_file', node_atelec, 'in_file')

    if graymatter:

        node_reconall = Node(ReconAll(), name='freesurfer')
        node_reconall.inputs.subjects_dir = str(FREESURFER_PATH)
        node_reconall.inputs.flags = ['-cw256', ]

        if upsample:
            w.connect(node_graymatter, 'out_file', node_realign_gm, 'in_file')
            w.connect(node_upsample, 'out_file', node_realign_gm, 'reference')
            w.connect(node_realign_gm, 'out_file', node_threshold, 'in_file')
        else:
            w.connect(node_graymatter, 'out_file', node_downsample, 'in_file')
            w.connect(node_compare, 'out_file', node_downsample, 'reference')
            w.connect(node_downsample, 'out_file', node_threshold, 'in_file')

        w.connect(node_threshold, 'out_file', node_atelec, 'graymatter')

    w.write_graph(
        graph2use='flat',
        )

    rmtree(LOG_PATH, ignore_errors=True)
    LOG_PATH.mkdir(exist_ok=True)
    logging.update_logging(config)

    return w
