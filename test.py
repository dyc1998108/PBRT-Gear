import flywheel

user_id = '' # to run this test, you first need to replace your flywheel user_id with the blank here.
fw = flywheel.Client(user_id)
gear = fw.lookup('gears/pbrt-gear/0.1.0') # if you want to test other version of the gear or even other gear, change this line as well.
gear.print_details()

# if the gear is a utility one, run this part.
acquisition = fw.lookup('wandell/Graphics test/test subject/test session/checkerboard') # change the path if you want.
inputs = {
        'file': acquisition.get_file('checkerboard.zip')
}
config = {
        'user_id':user_id
}
job_id = gear.run(config=config, inputs=inputs, destination=acquisition, tags=['my-job'])

# if the gear is a analysis one, run this part.
acquisition = fw.lookup('wandell/Graphics test/test subject/test session/checkerboard') # change the path if you want.
inputs = {
        'file': acquisition.get_file('checkerboard.zip')
}
config = {
        'user_id':user_id
}
analysis_id = gear.run(analysis_label = 'checkerboard_analysis', config=config, inputs=inputs, destination=acquisition)

# To simulate a batch, run this part
session = fw.lookup('wandell/Graphics test/test subject/test session')
t1_acquisitions = session.acquisitions()
proposal = gear.propose_batch(t1_acquisitions, config={'user_id': user_id})
jobs = proposal.run()