from ..workflow.struct.angio import mk_w_angio


def main(freesurfer_dir, angiogram, output_dir):
    """
    realign angiogram

    Parameters
    ----------
    freesurfer_dir : path

    angiogram : path

    output_dir : path

    """
    w = mk_w_angio(freesurfer_dir, angiogram, output_dir)

    w.write_graph()
    w.run(plugin='MultiProc')
