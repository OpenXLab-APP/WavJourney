conda env create -f Envs/AudioCraft.yml
conda run --live-stream -n AudioCraft pip install -U git+https://git@github.com/facebookresearch/audiocraft@c5157b5bf14bf83449c17ea1eeb66c19fb4bc7f0#egg=audiocraft
# Could not load library libcudnn_cnn_infer.so.8.
# Error: libnvrtc.so: cannot open shared object file: No such file or directory
CONDAENV=AudioCraft
source activate ${CONDAENV}
conda install -c "nvidia/label/cuda-11.8.0" cuda-toolkit
python3 -m pip install nvidia-cudnn-cu11==8.5.0.96
source deactivate
mkdir -p $CONDA_PREFIX/envs/${CONDAENV}/etc/conda/activate.d
echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/envs/${CONDAENV}/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/envs/${CONDAENV}/etc/conda/activate.d/env_vars.sh
source $CONDA_PREFIX/envs/${CONDAENV}/etc/conda/activate.d/env_vars.sh

# If you're using WSL2, you can add the following into ~/.bashrc
# export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH
