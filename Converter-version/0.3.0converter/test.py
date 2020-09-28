import flywheel

# Copy your id here.
user_id = ''
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
job_id = gear.run(config=config, inputs=inputs, destination=acquisition, tags=['converter_0.3.3'])

# 2. To simulate a batch, run this part.
# However, due to the underlying implementation of converter gear, there are other ways available to run a batch:
# Regardless of the fact that we are passing acquisitions list to propose a batch tests, the gear will only end up
# receiving session objects that each acquisition belongs to. Therefore in fact when running a batch, it is multiple
# sessions that passed to the gear, and no matter how much acquisitions that from one same session are in the passed
# list, the result will always be the same. So here I guess, no matter what form taken, just pass a list that contains
# some acquisitions to 'propose_batch', the program will still work and result in same output.
session = fw.lookup('wandell/Graphics test/scenes/suburb')
t1_acquisitions = session.acquisitions()
proposal = gear.propose_batch(t1_acquisitions, config={})
jobs = proposal.run()

# 3. To run specific multiple acquisitions in an acquisition, use 'for' loop.
session = fw.lookup('wandell/Graphics test/scenes/suburb')
acquisitions = session.acquisitions()
inputs = {}
config = {}
# Here is just an example to run the first two acquisitions, other methods are also feasible.
# The main point is to separately passing acquisitions, which create multiple jobs as well.
for i in range(2):
    print(gear.run(config=config, inputs=inputs, destination=acquisitions[i], tags=[acquisitions[i]['label']]))