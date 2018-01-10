# .travis
# 'wget -qO- ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz')
# 'tar -C /home/giovanni/tools/bidso/tests/data/derivatives -xf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz freesurfer/subjects/bert')






from pathlib import Path
from shutil import rmtree


# In[3]:


info = {
    'subject': 'bert',
    'session': 'day10',
    'modality': 'bold',
}


ROOT_PATH = Path('/home/giovanni/tools/bidso/tests/bids')

# TODO: participants

rmtree(ROOT_PATH)
ROOT_PATH.mkdir()

subj_path = ROOT_PATH / f'sub-{info["subject"]}'
subj_path.mkdir()

sess_path = subj_path / f'ses-{info["session"]}'
sess_path.mkdir()

modality_path = sess_path / f'{info["modality"]}'
modality_path.mkdir()


# In[7]:


get_ipython().system('ln -s /usr/local/freesurfer/subjects/bert /home/giovanni/tools/bidso/tests/derivatives/freesurfer/sub-bert')


# In[8]:


from nibabel import load
from nibabel import Nifti1Image




mri = load('/home/giovanni/tools/bidso/tests/derivatives/freesurfer/sub-bert/mri/brain.mgz')
x = mri.get_data()


# In[14]:


nifti = Nifti1Image(x, mri.affine)

Path('/home/giovanni/tools/bidso/tests/bids/sub-bert/ses-day10/anat/').mkdir(parents=True)  # TODO
nifti.to_filename(f'/home/giovanni/tools/bidso/tests/bids/sub-bert/ses-day10/anat/sub-{info["subject"]}_T1w.nii.gz')


# In[15]:


from bidso.utils import add_underscore, replace_underscore, replace_extension


# In[16]:


from numpy import array, stack, diag, ones, zeros, r_, NaN
from json import dump



# In[17]:


fmri_file = modality_path / f'sub-{info["subject"]}_ses-{info["session"]}_task-block_run-00'

_create_bold(mri, add_underscore(fmri_file, 'bold.nii.gz'))
_create_events(add_underscore(fmri_file, 'events.tsv'))


# In[19]:


from boavus.utils import ENVIRON
from tempfile import mkstemp
from shutil import copyfile
from subprocess import run
from pathlib import Path


def fsl_reorient2std(nii):
    """This function simply reorients nifti, so that FSL can work with it
    more easily (reg works much better after running this function).
    """
    tmp_nii = mkstemp(suffix='.nii.gz')[1]
    cmd = ['fslreorient2std',
           str(nii),
           tmp_nii,
           ]
    run(cmd, env=ENVIRON)
    copyfile(tmp_nii, nii)
    Path(tmp_nii).unlink()


fsl_reorient2std('/home/giovanni/tools/bidso/tests/bids/sub-bert/ses-day10/bold/sub-bert_ses-day10_task-block_run-00_bold.nii.gz')


# In[20]:


from boavus.fsl.feat import *
from boavus.fsl.feat import _write_events


# In[22]:


from bidso import Task, file_Core
task = Task('/home/giovanni/tools/bidso/tests/bids/sub-bert/ses-day10/bold/sub-bert_ses-day10_task-block_run-00_bold.nii.gz')


# In[23]:


FEAT_OUTPUT = Path('/home/giovanni/tools/bidso/tests/derivatives/feat')


# In[24]:


from boavus.fsl.feat import run_feat

run_feat(FEAT_OUTPUT, task)


# In[26]:





# In[137]:


get_ipython().system('freeview -v /home/giovanni/tools/bidso/tests/data/derivatives/freesurfer/subjects/bert/mri/brain.mgz /home/giovanni/tools/bidso/tests/data/derivatives/xm.nii.gz:opacity=.5')

