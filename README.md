# Scitify
This repository stores code for retrieving publications of a certain topic from the following sources automatically: bioRxiv, arXiv, and PubMed based on specified keywords.


# ctfGadget

ctfGadget can either be used as a standalone tool or within the [TomoCHAMPS](https://github.com/cyanching/TomoCHAMPS) workflow. It runs on one or more GPU(s) and parallelised CPU cores. At last, it allows the user to inspect poor-quality images and their corresponding CTF fit plots that were picked out to be discarded, and decide whether the decision should be final. If the data quality is satisfactory, you should only have very few images to discard. And of course, if you decide to skip this step, then the tilts will be discarded automatically.

We have been using ctfGadget for fast assessment of our *in vitro* cryo-ET datasets (of varying quality) acquired (mostly on lacey grids) externally on Titans and on our own Glacios without an energy filter. And we found it is a necessary step to avoid manual curation in further processing steps especially when the ice thickness is high. After completing all ctfGadget steps, you can directly continue processing if you have TomoCHAMPS installed and activated.

This tool was written by [Cyan Ching](https://cyanching.github.io/) (if ctfGadget fails, and it is REALLY not from your end, mainly blame this person) & [Julien Maufront](https://fr.linkedin.com/in/julien-maufront-032539135) (our awesome research engineer who devoted great effort to make ctfGadget user-friendly), and tested by [Astrid Canal](https://fr.linkedin.com/in/astrid-canal-bizeul-acb/no) (our brilliant master student who made your life EVEN easier, e.g., ctfGadget now automatically closes the opened windows when inspecting poor-quality images as you go). This tool is a production of the [Molecular Microscopy of Membranes team](https://institut-curie.org/team/levy) at the [Physical Chemistry Curie Lab](https://institut-curie.org/unit/umr168) of [Institut Curie](https://curie.fr/) headed by [Daniel Lévy](https://institut-curie.org/personne/daniel-levy). 

## Installation

### 1. Install MotionCor2 and ctffind4

Before you clone ctfGadget, please make sure you already have both [MotionCor2](https://emcore.ucsf.edu/ucsf-software) and [ctffind4](https://grigoriefflab.umassmed.edu/ctf_estimation_ctffind_ctftilt) installed on your Linux machine, follow the link associated with these softwares to download and install them. They are incredibly easy to install. While MotionCor2 depends on GPU, the rest of ctfGadget only requires CPU. We recommend the following versions: `MotionCor2 1.6.4` (requires CUDA 10.1 and above), and `ctffind-4.1.14`. Choose their respective folders for installation (the recommended destination can be `/usr/local`), you simply need to `unzip` and `tar` the files you have downloaded from their sites to make them ready-to-use. 

#### For MotionCor2

```
sudo mkdir /usr/local/MotionCor2_1.6.4
sudo unzip ~/Downloads/MotionCor2_1.6.4_Mar31_2023.zip -d /usr/local/MotionCor2_1.6.4
```
#### For ctffind4

```
sudo tar -xf ~/Downloads/ctffind-4.1.14-patched.tar.gz -C /usr/local/
```
