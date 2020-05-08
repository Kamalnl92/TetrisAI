from dqn_agent import DQNAgent
from tetris import Tetris
from datetime import datetime
from statistics import mean, median
import random
from logs import CustomTensorBoard
from tqdm import tqdm
import itertools


# Run dqn with Tetris
def dqn():

    env = Tetris()
    episodes = 2000  # 2000
    max_steps = None
    epsilon_stop_episode = 15000  # 1500
    mem_size = 2000 # 20000
    discount = 0.95
    batch_size = 512  # 512
    epochs = 1
    render_every = 50  # 50
    log_every = 50  # 50
    replay_start_size = 2000  # 2000
    train_every = 1
    n_neurons = [160, 160, 160, 160, 160]
    render_delay = None
    activations = ['relu', 'relu', 'relu', 'relu', 'relu', 'linear']
    # -------------------In play mode------------------- #
    # put model name that you want it to play in model_name below
    # set render_every = 1  in line 21
    # set agent_play below to True
    # set fetch_old_model below to True
    # the model will not be trained nor will be saved
    # the model lines clearing scoring will be saved if you let the model finish the episodes set above
    # ------------------- play mode Nuno Faria ------------------- #
    # same steps as in play mode, then
    # set board_state True
    # model_name = 'models/original'
    # ------------------- if training from scratch ------------------- #
    # set fetch_old_model = False, agent_play = false, board_state = False
    # ------------------- continue training ------------------- #
    # can continue the model but keep in mind that it will start exploring in the beginning again
    # set the model name that you want to continue training from
    # set fetch_old_model = True, agent_play = false, board_state = false
    # after the training is done, give the model and the files appropriate name

    # all model names, line_logging and the logs will be save with the same time stamp
    # choosing which model to train
    # 1 full board or board state input also for the nuno_faria
    # 2 CNN
    # 3 CNN merged
    # 4 Nuno Faria
    model_number = 3
    model_name = 'models/my_model-20200504-233443-h5'
    # Rendering false for Peregrine
    board_state = False
    rendering = True
    fetch_old_model = False
    agent_play = False

    if board_state:
        input_size = [1, 4]
    else:
        input_size = [1, 200]

    agent = DQNAgent(env.get_board_size(),
                     n_neurons=n_neurons, activations=activations,
                     epsilon_stop_episode=epsilon_stop_episode, mem_size=mem_size,
                     discount=discount, replay_start_size=replay_start_size, fetch_old_model=fetch_old_model,
                     model_name=model_name, model_number=model_number)

    time_frame = datetime.now().strftime("%Y%m%d-%H%M%S")

    open('lines_logging/' + f'linesfile-{time_frame}.txt', 'w') # creating file for the line logging
    log_dir = f'logs/tetris-nn={str(n_neurons)}-mem={mem_size}-bs={batch_size}-e={epochs}-{time_frame}'
    log = CustomTensorBoard(log_dir=log_dir)

    scores = []

    for episode in tqdm(range(episodes)):

        #current_board = env.reset()
        # env.reset()
        if board_state:
            current_board = [0]*4
        else:
            current_board = env.reset()
            #print(current_board)

        done = False
        steps = 0

        if rendering:
            if render_every and episode % render_every == 0:
                render = True
            else:
                render = False
        else:
            render = False

        # *k Game
        while not done and (not max_steps or steps < max_steps): #agent_train, input_size
            next_boards = env.get_next_boards(board_state)  # returns the all possible moves in next_state
            best_board = agent.best_board(next_boards.values(), agent_play, input_size, board_state)

            best_action = None

            for action, board in next_boards.items():  # Find the corresponding action for the desired board
                if board == best_board:
                    best_action = action
                    break
            # Reward each block placed yields 1 point. When clearing lines, the given score is
            # number_lines_cleared^2 × board_width. Losing a game subtracts 1 point.
            reward, done = env.play(best_action[0], best_action[1], render=render,
                                    render_delay=render_delay, time_frame=time_frame)

            if board_state:
                agent.add_to_memory(current_board, next_boards[best_action], reward, done)
            else:
                agent.add_to_memory(list(itertools.chain.from_iterable(current_board)),
                                    list(itertools.chain.from_iterable(next_boards[best_action])),
                                    reward, done)

            current_board = next_boards[best_action]
            steps += 1

        scores.append(env.get_game_score())

        # Train
        if episode % train_every == 0 and not agent_play:
            agent.train(batch_size=batch_size, epochs=epochs, model_number=model_number)
        # Logs
        if log_every and episode and episode % log_every == 0:
            avg_score = mean(scores[-log_every:])
            min_score = min(scores[-log_every:])
            max_score = max(scores[-log_every:])

            log.log(episode, avg_score=avg_score, min_score=min_score,
                    max_score=max_score)
    # save the model
    if not agent_play:
        agent.model_save(time_frame)


if __name__ == "__main__":
    dqn()