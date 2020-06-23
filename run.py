import flywheel
import os
import zipfile
import shutil
import json

# This run.py is just a simulation of the real situation, therefore inputs and outputs are abbreviated.
# However, since this script only use Yichao Deng's permission to accessing flywheel,
# projects may not be avaliable in some cases.

user_id = 'stanfordlabs.flywheel.io:dddk2FvdSYhElu6BFK'
fw = flywheel.Client(user_id)
self = fw.get_current_user()

def listall(root, path):
    if not os.path.isdir(os.path.join(path,root)):
        return [os.path.join(path,root)]
    items = os.listdir(os.path.join(path,root))
    all = []
    for item in items:
        all.extend(listall(item, os.path.join(path,root)))
    return all

acquisition = fw.lookup('wandell/Graphics test/image alignment/city3_14:17_v10.0_f74.04left_o270.00_201962618446/pos_5000_5000_5000')
try:
    os.mkdir('temporary')
    i = 0
    for file in acquisition.files:
        print(file['name'])
        str = file['name']
        # The line below is necessary only if you are running on Windows.
        # However, I suggest not deleting it this time.
        new = str.replace(':', '_')
        acquisition.download_file(r'%s' % str, r'temporary/%s' % new)
        i += 1
    os.chdir('temporary/')
    fp = open('city3_14_17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000_target.json', 'r', encoding='utf8')
    js = json.load(fp)
    targets = js['fwAPI']['InfoList'].split(' ')
    root = os.getcwd()
    os.mkdir('scene/')
    os.mkdir('scene/PBRT/')
    os.mkdir('scene/PBRT/pbrt-geometry')
    for i in range(len(targets)):
        target = targets[i]
        print(target)
        if not target.endswith('.zip') and not target.endswith('.exr'):
            tmp = fw.get(target)
            file_name = targets[i + 1]
            tmp.download_file(file_name, file_name)
            try:
                if file_name == 'data.zip':
                    print('Is data.zip')
                    zip = zipfile.ZipFile(file_name)
                    zip.extractall(path=os.getcwd())
                    zip.close()
                # I'm not sure whether this part is necessary, since I notice that in 5000.pbrt,
                # .exr will only be used in root dir.
                if file_name.endswith('.exr'):
                    shutil.copy(file_name, 'scene/PBRT/pbrt-geometry')
                else:
                    os.mkdir('%s' % file_name[:-4])
                    zip = zipfile.ZipFile(file_name)
                    zip.extractall(path=file_name[:-4])
                    zip.close()
                    os.chdir(file_name[:-4] + '/scene/PBRT/pbrt-geometry')
                    for i in os.listdir(os.getcwd()):
                        shutil.copy(i, root + '/scene/PBRT/pbrt-geometry')
                    os.chdir(root)
                    os.mkdir('%s' % file_name[:-4])
                    zip = zipfile.ZipFile(file_name)
                    zip.extractall(path=file_name[:-4])
                    zip.close()
                    # As for textures, I just put them in a dir called textures under root.
                    os.chdir(file_name[:-4] + '/textures')
                    for i in os.listdir(os.getcwd()):
                        shutil.copy(i, root + '/textures')
            finally:
                os.chdir(root)
                if file_name == 'data.zip': os.remove('data.zip')
                elif os.path.exists('%s' % file_name[:-4]):
                    os.remove(file_name)
                    shutil.rmtree('%s' % file_name[:-4])
    root = 'temporary'
    os.chdir(root)
    os.mkdir('result')
    os.mkdir('result/renderings')
    output_file = 'result/renderings/city3_14_17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000.dat'
    curr_file = os.path.abspath('city3_14_17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000.pbrt')
    render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
    os.system(render_command)
finally:
    os.chdir('/flywheel/v0/')
    if os.path.exists('temporary'):
        print('If there is an exception raised, try again.')
        # shutil.rmtree('temporary') # this line is used to reserve the resulting .dat file.
