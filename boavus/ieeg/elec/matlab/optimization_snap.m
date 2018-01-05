function coord_snapped = optimization_snap(coord, surf)

% get starting coordinates
coord0 = coord;

% compute pairs of neighbors
pairs = knn_pairs(coord, 4);

% anonymous function handles
efun = @(coord_snapped) energy_electrodesnap(coord_snapped, coord, pairs);
cfun = @(coord_snapped) dist_to_surface(coord_snapped, surf);

% options
options = optimset('Algorithm','active-set',...
  'Display', 'iter',...
  'MaxIter', 50,...
  'MaxFunEvals', Inf,...
  'UseParallel', 'always',...
  'GradObj', 'off',...
  'TypicalX', coord(:),...
  'DiffMaxChange', 2,...
  'DiffMinChange', 0.3,...
  'TolFun', 0.3,...
  'TolCon', 0.01 * size(coord0, 1),...
  'TolX', 0.5,...
  'Diagnostics', 'off',...
  'RelLineSrchBnd',1);

% run minimization
coord_snapped = fmincon(efun, coord0, [], [], [], [], [], [], cfun, options);

end

function [energy, denergy]=energy_electrodesnap(coord, coord_orig, pairs)

energy_eshift = sum((coord - coord_orig).^2, 2);

energy_deform = deformation_energy(coord, coord_orig, pairs);

energy = mean(energy_eshift) + mean(energy_deform.^2);

denergy=[];

end

function energy = deformation_energy(coord, coord_orig, pairs)

dist = sqrt(sum((coord(pairs(:, 1), :) - coord(pairs(:, 2), :)) .^ 2, 2));
dist_orig = sqrt(sum((coord_orig(pairs(:, 1), :) - coord_orig(pairs(:, 2), :)) .^ 2, 2));

energy = (dist - dist_orig) .^2;
end

function [c, dist] = dist_to_surface(coord, surf)
% Compute distance to surface, this is the fastest way to run it, although
% running the loops in other directions might be more intuitive.

c = [];

dist = zeros(size(coord, 1), 1);
for i0 = 1:size(coord, 1)
  dist_one_elec = zeros(size(surf.vert, 1), 1);
  for i1 = 1:size(surf.vert, 2)
    dist_one_elec = dist_one_elec + (surf.vert(:, i1) - coord(i0, i1)) .^ 2;
  end
  dist(i0) = min(dist_one_elec);
end
dist = sqrt(dist);

end

function pairs=knn_pairs(coord, k)

knn_ind = knnsearch(coord, coord, k);
pairs = cat(3, knn_ind, repmat([1:size(coord,1)]',1,k));
pairs = permute(pairs,[3 1 2]);
pairs = sort(reshape(pairs,2,[]),1)';
pairs = unique(pairs,'rows');

end

function idx = knnsearch(Q, R, K)

[N, M] = size(Q);
L = size(R, 1);
idx = zeros(N, K);
D = idx;

for k = 1:N
  d = zeros(L, 1);
  for t = 1:M
    d = d + (R(:, t) - Q(k, t)) .^ 2;
  end
  
  d(k) = inf;
  
  [s, t] = sort(d);
  idx(k, :) = t(1:K);
  D(k, :)= s(1:K);
end

end