import flywheel
import os
import zipfile
import shutil

# 0. handling user input
context = flywheel.GearContext()  # Get the gear context
config = context.config           # from the gear context, get the config settings

# 1. Login Flywheel by user_id
fw = context.client
self = fw.get_current_user()
target_id = context.destination['id']
print('The user now is :', self)
print('destination is :', context.destination)

# Try getting the target container by destination['id']
try:
    target = fw.get(target_id)
    target_name = target['label']
except Exception as e:
    print('Oops! Something wrong happens when looking up the target acquisition!')
    print(e)
    raise
finally:
    print('You may just try it again.')


# 2. Using the function below, we can get a list of all files in the zip file.
# This function is used to list all files recursively.
# it'll return a list that contains all files under a specific directory(unlike os.listdir())
def listall(root, path):
    if not os.path.isdir(os.path.join(path,root)):
        return [os.path.join(path,root)]
    items = os.listdir(os.path.join(path,root))
    all = []
    for item in items:
        all.extend(listall(item, os.path.join(path,root)))
    return all

# 3. Main part.
try:
    # Creating folder 'result/renderings' to put the result.
    if os.path.exists('result'):
        print('Warning: Folder "result" already exists. Deleting it now...')
        shutil.rmtree('result')
    os.mkdir("result")
    os.mkdir("result/renderings")
    output_dir = os.path.abspath("result")

    # Downloading the target zipfile and unzip it into temp.
    if os.path.exists('temp'):
        print('Warning: Folder "temp" already exists. Deleting it now...')
        shutil.rmtree('temp')
    os.mkdir('temp')
    target.download_file('%s.zip' % target_name, '%s.zip' % target_name)
    zip = zipfile.ZipFile('%s.zip' % target_name)
    zip.extractall(path='temp/')
    zip.close()
    # since os.path.abspath() will only append the current work dir with the file/folder passed,
    # we need to change the work dir to temp.
    # flywheel/v0/... => flywheel/v0/temp/...
    os.chdir("temp")

    # find the pbrt file and starting pbrt.
    for curr in os.listdir(os.getcwd()):
        if not os.path.isdir(os.path.abspath(curr)) and curr == '%s.pbrt' % target_name:
            root = os.path.abspath(curr)
            basename = os.path.split(root)[1]
            currName = basename
            output_file = os.path.join(output_dir, "renderings", currName[:-5] + ".dat")
            curr_file = root
            render_command = '/pbrt/pbrt-v3-spectral/build/pbrt --outfile %s %s' % (output_file, curr_file)
            cmd = render_command
            print(cmd)
            print(os.system(cmd)) # print() is not necessary, just to make debugging more convenient.

    # Since result is under flywheel/v0/, we need to alter our working directory back.
    os.chdir("/flywheel/v0/")
    upload_files = listall("result",'')

    # 4. Uploading files.
    print('Putting files into output...')
    for f in upload_files:
        print('\t%s...' % (f))
        target.upload_file(f)     # this line originally committed fot uploading result directly.
        shutil.copy(f, context.output_dir)
        os.remove(f)
    print('Done!')

# 5. We need to delete temp and result for future use. A "try...finally..." will always ensure it.
finally:
    if os.path.exists('temp'): shutil.rmtree('temp')
    if os.path.exists('%s.zip' % target_name):  os.remove('%s.zip' % target_name)
    if os.path.exists('result'): shutil.rmtree('result/')
