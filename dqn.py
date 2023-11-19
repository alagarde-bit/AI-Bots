import pandas as pd
import numpy as np
import tensorflow as tf
import random

nvidia = pd.read_csv('NVDA.csv')
np.random.seed(5)
nvidia['Open'] = (nvidia['Open'] - nvidia['Open'].min()) / (nvidia['Open'].max() - nvidia['Open'].min())
#initializing state space
account_balance = 20000
nvidia_shares_owned = 0
nvidia_price = round(nvidia[1])
action_space = np.array(["buy", "sell", "hold"])

GAMMA=0.95
LEARNING_RATE = 0.001
min_eps = 0.01
episodes = len(nvidia.index)
eps = 1
decay_rate=0.995
replay_memory = []
def model_fit(model, replay_memory, batch_size):
    # Sample experiences from the replay memory
    experiences = replay_memory.sample(batch_size)

    # Separate experiences into state, action, reward, and next state
    states = []
    actions = []
    rewards = []
    next_states = []

    for experience in experiences:
        state, action, reward, next_state = experience
        states.append(state)
        actions.append(action)
        rewards.append(reward)
        next_states.append(next_state)

    # Convert data into NumPy arrays
    states = np.array(states)
    actions = np.array(actions)
    rewards = np.array(rewards)
    next_states = np.array(next_states)

    # Calculate target Q-values using Bellman equation
    target_q_values = model.predict(next_states)
    max_q_values = np.max(target_q_values, axis=1)
    target_q_values = rewards + GAMMA * max_q_values

    # Predict Q-values for current states
    predicted_q_values = model.predict(states)

    # Update Q-values for selected actions
    for i, action in enumerate(actions):
        predicted_q_values[i, action] = target_q_values[i]

    # Calculate loss using mean squared error
    loss = np.mean((target_q_values - predicted_q_values)**2)

    # Update model weights using gradient descent
    model.compile(loss='mse', optimizer='adam')
    model.fit(states, predicted_q_values, epochs=1, verbose=0)

def push_experience(experience):
    # Add the experience tuple to the replay memory
    replay_memory.append(experience)

def buy(account_balance, nvidia_shares_owned, nvidia_price, nvidia_next_price):
    try:
        # Check if account balance is sufficient to buy one share
        if account_balance < nvidia_price:
            raise ValueError("Insufficient account balance to buy a share")

        # Calculate the maximum number of shares to buy
        max_shares_to_buy = int(account_balance / nvidia_price)

        # Determine the actual number of shares to buy
        shares_to_buy = min(max_shares_to_buy, 20)

        # Update account balance and number of shares owned
        new_account_balance = account_balance - shares_to_buy * nvidia_price
        new_nvidia_shares_owned = nvidia_shares_owned + shares_to_buy

        # Calculate reward based on the difference between next price and current price
        reward = nvidia_next_price - nvidia_price

        return new_account_balance, new_nvidia_shares_owned, reward
    except ValueError:
        return account_balance, nvidia_shares_owned, 0, "Insufficient account balance"


def sell(account_balance, nvidia_shares_owned, nvidia_price, nvidia_next_price):
    try:
        # Check if there are any shares to sell
        if nvidia_shares_owned == 0:
            raise ValueError("No shares to sell")

        # Determine the maximum number of shares to sell
        shares_to_sell = min(nvidia_shares_owned, 20)

        # Update account balance and number of shares owned
        new_account_balance = account_balance + shares_to_sell * nvidia_price
        new_nvidia_shares_owned = nvidia_shares_owned - shares_to_sell

        # Calculate reward based on the difference between current price and next price
        reward = nvidia_price - nvidia_next_price

        return new_account_balance, new_nvidia_shares_owned, reward
    except ValueError:
        return account_balance, nvidia_shares_owned, 0, "No shares to sell"
def model_builder(input_size, output_size):
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(units=32, activation='relu', input_shape=(input_size,)))
    model.add(tf.keras.layers.Dense(units=64, activation='relu'))
    model.add(tf.keras.layers.Dense(units=128, activation='relu'))
    model.add(tf.keras.layers.Dense(units=output_size, activation='linear'))
    return model
def select_action(model, state):
    # Get the Q-values for the current state from the DQN model
    q_values = model.predict(state)

    # Find the index of the action with the highest Q-value
    action_index = np.argmax(q_values)

    # Get the corresponding action from the action space
    action = action_space[action_index]

    return action

dqn = model_builder(3, 3)

for i in np.arange(1, episodes):
    if i == episodes - 1:
        break
    open_price = nvidia.loc[i, 'Open']
    next_price = nvidia.loc[i + 1, 'Open']
    state_space = np.array([account_balance, nvidia_shares_owned, open_price])
       # Exploration-exploitation trade-off
    if np.random.rand() < eps or i < 60:
        # Explore: choose a random action
        action = np.random.choice(action_space)
        if action == "buy":
            account_balance, nvidia_shares_owned, reward, issue = buy(account_balance, nvidia_shares_owned, open_price, next_price)
            if issue=="problem":
                new_action = np.random.choice(["sell", "hold"])
                if new_action == "sell":
                    account_balance, nvidia_shares_owned, reward, issue = sell(account_balance, nvidia_shares_owned, open_price, next_price)
                    if issue == "problem":
                        new_action = "hold"
        elif action == "sell":
            account_balance, nvidia_shares_owned, reward, issue = sell(account_balance, nvidia_shares_owned, open_price, next_price)
            if issue == "problem":
                new_action = np.random.choice(["buy", "hold"])
                if new_action == "buy":
                    account_balance, nvidia_shares_owned, reward, issue = buy(account_balance, nvidia_shares_owned, open_price, next_price)
                    if issue == "problem":
                        new_action = "hold"
        elif action == "hold":
            reward = 0
        push_experience((state_space, action, reward, np.array([account_balance, nvidia_shares_owned, next_price])))
        eps = eps * decay_rate
    else:
        # Exploit: choose the action with the highest Q-value
        action = select_action(dqn, np.array([state_space]))
        if action == "buy":
            account_balance, nvidia_shares_owned, reward, issue = buy(account_balance, nvidia_shares_owned, open_price, next_price)
            if issue == "problem":
                new_action = np.random.choice(["sell", "hold"])
                if new_action == "sell":
                    account_balance, nvidia_shares_owned, reward, issue = sell(account_balance, nvidia_shares_owned, open_price, next_price)
                    if issue == "problem":
                        new_action = "hold"
        elif action == "sell":
            account_balance, nvidia_shares_owned, reward, issue = sell(account_balance, nvidia_shares_owned, open_price, next_price)
            if issue == "problem":
                new_action = np.random.choice(["buy", "hold"])
                if new_action == "buy":
                    account_balance, nvidia_shares_owned, reward, issue = buy(account_balance, nvidia_shares_owned, open_price, next_price)
                    if issue == "problem":
                        new_action = "hold"
        elif action == "hold":
            reward = 0
        push_experience((state_space, action, reward, np.array([account_balance, nvidia_shares_owned, next_price])))
        model_fit(dqn, replay_memory, 32)
        eps = eps * decay_rate
      
