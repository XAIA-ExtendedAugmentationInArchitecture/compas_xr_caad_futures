__Installing Compas XR Dependencies for Compas XR CAAD Futures__

# CLONE REPO
1. `clone to path/to/compas_xr_caad_futures`

# STEPS FOR INSTALLING THROUGH ANACONDA PROMPT:
1. `conda env create -f /path/to/compas_xr_caad_futures_env.yml`
2. `conda activate compas_xr_caad_futures_env`
3. `cd /path/to/compas_xr_caad_futures`
4. `pip install -e .`
5. `python -m compas_rhino.install -v 7.0`