from nipype import Workflow, Node
from nipype.interfaces.ants import Registration, ApplyTransforms
from nipype.interfaces.freesurfer import MRIConvert
from nipype.interfaces.fsl import Threshold, BinaryMaths, Split
from nipype.interfaces.io import FreeSurferSource, DataSink
from nipype.interfaces.utility import IdentityInterface, Rename

from ..utils import select_file


def mk_w_angio(freesurfer_dir, angiogram, out_dir):

    n_input = Node(IdentityInterface(fields=[
        'fs_dir',
        'fs_subj',
        'angiogram',
        'out_dir',
        ]), name='input')

    n_input.inputs.fs_dir = str(freesurfer_dir.parent)
    n_input.inputs.fs_subj = freesurfer_dir.name
    n_input.inputs.angiogram = str(angiogram)
    n_input.inputs.out_dir = str(out_dir)

    n_coreg = Node(Registration(), name='antsReg')
    n_coreg.inputs.num_threads = 40
    n_coreg.inputs.use_histogram_matching = False
    n_coreg.inputs.dimension = 3
    n_coreg.inputs.winsorize_lower_quantile = 0.001
    n_coreg.inputs.winsorize_upper_quantile = 0.999
    n_coreg.inputs.float = True
    n_coreg.inputs.interpolation = 'Linear'
    n_coreg.inputs.transforms = ['Rigid', ]
    n_coreg.inputs.transform_parameters = [[0.1, ], ]
    n_coreg.inputs.metric = ['MI', ]
    n_coreg.inputs.metric_weight = [1, ]
    n_coreg.inputs.radius_or_number_of_bins = [32, ]
    n_coreg.inputs.sampling_strategy = ['Regular', ]
    n_coreg.inputs.sampling_percentage = [0.5, ]
    n_coreg.inputs.sigma_units = ['mm', ]
    n_coreg.inputs.convergence_threshold = [1e-6, ]
    n_coreg.inputs.smoothing_sigmas = [[1, 0], ]
    n_coreg.inputs.shrink_factors = [[1, 1], ]
    n_coreg.inputs.convergence_window_size = [10, ]
    n_coreg.inputs.number_of_iterations = [[250, 100], ]
    n_coreg.inputs.output_warped_image = True
    n_coreg.inputs.output_inverse_warped_image = True
    n_coreg.inputs.output_transform_prefix = 'angio_to_struct'

    n_apply = Node(ApplyTransforms(), name='ants_apply')
    n_apply.inputs.dimension = 3
    n_apply.inputs.interpolation = 'Linear'
    n_apply.inputs.default_value = 0

    n_convert = Node(MRIConvert(), 'convert')
    n_convert.inputs.out_type = 'niigz'

    n_binarize = Node(Threshold(), 'make_mask')
    n_binarize.inputs.thresh = .1
    n_binarize.inputs.args = '-bin'

    n_mask = Node(BinaryMaths(), 'mask')
    n_mask.inputs.operation = 'mul'

    n_veins = Node(Rename(), 'rename_veins')
    n_veins.inputs.format_string = 'angiogram.nii.gz'

    n_sink = Node(DataSink(), 'sink')
    n_sink.inputs.base_directory = '/Fridge/users/giovanni/projects/intraop/loenen/angiogram'
    n_sink.inputs.remove_dest_dir = True

    fs = Node(FreeSurferSource(), 'freesurfer')

    n_split = Node(Split(), 'split_pca')
    n_split.inputs.dimension = 't'

    w = Workflow('tmp_angiogram')
    w.base_dir = str(out_dir)

    w.connect(n_input, 'fs_dir', fs, 'subjects_dir')
    w.connect(n_input, 'fs_subj', fs, 'subject_id')
    w.connect(n_input, 'angiogram', n_split, 'in_file')
    w.connect(n_split, ('out_files', select_file, 0), n_coreg, 'moving_image')
    w.connect(fs, 'T1', n_coreg, 'fixed_image')

    w.connect(n_coreg, 'forward_transforms', n_apply, 'transforms')
    w.connect(n_split, ('out_files', select_file, 1), n_apply, 'input_image')
    w.connect(fs, 'T1', n_apply, 'reference_image')
    w.connect(fs, 'brain', n_convert, 'in_file')
    w.connect(n_convert, 'out_file', n_binarize, 'in_file')
    w.connect(n_apply, 'output_image', n_mask, 'in_file')
    w.connect(n_binarize, 'out_file', n_mask, 'operand_file')
    w.connect(n_mask, 'out_file', n_veins, 'in_file')
    w.connect(n_input, 'out_dir', n_sink, 'base_directory')
    w.connect(n_veins, 'out_file', n_sink, '@angiogram')
    w.connect(n_convert, 'out_file', n_sink, '@brain')

    return w
