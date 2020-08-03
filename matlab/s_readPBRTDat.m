%%

wave = 400:10:700;
nWave = length(wave);
filename = fullfile(piRootPath, 'local', 'readPBRTDat',...
    'city3_11:16_v12.0_f47.50front_o270.00_2019626181423_pos_163_000_000.dat');
energy = piReadDAT(filename);
photon = Energy2Quanta(wave,energy);
scene = piSceneCreate(photon, 'wavelength', wave);
sceneWindow(scene);

%% 
wave = 400:10:700;
nWave = length(wave);
filename = fullfile(piRootPath, 'local', 'readPBRTDat',...
    'city3_11:16_v12.0_f47.50front_o270.00_2019626181423_pos_163_000_000_depth.dat');
depth = piReadDAT(filename);
depth = depth(:,:,1);
ieNewGraphWin; imagesc(depth);

%% 
wave = 400:10:700;
nWave = length(wave);
filename = fullfile(piRootPath, 'local', 'readPBRTDat',...
    'city3_11:16_v12.0_f47.50front_o270.00_2019626181423_pos_163_000_000_mesh.dat');
mesh = piReadDAT(filename);
mesh = mesh(:,:,1);
ieNewGraphWin; imagesc(mesh);
%{
oi = oiCreate;
oi = oiCompute(oi, scene);
oiWindow(oi);
sensor = sensorCreate;
sensor = sensorSet(sensor, 'size', [800, 800]);
sensor = sensorCompute(sensor, oi);
sensorWindow(sensor)
ip = ipCreate;
ip = ipCompute(ip, sensor);
ipWindow(ip)
%}