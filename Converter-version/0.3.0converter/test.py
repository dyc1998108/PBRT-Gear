import flywheel

# Copy your id here.
user_id = 'stanfordlabs.flywheel.io:v1PolPtR2GQrXSp7Jr'
fw = flywheel.Client(user_id)

# Get the Flywheel Example Utility gear
gear = fw.lookup('gears/pbrt-gear-converter/0.3.3')
gear.print_details()

# 1. This part is used for testing converter gear with single acquisition.
# Here I just use city3 as an example.
acquisition = fw.lookup('wandell/Graphics test/batchtest/batchtest/suburb_9-30_v0.0_f40.00front_o270.00_20205885756')
# Since our gear don't receive any input and config, nothing will be include in these two parameters.
inputs = {}
config = {}
# here 'tags' could be change to anything you like.
job_id = gear.run(config=config, inputs=inputs, destination=acquisition, tags=['converter_city3'])

# 2. To run specific multiple acquisitions in an acquisition, use 'for' loop.
session = fw.lookup('wandell/Graphics test/scenes/suburb')
acquisitions = session.acquisitions()
inputs = {}
config = {}
# Here is just an example to run the first two acquisitions, other methods are also feasible.
# The main point is to separately passing acquisitions, which create multiple jobs as well.
for i in range(2):
    print(gear.run(config=config, inputs=inputs, destination=acquisitions[i], tags=[acquisitions[i]['label']]))