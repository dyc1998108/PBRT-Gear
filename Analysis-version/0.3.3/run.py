import flywheel
import os
import zipfile
import shutil
import json
import sys

# For a gear, it should be /flywheel/v0/
ori = os.getcwd()

# This 'root' will be our main working directory.
root = 'temporary'

try:

    # handling user input
    context = flywheel.GearContext()
    config = context.config
    scene_type = config['scene_type']
    keyword = config['keyword']
    pbrt_select = config['pbrt_select']

    # Examine the correctness of config first.
    assert scene_type in ['complicate', 'simple', 'No specific type'], 'Wrong scene_type config with ' + scene_type
    pbrt_type = pbrt_select.split(',')
    for i in pbrt_type:
        assert i in ['radiance', 'depth', 'mesh', 'No specific pbrt'], 'Wrong pbrt_select config with ' + i

    # Login Flywheel by user_id
    fw = context.client
    self = fw.get_current_user()

    # Try getting the target container by destination['id']. Since analysis type only receive analysis object as
    # destination, using ['parent'] to find the target session.
    analysis_id = context.destination['id']
    analysis = fw.get_analysis(analysis_id)
    container_type = analysis['parent']['type']
    container_id = analysis['parent']['id']
    target_id = container_id
    # If the parent is not a session, then raise a exception.
    assert container_type == 'session', 'Gear not running in session.'
    print('The user now is :', self)
    target = fw.get_session(target_id)
    target_name = target['label']
    print('Gear running in session:', target_name)

except Exception as e:
    print('Oops! Something wrong happens when looking up the target acquisition!')
    print(e)
    print('You may just check it out and try again.')
    raise

try:
    # Making a temporary folder, which will be the main folder to work with, to put all of the files in a scene.
    # Before making the directory, check if it exists.
    if os.path.exists(root):
        print("Warning: Folder 'temporary' already exist. Automatically deleting it now...")
        shutil.rmtree(root)
    os.mkdir(root)
    os.chdir(root)
    root = os.path.abspath(os.getcwd())

    # Using fw sdk to get those target acquisitions, and then downloading their files.
    # For analysis gear, it'll always receive session object, therefore iterating its acquisition without check.
    acquisitions = target.acquisitions()
    for acquisition in acquisitions:
        # In case the acquisition doesn't have any file in it.
        if acquisition.files:

            # Changing this line if the situation is different.
            # These two files is used for judging acquisition type.
            target_file = '%s_target.json' % acquisition['label']
            zip_file = '%s.zip' % acquisition['label']

            # If scene_type is 'complicate', then skip those 'simple' ones; similar with the 'simple' scene_type.
            if scene_type == 'complicate':
                flag = False
                for file in acquisition.files:
                    if file['name'] == target_file:
                        flag = True
                if not flag:
                    print('acquisition ' + acquisition['label'] + ' not complicate')
                    continue
            elif scene_type == 'simple':
                flag = False
                for file in acquisition.files:
                    if file['name'] == zip_file:
                        flag = True
                if not flag:
                    print('acquisition ' + acquisition['label'] + ' not simple')
                    continue

            # Or skip those acquisition whose names are not corresponding to the keyword.
            if keyword != 'No keyword':
                if acquisition['label'].find(keyword) == -1:
                    print('Acquisition ' + acquisition['label'] + ' do not corresponds with keyword.')
                    continue

            # After filtering, start handling with current acquisition.
            # To begin with, downloading files in the acquisition.
            print('Finish filtering.')
            for file in acquisition.files:
                print(file['name'])
                str = file['name']
                acquisition.download_file(r'%s' % str, r'%s' % str)

            # Checking if the scene is a simple scene that have no target json file.
            if os.path.exists(target_file):
                # Using built-in function to handle json file, getting the target line.
                fp = open(target_file, 'r', encoding='utf8')
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
                    print(target)  # For debugging.

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

                                # Copying all textures to textures/. Some targets even don't  have textures.
                                texture_dir = file_name[:-4] + '/textures'
                                if os.path.exists(texture_dir):
                                    os.chdir(texture_dir)
                                    for i in os.listdir(os.getcwd()):
                                        shutil.copy(i, root + '/textures')
                                    os.chdir(root)

                        finally:
                            # deleting all zip files downloaded and temporary folders used for place files.
                            if file_name == 'data.zip':
                                os.remove(file_name)
                            elif os.path.exists('%s' % file_name[:-4]):
                                os.remove(file_name)
                                shutil.rmtree('%s' % file_name[:-4])

            # To handle on simple scene, just extract the zip file for later PBRT rendering.
            else:
                # Maybe sometime a problematic acquisition is passed, so add this line to confirm.
                assert os.path.exists(zip_file), 'Not a simple scene with zip file or a complicated one with json file.'
                if os.path.exists(zip_file):
                    zip = zipfile.ZipFile(zip_file)
                    zip.extractall(path=os.getcwd())
                    zip.close()

            # Building result/renderings for PBRT rendering.
            # Before making the directory, check if it exists.
            os.chdir(root)
            if os.path.exists('result'):
                print("Warning: Folder 'result' already exists. Automatically deleting it now...")
                shutil.rmtree('result')
            os.mkdir('result')
            os.mkdir('result/renderings')

            # Changing this line if the situation is different.
            # It should always corresponding to the name of the file that running pbrt rendering at.
            # To run specific pbrt, using pbrt_type to filter.
            pbrt = '%s' % acquisition['label']
            files = []
            for i in ['mesh', 'depth']:
                if i in pbrt_type:
                    files.append(pbrt + '_' + i)
            if 'radiance' in pbrt_type:
                files.append(pbrt)
            elif 'No specific pbrt' in pbrt_type:
                files.append(pbrt)
                files.append(pbrt + '_mesh')
                files.append(pbrt + '_depth')

            for file in files:
                if os.path.exists('%s.pbrt' % file):
                    # Generating PBRT command and run it by os.system().
                    output_file = 'result/renderings/%s.dat' % file
                    curr_file = os.path.abspath('%s.pbrt' % file)
                    render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
                    os.system(render_command)

            # Using shutil to make a archive, then copying it to output dir.
            result = shutil.make_archive(pbrt, 'zip', 'result/renderings')
            shutil.copy('%s.zip' % pbrt, context.output_dir)

# Printing out the exception.
except Exception as  e:
    s = sys.exc_info()
    print("oops! There is an error '%s' in line %s" %(s[1], s[2].tb_lineno))
    raise e

finally:
    # Checking whether root exist, if true then deleting it for future use.
    # Mention here that if we delete root, all other directory we made('result', 'scene'...) will be deleted as well.
    os.chdir(ori)
    if os.path.exists(root):
        print('If there is an exception raised, you may just fixed it and try again.')
        shutil.rmtree(root)