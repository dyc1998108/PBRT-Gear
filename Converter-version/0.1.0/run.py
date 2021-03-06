import flywheel
import os
import zipfile
import shutil
import json
import sys

# CAUTION: There are two places(line 59 and 158) you'll probably need to modify, according to your situation.

# For a gear, it should be /flywheel/v0/
ori = os.getcwd()

# This 'root' will be our main working directory.
root = 'temporary'

try:

    # handling user input
    context = flywheel.GearContext()
    config = context.config

    # Login Flywheel by user_id
    fw = context.client
    self = fw.get_current_user()

    # Try getting the target container by destination['id']
    target_id = context.destination['id']
    print('The user now is :', self)
    print('destination is :', context.destination)
    target = fw.get(target_id)
    target_name = target['label']
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
    # Considering that when running a batch for converter gear, a session object will be passed, therefore iterating it.
    acquisitions = []
    if context.destination['type'] == 'session':
        acquisitions = [acquisition for acquisition in target.acquisitions()]
    elif context.destination['type'] == 'acquisition':
        acquisitions.append(target)
    for acquisition in acquisitions:
        # In case the acquisition has no file in it.
        if acquisition.files:
            for file in acquisition.files:
                print(file['name'])
                str = file['name']
                acquisition.download_file(r'%s' % str, r'%s' % str)

            # Changing this line if the situation is different.
            # It should always corresponding to the name of the file where target line located.
            pbrt_file = '%s_target.json' % acquisition['label']

            # Using built-in function to handle json file, getting the target line.
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
            file = '%s' % acquisition['label']

            # Generating PBRT command and run it by os.system().
            output_file = 'result/renderings/%s.dat' % file
            curr_file = os.path.abspath('%s.pbrt' % file)
            render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
            os.system(render_command)

            # Move the result to output directory.
            shutil.copy(output_file, context.output_dir)

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