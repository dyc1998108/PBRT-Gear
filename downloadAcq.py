'''
downloadAcq.py

Used for testing downloading and reconstructing large complicated traffic scenes stored
on FW.
'''


# Import necessary packages
import flywheel
import os
import zipfile
import shutil
import json

# This run.py is just a simulation of the real situation, therefore inputs and outputs are abbreviated.
# However, since this script only use Yichao Deng's permission to accessing flywheel,
# projects may not be avaliable in some cases.

# Specify user id. Users need to look up their own API keys from personal profile
api_key = 'R8A5uq2z1xyOmpB69j'
user_id = 'stanfordlabs.flywheel.io:' + api_key

# Initialize fw client
fw = flywheel.Client(user_id)

# Look up a certain acquisition
this_acq_name = 'wandell/Graphics test/image alignment/city3_14:17_v10.0_f74.04left_o270.00_201962618446/pos_5000_5000_5000'
acquisition = fw.lookup(this_acq_name)

try:
    # # This is the destination directory when running with Gear
    # dest_dir = 'temporary/'

    # Use another folder for local test now
    cur_path = os.getcwd()
    # This is the folder for downloads
    dest_dir = cur_path + '/' + 'local' + '/' + 'city3'

    # Create folder if not exist
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    # for file in acquisition.files:
    #     print(file['name'])
    #     str = file['name']
    #     # # The line below is necessary only if you are running on Windows.
    #     # # However, I suggest not deleting it this time.
    #     # new = str.replace(':', '_')
    #     acquisition.download_file(r'%s' % str, r'%s/%s' % (dest_dir, str))

    # Change to destination directory
    os.chdir(dest_dir)

    # Specify the target json file that contains the instance id list
    this_json_name = 'city3_14:17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000_target.json'
    fp = open(this_json_name, 'r', encoding='utf8')
    js = json.load(fp)

    # Parse the id list
    # Target has id-filename pairs
    targets = js['fwAPI']['InfoList'].split(' ')

    # Already switch to destination folder
    root = os.getcwd()

    # Create folders
    os.mkdir('scene/')
    os.mkdir('scene/PBRT/')
    os.mkdir('scene/PBRT/pbrt-geometry')
    os.mkdir('textures/')

    # Loop through target elements
    for i in range(len(targets)):

        target = targets[i]
        print(target)

        # If current target is a file id, download.
        if not target.endswith('.zip') and not target.endswith('.exr'):
            tmp = fw.get(target)

            # Get the file name
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
                elif file_name.endswith('.exr'):
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

finally:
    os.mkdir('result')
    os.mkdir('result/renderings')
    # output_file = 'result/renderings/city3_14:17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000.dat'
    # curr_file = os.path.abspath('city3_14:17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000.pbrt')
    # render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
    # os.system(render_command)
    print('Done')

