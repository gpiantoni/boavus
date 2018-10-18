from shutil import rmtree
from nipype import Workflow, Node, MapNode, config, logging
from nipype.interfaces.utility import IdentityInterface
from ..ieeg import (function_ieeg_read,
                    function_ieeg_preprocess,
                    function_ieeg_powerspectrum,
                    function_ieeg_compare,
                    )


def workflow_ieeg(NIPYPE_PATH, PARAMETERS):

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

    input = Node(IdentityInterface(fields=['ieeg', 'electrodes']), name='input')

    node_read = Node(function_ieeg_read, name='read')
    node_read.inputs.conditions = {'move': 'move', 'rest': 'rest'}
    node_read.inputs.minimalduration = 20

    node_preprocess = MapNode(function_ieeg_preprocess, name='preprocess', iterfield=['ieeg', ])
    node_preprocess.inputs.duration = PARAMETERS['preprocess']['duration']
    node_preprocess.inputs.reref = PARAMETERS['preprocess']['reref']
    node_preprocess.inputs.offset = PARAMETERS['preprocess']['offset']

    node_frequency = MapNode(function_ieeg_powerspectrum, name='powerspectrum', iterfield=['ieeg', ])
    node_frequency.inputs.method = PARAMETERS['powerspectrum']['method']
    node_frequency.inputs.taper = PARAMETERS['powerspectrum']['taper']
    node_frequency.inputs.duration = PARAMETERS['powerspectrum']['duration']

    node_compare = Node(function_ieeg_compare, name='ecog_compare')
    node_compare.inputs.frequency = PARAMETERS['ecog_compare']['frequency']
    node_compare.inputs.baseline = PARAMETERS['ecog_compare']['baseline']
    node_compare.inputs.method = PARAMETERS['ecog_compare']['method']
    node_compare.inputs.measure = PARAMETERS['ecog_compare']['measure']

    w = Workflow('ieeg')
    w.base_dir = str(NIPYPE_PATH)

    w.connect(input, 'ieeg', node_read, 'ieeg')
    w.connect(node_read, 'ieeg', node_preprocess, 'ieeg')
    w.connect(node_preprocess, 'ieeg', node_frequency, 'ieeg')
    w.connect(node_frequency, 'ieeg', node_compare, 'in_files')

    w.write_graph(
        graph2use='flat',
        )

    rmtree(LOG_PATH, ignore_errors=True)
    LOG_PATH.mkdir()
    logging.update_logging(config)

    return w
