import flywheel

user_id = 'stanfordlabs.flywheel.io:R8A5uq2z1xyOmpB69j'
fw = flywheel.Client(user_id)
gear = fw.lookup('gears/pbrt-gear-utility/0.2.2')
gear.print_details()

# session = fw.lookup('wandell/Graphics test/scenes/suburb')
# print(session)
# inputs = {}
# config = {}
# analysis_id = gear.run(analysis_label = 'suburb_analysis', config=config, inputs=inputs, destination=session)

# To simulate a batch, run this part
session = fw.lookup('wandell/Graphics test/scenes/single scene')
t1_acquisitions = session.acquisitions()
proposal = gear.propose_batch(t1_acquisitions, config={})
jobs = proposal.run()
