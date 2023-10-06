I ran three experiments, the only variable was replay memory size.
Constants:
BATCH_SIZE = 128
GAMMA = 0.99
LR = 1e-5
EPS_START
EPS_END = 0.1
EPS_DECAY = 800000
GRAD_CLIP_MIN = -10
GRAD_CLIP_MAX = 10
TAU = 0.005

Results:
	memory: 100 : −0.2275
	memory: 1000 : -0.1315
	memory: 10000 : -0.2545
	
	
Conculusion:
	1000 had a .1 higher reward after 390k steps than 100. 100 also experienced loss explosion while 1000 did not.