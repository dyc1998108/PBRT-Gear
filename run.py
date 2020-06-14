import flywheel
import os
import zipfile
import shutil

# 0. handling user input
context = flywheel.GearContext()  # Get the gear context
config = context.config           # from the gear context, get the config settings
user_id = 'stanfordlabs.flywheel.io:' + config['user_id']
file = open(context.get_input_path('files'), mode = 'r')

# 1. Login Flywheel by user_id
fw = flywheel.Client(user_id)
self = fw.get_current_user()

# 2. handling the .txt file input.
class FW:
    def __init__(self, type, name, path):
        self.type = type
        self.name = name
        self.path = path


line = file.readline()
nodes = []
nodes.append(FW(0, line[:-1], line[:-1]))
line = file.readline()
while line:
    type = line.count("\t")
    name = line[line.count("\t"):-1]
    i = -1
    while nodes[i].type >= type and abs(i) <= len(nodes):
        i -= 1
    if abs(i) > len(nodes): path = name
    else: path = nodes[i].path + '/' + name
    node = FW(type, name, path)
    nodes.append(node)
    line = file.readline()

# 3. Using the function below, we can get a list of all files in the zip file.
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

# 4. Main part.
try:
    os.mkdir("result")
    os.mkdir("result/renderings")
    output_dir = os.path.abspath("result")
    # Checking the correctness of input.
    for i in nodes:
        try:
            tmp = fw.lookup(i.path)
        except flywheel.ApiException as e:
            print('The path: %s is illegal.' % (i.path))
            raise

        # Downloading the target zipfile and unzip it into temp.
        try:
            if i.type == 3:
                os.mkdir("temp")
                tmp.download_file('%s.zip' % i.name, '%s.zip' % i.name)
                zip = zipfile.ZipFile('%s.zip' % i.name)
                zip.extractall(path='temp/')
                zip.close()
                # since os.path.abspath() will only append the current work dir with the file/folder passed,
                # we need to change the work dir to temp.
                # flywheel/v0/... => flywheel/v0/temp/...
                os.chdir("temp")

                # find the pbrt file and starting pbrt.
                for curr in os.listdir(os.getcwd()):
                    if not os.path.isdir(os.path.abspath(curr)) and curr == '%s.pbrt' % i.name:
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

                # 5. Uploading files.
                print('Putting files into output...')
                for f in upload_files:
                    print('\t%s...' % (f))
                    # tmp.upload_file(f)     # this line originally committed fot uploading result directly.
                    shutil.copy(f, 'output')
                    os.remove(f)
                print('Done!')

        # 6. We need to delete temp and result for future use. A "try...finally..." will always ensure it.
        finally:
            if os.path.exists('temp'):  shutil.rmtree('temp/')
            if os.path.exists('%s.zip' % i.name):  os.remove('%s.zip' % i.name)
finally:
    if os.path.exists('result'): shutil.rmtree('result/')