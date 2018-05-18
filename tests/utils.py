from hashlib import md5
import gzip


def compute_md5(p):
    """Compute m5sum for a file. If the file is .gz (in the case of .nii.gz)
    then it reads the archived version (the .gz contains metadata that changes
    every time)
    """
    md5_ = md5()

    if p.suffix == '.gz':
        f = gzip.open(p, 'rb')
    else:
        f = p.open('rb')

    md5_.update(f.read())
    f.close()

    return md5_.hexdigest()
