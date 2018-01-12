



# In[15]:


from bidso.utils import add_underscore, replace_underscore, replace_extension


# In[16]:


from numpy import array, stack, diag, ones, zeros, r_, NaN
from json import dump



# In[17]:




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

