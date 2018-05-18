import numpy as np
import nibabel as nib
from scipy.spatial.distance import cdist


def snap_elec_to_surf(e_init, surf_smooth):
    dura = nib.freesurfer.read_geometry(str(surf_smooth))[0]

    max_steps = 4000
    temperature_exponent = 1
    deformation_constant = 1.
    giveup_steps = 10000
    init_temp = 1e-3

    n = e_init.shape[0]
    alpha = np.zeros((n, n))
    init_dist = cdist(e_init, e_init)

    neighbors = []

    for i in range(n):
        neighbor_vec = init_dist[:, i]
        # take 5 highest neighbors
        i_neigh = np.min((5, len(neighbor_vec) - 1))
        h5, = np.where(np.logical_and(neighbor_vec < np.sort(neighbor_vec)[i_neigh],
                                      neighbor_vec != 0))

        neighbors.append(h5)

    neighbors = np.squeeze(neighbors)

    # get distances from each neighbor pairing
    neighbor_dists = []
    for i in range(n):
        neighbor_dists.append(init_dist[i, neighbors[i]])

    neighbor_dists = np.hstack(neighbor_dists)

    max = np.max(np.around(neighbor_dists))
    min = np.min(np.around(neighbor_dists))

    hist, _ = np.histogram(neighbor_dists, bins=int((max - min) / 2), range=(min, max))

    fundist = np.argmax(hist) * 2 + min + 1

    # apply fundist to alpha matrix
    alpha_tweak = 1.75

    for i in range(n):
        neighbor_vec = init_dist[:, i]
        neighbor_vec[i] = np.inf

        neighbors = np.where(neighbor_vec < fundist * alpha_tweak)

        if len(neighbors) > i_neigh:
            neighbors = np.where(neighbor_vec < np.sort(neighbor_vec)[i_neigh])

        if len(neighbors) == 0:
            closest = np.argmin(neighbors)
            neighbors = np.where(neighbor_vec < closest * alpha_tweak)

        alpha[i,neighbors]=1

        for j in range(i):
            if alpha[j,i]==1:
                alpha[i,j]=1
            if alpha[i,j]==1:
                alpha[j,i]=1

    # alpha is set, now do the annealing
    def energycost(e_new, e_old, alpha):
        n = len(alpha)

        dist_new = cdist(e_new, e_new)
        dist_old = cdist(e_old, e_old)

        H=0

        for i in range(n):
            H += deformation_constant*float(cdist( [e_new[i]], [e_old[i]] ))

            for j in range(i):
                H += alpha[i,j] * (dist_new[i,j] - dist_old[i,j])**2

        return H

    max_deformation = 3
    deformation_choice = 50

    # adjust annealing parameters
    # H determines maximal number of steps
    H = max_steps
    # Texp determines the steepness of temperateure gradient
    Texp = 1 - temperature_exponent / H
    # T0 sets the initial temperature and scales the energy term
    T0 = init_temp
    # Hbrk sets a break point for the annealing
    Hbrk = giveup_steps

    h = 0
    hcnt = 0
    lowcost = mincost = 1e6

    # start e-init as greedy snap to surface
    e_snapgreedy = dura[np.argmin(cdist(dura, e_init), axis=0)]

    e = np.array(e_snapgreedy).copy()
    emin = np.array(e_snapgreedy).copy()

    # TODO: there is a random element, and it seems to affect the results
    # we set a seed, otherwise the tests are not reproducible
    np.random.seed(0)

    # the annealing schedule continues until the maximum number of moves
    while h < H:
        h += 1
        hcnt += 1
        # terminate if no moves have been made for a long time
        if hcnt > Hbrk:
            break

        # current temperature
        T = T0 * (Texp**h)

        # select a random electrode
        e1 = np.random.randint(n)
        # transpose it with a *nearby* point on the surface

        # find distances from this point to all points on the surface
        dists = np.squeeze(cdist(dura, [e[e1]]))
        # take a distance within the minimum 5X

        # mindist = np.min(dists)
        mindist = np.sort(dists)[deformation_choice]
        candidate_verts, = np.where(dists < mindist * max_deformation)
        choice_vert = candidate_verts[np.random.randint(len(candidate_verts))]

        e_tmp = e.copy()
        e_tmp[e1] = dura[choice_vert]

        cost = energycost(e_tmp, e_init, alpha)

        if cost < lowcost or np.random.random() < np.exp(-(cost - lowcost) / T):
            e = e_tmp
            lowcost = cost

            if cost < mincost:
                emin = e
                mincost = cost
                hcnt = 0

            if mincost == 0:
                break

    return emin
