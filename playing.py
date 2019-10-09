"""
Once a model is learned, use this to play it. that is run/exploit a policy to get the feature expectations of the policy
"""
from mdp import *
import sys
sys.path.insert(1, 'flat_game/')
import carmunk
import numpy as np
from nn import neural_net
import sys
import time
import manualControl
import toy_car_HRL
from birl import *
import math
import curses


NUM_STATES = 8
GAMMA = 0.9

# DAP ################################
# expert weights of sub policies captured by manual control
expert_weights_A_to_B = [6.4156832,  4.45631171, 5.0337354,  1.44288468, 2.83665219, 0.,4.47014758, 0.]
expert_weights_B_to_C = [6.99269636, 5.25697135, 6.04451451, 0.11338186, 2.06359066, 0., 7.35201461, 0.]
expert_weights_C_to_D = [7.11163716, 5.29470348, 5.51959211, 1.55193193, 3.5238935,  0., 4.86054772, 0.]
expert_weights_D_to_E = [7.87843674, 4.25833842, 5.61970949, 0.0864165,  2.43881191, 0., 7.24948759, 0.]
expert_weights_E_to_F = [5.31886323, 3.05535226, 5.30674048, 0.70386583, 3.07872172, 0., 3.67554662, 0.]
expert_weights_F_to_G = [6.69265079, 4.96532849, 4.5920296,  0.34004698, 1.35557813, 0.10679573, 7.10338926, 0.]
expert_weights_G_to_H = [7.17878922, 3.06259749, 4.81231898, 1.42092422,  0., 3.84572925, 3.9356821,  0.]
expert_weights_H_to_I = [7.70629269, 3.27166117, 4.75653448, 1.16855854, 2.50979027, 1.11191387, 4.93160894, 0.]
car_distance = 0

def play(model, weights, x , y , angle, car_distance):

	game_state = carmunk.GameState(weights)
	expert_trace = {(0, 1), (0, 2), (0, 3), (0, 4)}
	_, state, __ = game_state.frame_step((2))

	# DAP ################################
	# setting the new position of car based on subpolicy
	car = carmunk.GameState(weights)
	car.create_car(x, y, 15)
	# setting the new angle of car:
	car.car_body.angle = angle
	featureExpectations = np.zeros(len(weights))
	
	# DAP ################################
	# BHIRL : Bayesian Hierarchical IRL
	# Run the main BIRL algorithm to calculate the posterior and prior probability of being in a state,
	# also it returns the reward error, which can be updated with each iteration.
	# Currently we are running BIRL for 2 iteration and step size of 2. The bounds of reward set her eis +10 and -10

	birl = BIRL(expert_trace, [200,250], [(9, 4)],math.log, birl_iteration=2, step_size=2)
	pi, mdp, policy_error, reward_error = birl.run_birl()
	print(reward_error)

	# Move.
	#time.sleep(15)
	while True:
		car_distance += 1

		# Choose action.
		action = (np.argmax(model.predict(state, batch_size=1)))
		#print ("Action ", action)

		# Take action.
		immediateReward , state, readings = game_state.frame_step(action)

		# Check for crash state in FE, if crash we try out other expert policy using the manualcontrol.py
		# which gives new weights, against which we test the new policy based on this new expert policy.
		# This is an hierachical approach as we check for lower level policy updation only when the 1st sub policy fails.

		if state[0][7] >= 0.95:  #terminal state (Crash : 1, Alive : 0) , so we take chances of more than 0.95
			screen = curses.initscr()
			curses.noecho()
			curses.curs_set(0)
			screen.keypad(1)
			screen.addstr("Play the game")
			new_expert_policy = manualControl.play(screen)
			NUM_STATES = 8
			BEHAVIOR = 'red'  # yellow/brown/red/bumping
			FRAMES = 3000  # number of RL training frames per iteration of H-IRL
			epsilon = 0.1
			# Currently we are using new expert policy given by expert through manual control:
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, new_expert_policy, epsilon, NUM_STATES, FRAMES, BEHAVIOR, reward_error)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# check for the state of car, if it crosses points B, C, D, E, F, G, H or I then we can change the weights
		# according to the new subpolicy.

		# You have successfully crossed point B, so we can call new expert sub-policy for B to C
		if(immediateReward <= 0 and car_distance > 50):
			x = 50
			y = 360
			angle = 1.4
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_B_to_C, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point C, so we can call new expert sub-policy for C to D
		elif(immediateReward <= 0 and car_distance > 100):
			x = 150
			y = 640
			angle = 1.4
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_C_to_D, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point D, so we can call new expert sub-policy for D to E
		elif(immediateReward <= 0 and car_distance > 150):
			x = 600
			y = 640
			angle = 1.4
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_D_to_E, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point E, so we can call new expert sub-policy for E to F
		elif(immediateReward <= 0 and car_distance > 200):
			x = 930
			y = 580
			angle = 200
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_E_to_F, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point F, so we can call new expert sub-policy for F to G
		elif(immediateReward <= 0 and car_distance > 250):
			x = 930
			y = 280
			angle = 200
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_F_to_G, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point G, so we can call new expert sub-policy for G to H
		elif(immediateReward <= 0 and car_distance > 300):
			x = 850
			y = 40
			angle = 110
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_G_to_H, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		# You have successfully crossed point H, so we can call new expert sub-policy for H to I
		elif(immediateReward <= 0 and car_distance > 350):
			x = 550
			y = 40
			angle = 110
			hrlearner = toy_car_HRL.hrlAgent(randomPolicyFE, expert_weights_H_to_I, epsilon, NUM_STATES, FRAMES, BEHAVIOR)
			print (hrlearner.optimalWeightFinder( x , y , angle, car_distance))

		##############################
		#print ("immeditate reward:: ", immediateReward)
		#print ("readings :: ", readings)
		#start recording feature expectations only after 100 frames
		if car_distance > 10:
			featureExpectations += (GAMMA**(car_distance-101))*np.array(readings)
		#print ("Feature Expectations :: ", featureExpectations)
		# Tell us something.
		if car_distance % 2000 == 0:
			print("Current distance: %d frames." % car_distance)
			break

	return featureExpectations


def read(beh, iters, frame):
	BEHAVIOR = beh
	ITERATION = iters
	FRAME = frame
	saved_model = 'saved-models_'+BEHAVIOR+'/evaluatedPolicies/'+str(ITERATION)+'-164-150-100-50000-'+str(FRAME)+'.h5'

	# DAP ################
	# expert weights for red from sub poicy A to B
	x = 150
	y = 20
	angle = 1.4
	car_distance = 0
	expert_weights_A_to_B = [6.4156832,  4.45631171, 5.0337354,  1.44288468, 2.83665219, 0.,4.47014758, 0.]
	model = neural_net(NUM_STATES, [164, 150], saved_model)
	print(play(model, expert_weights_A_to_B, x, y, angle, car_distance ))
