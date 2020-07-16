import flywheel

user_id = 'stanfordlabs.flywheel.io:dddk2FvdSYhElu6BFK'
fw = flywheel.Client(user_id)
gear = fw.lookup('gears/pbrt-gear/0.2.1')
gear.print_details()

session = fw.lookup('wandell/Graphics test/scenes/suburb')
print(session)
inputs = {}
config = {}
analysis_id = gear.run(analysis_label = 'suburb_analysis', config=config, inputs=inputs, destination=session)

# # To simulate a batch, run this part
# session = fw.lookup('wandell/Graphics test/scenes/suburb')
# t1_acquisitions = session.acquisitions()
# proposal = gear.propose_batch(t1_acquisitions, config={})
# jobs = proposal.run()