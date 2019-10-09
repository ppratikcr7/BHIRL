from flat_game import carmunk
import numpy as np
import random
import csv
from nn import neural_net, LossHistory
import os.path
import timeit
import pandas as pd

NUM_INPUT = 8 
GAMMA = 0.9  # Forgetting.
TUNING = False  # If False, just use arbitrary, pre-selected params.
TRAIN_FRAMES = 3000 # to train for 3K frames in total

#---------------Task 2.a----------------------------------------#
# Creating dictionary and list for storing values in a csv file
max_d = []
t_c = []
epsilon_c = []
car_d = []
fps_c=[]
#------------------------------------------------------------#
def train_net(model, params, weights, path, trainFrames, i):

    filename = params_to_filename(params)

    observe = 1000  # Number of frames to observe before training.
    epsilon = 1
    train_frames = trainFrames  # Number of frames to play. 
    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    max_car_distance = 0
    car_distance = 0
    t = 0
    data_collect = []
    replay = []  # stores tuples of (S, A, R, S').

    loss_log = []

    # Create a new game instance.
    game_state = carmunk.GameState(weights)

    # Get initial state by doing nothing and getting the state.
    _, state, temp1 = game_state.frame_step((2))

    # Let's time it.
    start_time = timeit.default_timer()

    # Run the frames.
    while t < train_frames:

        t += 1
        car_distance += 1

        # Choose an action.
        if random.random() < epsilon or t < observe:
            action = np.random.randint(0, 3)  # random #3
        else:
            # Get Q values for each action.
            qval = model.predict(state, batch_size=1)
            action = (np.argmax(qval))  # best
            #print ("action under learner ", action)

        # Take action, observe new state and get our treat.
        reward, new_state, temp2 = game_state.frame_step(action)

        # Experience replay storage.
        replay.append((state, action, reward, new_state))

        # If we're done observing, start training.
        if t > observe:

            # If we've stored enough in our buffer, pop the oldest.
            if len(replay) > buffer:
                replay.pop(0)

            # Randomly sample our experience replay memory
            minibatch = random.sample(replay, batchSize)

            # Get training values.
            X_train, y_train = process_minibatch(minibatch, model)

            # Train the model on this batch.
            history = LossHistory()
            model.fit(
                X_train, y_train, batch_size=batchSize,
                nb_epoch=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)

        # Update the starting state with S'.
        state = new_state

        # Decrement epsilon over time.
        if epsilon > 0.1 and t > observe:
            epsilon -= (1/train_frames)

        # We died, so update stuff.
        if state[0][7] == 1:
            # Log the car's distance at this T.
            data_collect.append([t, car_distance])

            # Update max.
            if car_distance > max_car_distance:
                max_car_distance = car_distance

            # Time it.
            tot_time = timeit.default_timer() - start_time
            fps = car_distance / tot_time

            # Output some stuff so we can watch.
            print("Max: %d at %d\tepsilon %f\t(%d)\t%f fps" %
                  (max_car_distance, t, epsilon, car_distance, fps))
            
            #-----------------Task -2.a----------------------------#
            # saving to csv file 
            max_d.append(max_car_distance)
            t_c.append(t)
            epsilon_c.append(epsilon)
            car_d.append(car_distance)
            fps_c.append(fps)
            
            #------------------------------------------------------#

            # Reset.
            car_distance = 0
            start_time = timeit.default_timer()

        # Save the model 
        if t % train_frames == 0:
            model.save_weights('saved-models_'+ path +'/evaluatedPolicies/'+str(i)+'-'+ filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))

    # Log results after we're done all frames.
    log_results(filename, data_collect, loss_log)


def log_results(filename, data_collect, loss_log):
    # Save the results to a file so we can graph it later.
    with open('results/sonar-frames/learn_data-' + filename + '.csv', 'w') as data_dump:
        wr = csv.writer(data_dump)
        wr.writerows(data_collect)

    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        for loss_item in loss_log:
            wr.writerow(loss_item)


def process_minibatch(minibatch, model):
    """This does the heavy lifting, aka, the training. It's super jacked."""
    X_train = []
    y_train = []
    # Loop through our batch and create arrays for X and y
    # so that we can fit our model at every step.
    for memory in minibatch:
        # Get stored values.
        old_state_m, action_m, reward_m, new_state_m = memory
        # Get prediction on old state.
        old_qval = model.predict(old_state_m, batch_size=1)
        # Get prediction on new state.
        newQ = model.predict(new_state_m, batch_size=1)
        # Get our best move. I think?
        maxQ = np.max(newQ)
        y = np.zeros((1, 3)) #3
        y[:] = old_qval[:]
        # Check for terminal state.
        if new_state_m[0][7] == 1:  #terminal state (Crash : 1, Alive : 0)
            update = reward_m
        else:  # non-terminal state
            update = (reward_m + (GAMMA * maxQ))
        # Update the value for the action we took.
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(3,)) #3

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train

def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
            str(params['batchSize']) + '-' + str(params['buffer'])

def launch_learn(params):
    filename = params_to_filename(params)
    print("Trying %s" % filename)
    # Make sure we haven't run this one.
    if not os.path.isfile('results/sonar-frames/loss_data-' + filename + '.csv'):
        # Create file so we don't double test when we run multiple
        # instances of the script at the same time.
        open('results/sonar-frames/loss_data-' + filename + '.csv', 'a').close()
        print("Starting test.")
        # Train.
        model = neural_net(NUM_INPUT, params['nn'])
        train_net(model, params)
    else:
        print("Already tested.")

def HRL_helper(weights, path, trainFrames, i):
    nn_param = [164, 150]
    params = {
        "batchSize": 100,
        "buffer": 50000,
        "nn": nn_param
    }
    model = neural_net(NUM_INPUT, nn_param)
    train_net(model, params, weights, path, trainFrames, i)



if __name__ == "__main__":
    weights = [6.4156832, 4.45631171, 5.0337354,  1.44288468, 2.83665219, 0., 4.47014758, 0.]
    i=2
    path = 'red'
    if TUNING:
        param_list = []
        nn_params = [[164, 150], [256, 256],
                     [512, 512], [1000, 1000]]
        batchSizes = [40, 100, 400]
        buffers = [10000, 50000]

        for nn_param in nn_params:
            for batchSize in batchSizes:
                for buffer in buffers:
                    params = {
                        "batchSize": batchSize,
                        "buffer": buffer,
                        "nn": nn_param
                    }
                    param_list.append(params)

        for param_set in param_list:
            launch_learn(param_set)

    else:
        nn_param = [164, 150]
        params = {
            "batchSize": 100,
            "buffer": 50000,
            "nn": nn_param
        }
        model = neural_net(NUM_INPUT, nn_param)
        train_net(model, params, weights, path, TRAIN_FRAMES, i)
        
 
    #-----------------------------Task -2.a---------------------#
    # creating a csv file
    dict_ = {'time':t_c, 'car_distance':car_d}

    df = pd.DataFrame(dict_)
    # check the output.csv file for the output it contains car_distance and time at which car crashes
    df.to_csv('output.csv', header = False, index = False)
    print("Outpust saved for graphical results in csv")
    
    #----------------------------------------------------------#

