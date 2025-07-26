# Master-Thesis
This is an extract of the code developed for my Master Thesis, accompanied with the final Thesis text. It's a research about the use of symbolic planning to aid RL training phase.

This thesis is an explorative study regarding the effectiveness of symbolic planningbased approaches as support for typical Reinforcement Learning algorithms.
Planning-based approaches deal in similar contexts as Reinforcement Learning’s ones, but generally on a higher level of abstraction. 
They both define their problem with MDP assumptions and both aim to do the same thing, to teach an agent what action/move to select for each given state in order to reach a goal.
Motivated by that, the study on this thesis generates a plan with a symbolic planningbased approach and uses it as a starting point/initialization for Reinforcement Learning algorithms.
The selected case study is the Lunar Lander environment offered by Gymnasium’s OpenAI, a minigame in which a spacecraft has to land safely on the ground.
The planning-based method involves an initial discretization of the domain to transpose the original environment in finite domain variables, a domain and problem definition in FOND (Fully Observable Non-Deterministic) settings to generate a plan that will be used to initially guide the reinforcement learning model.
The experiment with the proposed methods confirm the struggle of tabular versions of RL with this kind of environment, but show promising results with the Deep Q-Learning version methods that can solve the environment in a shorter time.
