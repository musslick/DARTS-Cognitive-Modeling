This repository showcases the recovery of quantitative models of human information processing with differentiable architecture search (DARTS).

# Installation
Requires Python 3.7.
Required packages are listed in requirements.txt

# Note
We are currently in the process of adding full documentation and tutorials for this code, as part of a pipeline for autonomous empirical research (empiricalresearch.ai). Please stay tuned for updates.

We adopted parts of the code from:
https://github.com/quark0/darts

# Execution
To run the recovery of the weber model with original DARTS 

*python run_weber_original_study_slurm.py --slurm_id 0*

The *slurm_id* may vary from 0-149 and generates results for different combinations of 
- the number of intermediate nodes k and
- the parameter penalty gamma


# References
Liu, H., Simonyan, K., & Yang, Y. (2018). Darts: Differentiable architecture search. arXiv preprint arXiv:1806.09055.

Musslick, S. (2021). Recovering Quantitative Models of Human Information Processing with Differentiable Architecture Search. 
arXiv preprint arXiv:2103.13939.
