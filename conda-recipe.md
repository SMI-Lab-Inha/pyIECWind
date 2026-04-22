# Conda Install

Use your Miniconda installation directly if `conda` is not on `PATH`:

```powershell
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' env create -f environment.yml
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' run -n pyiecwind pyiecwind --help
```

If you prefer to create the environment manually:

```powershell
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' create -n pyiecwind python=3.11 numpy pip -y
& 'C:\Users\burak\miniconda3\Scripts\conda.exe' run -n pyiecwind python -m pip install -e .
```
