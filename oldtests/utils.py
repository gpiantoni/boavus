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
        val = f.read()

    elif p.suffix == '.vhdr':
        # skip first two lines because it contains the time the file was written
        f = f.open('rb')
        val = b'\n'.join(f.read().split(b'\n')[2:])

    else:
        f = p.open('rb')
        val = f.read()

    md5_.update(val)
    f.close()

    return md5_.hexdigest()
