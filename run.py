import flywheel
import os
import zipfile
import shutil
import json

# This run.py is just a simulation of the real situation, therefore inputs and outputs are abbreviated.
# For a gear, it should be /flywheel/v0/
ori = os.getcwd()

# This 'root' will be our main working directory.
root = 'temporary'

try:
    # Using user api-key to get access to flywheel. One may change the api-key to get a higher authentication.
    user_api = 'dddk2FvdSYhElu6BFK'
    user_id = 'stanfordlabs.flywheel.io:' + user_api
    fw = flywheel.Client(user_id)
    self = fw.get_current_user()

    # Making a temporary folder, which will be the main folder to work with, to put all of the files in a scene.
    # Before making the directory, check if it exists.
    if os.path.exists(root):
        print("Warning: Folder 'temporary' already exist. Automatically deleting it now...")
        shutil.rmtree(root)
    os.mkdir(root)
    os.chdir(root)
    root = os.path.abspath(os.getcwd())

    # Using fw sdk to get city3 acquisition, and then downloading its files.
    acquisition = fw.lookup('wandell/Graphics test/image alignment/city3_14:17_v10.0_f74.04left_o270.00_201962618446/pos_5000_5000_5000')
    for file in acquisition.files:
        print(file['name'])
        str = file['name']
        # Since windows don't support ':' in files' name, replace them with '_'
        new = str.replace(':', '_')
        acquisition.download_file(r'%s' % str, r'%s' % new)

    # Due to the limitation of Windows mentioned above, all of the ':' in file name originally are replaced by '_".
    # In addition, code are modified correspond to then alternation of file name manually(not showing there).

    # Using built-in function to handle json file, getting the target line.
    pbrt_file = 'city3_14_17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000_target.json'
    fp = open(pbrt_file, 'r', encoding='utf8')
    js = json.load(fp)

    # By split(), we can get all of the container(acquisition) id and target files' name.
    targets = js['fwAPI']['InfoList'].split(' ')

    # Making new folder to save pbrt geometry and textures for future use.
    # Before making the directory, check if it exists.
    if os.path.exists('scene/'):
        print("Warning: Folder 'scene' already exists. Automatically deleting it now...")
        shutil.rmtree('scene/')
    os.mkdir('scene/')
    os.mkdir('scene/PBRT/')
    os.mkdir('scene/PBRT/pbrt-geometry')

    if os.path.exists('textures/'):
        print("Warning: Folder 'textures/' already exists. Automatically deleting it now...")
        shutil.rmtree('textures/')
    os.mkdir('textures/')

    # Using for loop to iterate targets, then download every target files by fw sdk.
    for i in range(len(targets)):
        target = targets[i]
        print(target) # For debugging.

        # If a target is neither endswith zip nor endswith exr, then it should be a container id to look up.
        if not target.endswith('.zip') and not target.endswith('.exr'):

            # 'tmp' is the container to be looked up.
            # 'file_name' is the target file to download, which can be get from target[i+1].
            tmp = fw.get(target)
            file_name = targets[i + 1]
            tmp.download_file(file_name, file_name)

            try:

                # There are three situations:
                # 1. target is data.zip
                # 2. target is .exr file
                # 3. other geometry zip files

                # If target is data.zip, we just need to unzip it to the main working directory.
                if file_name == 'data.zip':
                    print('Is data.zip')
                    zip = zipfile.ZipFile(file_name)
                    zip.extractall(path=os.getcwd())
                    zip.close()

                # If target is .exr file.
                # I'm not sure whether this part is necessary, since I notice that in 5000.pbrt,
                # .exr will only be used in root dir.
                elif file_name.endswith('.exr'):
                    shutil.copy(file_name, 'scene/PBRT/pbrt-geometry')

                # If target is a geometry zip file, we need to unzip it and put its geometry and textures separately.
                else:
                    # Building a folder to place all of the files in target zip file.
                    os.mkdir('%s' % file_name[:-4])
                    # Unzipping target file.
                    zip = zipfile.ZipFile(file_name)
                    zip.extractall(path=file_name[:-4])
                    zip.close()

                    # Copying all geometry pbrt to scene/PBRT/pbrt-geometry
                    os.chdir(file_name[:-4] + '/scene/PBRT/pbrt-geometry')
                    for i in os.listdir(os.getcwd()):
                        shutil.copy(i, root + '/scene/PBRT/pbrt-geometry')
                    os.chdir(root)

                    # Copying all textures to textures/
                    os.chdir(file_name[:-4] + '/textures')
                    for i in os.listdir(os.getcwd()):
                        shutil.copy(i, root + '/textures')
                    os.chdir(root)

            finally:
                # deleting all zip files downloaded and temporary folders used for place files.
                if file_name == 'data.zip': os.remove(file_name)
                elif os.path.exists('%s' % file_name[:-4]):
                    os.remove(file_name)
                    shutil.rmtree('%s' % file_name[:-4])

    # Building result/renderings for PBRT rendering.
    # Before making the directory, check if it exists.
    os.chdir(root)
    if os.path.exists('result'):
        print("Warning: Folder 'result' already exists. Automatically deleting it now...")
        shutil.rmtree('result')
    os.mkdir('result')
    os.mkdir('result/renderings')

    # Generating PBRT command and run it by os.system().
    file = 'city3_14_17_v10.0_f74.04left_o270.00_201962618446_pos_5000_5000_5000'
    output_file = 'result/renderings/%s.dat' % file
    curr_file = os.path.abspath('%s.pbrt' % file)
    render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
    os.system(render_command)

# Printing out the exception.
except Exception as  e:
    print('oops! Something went wrong there.')
    raise e

finally:
    # Checking whether root exist, if true then deleting it for future use.
    # Mention here that if we delete root, all other directory we made('result', 'scene'...) will be deleted as well.
    os.chdir(ori)
    if os.path.exists(root):
        print('If there is an exception raised, you may just fixed it and try again.')
        shutil.rmtree(root)
