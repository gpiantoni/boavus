function snap_to_surface(surf_file, elec_file)
%SNAP_TO_SURFACE snap electrodes to pial surface
%
% surf_file : path to file ?h.pial_outer_smooth
% elec_file : path to csv file with electrodes (label, x, y, z)
%
% it writes a file with _snapped at the end of the name.

[path, name, ext] = fileparts(elec_file);
snapped_elec_file = [path filesep name '_snapped' ext];

surf = read_surf(surf_file);
elec = read_sens(elec_file);

elec.pos(elec.pos == 0) = 0.01;  % values shouldn't be zero, otherwise optimization complains

elec.pos = optimization_snap(elec.pos, surf);

write_sens(snapped_elec_file, elec);

end

function sens = read_sens(filename)

fid = fopen(filename);
tmp = textscan(fid, '%s%f%f%f', 'Delimiter', ',');
fclose(fid);
sens.label = tmp{1};
sens.pos = [tmp{2:4}];

end

function write_sens(filename, sens)
fid = fopen(filename, 'w');
for i = 1:numel(sens.label)
  fprintf(fid, '%s, %.3f, %.3f, %.3f\n', sens.label{i}, sens.pos(i, :));
end
fclose(fid);

end

function surf = read_surf(fname)
%
% surf = read_surf(fname)
% reads a the vertex coordinates and face lists from a surface file
% note that reading the faces from a quad file can take a very long
% time due to the goofy format that they are stored in. If the faces
% output variable is not specified, they will not be read so it
% should execute pretty quickly.
%

TRIANGLE_FILE_MAGIC_NUMBER =  16777214;
QUAD_FILE_MAGIC_NUMBER =  16777215;

fid = fopen(fname, 'rb', 'b');
if (fid < 0)
  error('could not open curvature file %s.', fname);
end

magic = fread3(fid);

if(magic == QUAD_FILE_MAGIC_NUMBER)
  vnum = fread3(fid);
  fnum = fread3(fid);
  vertex_coords = fread(fid, vnum*3, 'int16') ./ 100;
  faces = nan(fnum, 4);
  for i=1:fnum
    for n=1:4
      faces(i,n) = fread3(fid);
    end
  end
elseif (magic == TRIANGLE_FILE_MAGIC_NUMBER)
  fgets(fid);
  fgets(fid);
  vnum = fread(fid, 1, 'int32');
  fnum = fread(fid, 1, 'int32');
  vertex_coords = fread(fid, vnum*3, 'float32');
  faces = fread(fid, fnum*3, 'int32');
  faces = reshape(faces, 3, fnum)';
end

vertex_coords = reshape(vertex_coords, 3, vnum)';
fclose(fid);

surf = [];
surf.vert = vertex_coords;
surf.faces = faces + 1;

end

function [retval] = fread3(fid)
% [retval] = fread3(fid)
% read a 3 byte integer out of a file

b1 = fread(fid, 1, 'uchar');
b2 = fread(fid, 1, 'uchar');
b3 = fread(fid, 1, 'uchar');
retval = bitshift(b1, 16) + bitshift(b2,8) + b3;

end
