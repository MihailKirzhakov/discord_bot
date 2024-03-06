@echo off

call %~dp0venv\Scripts\activate

cd %~dp0bot

set TOKEN=MTIxNDg3Mzc2NTk5ODEwODcwMg.G9nNNb.L7eZFLIUsBPc0KybkoLXVetYNJzFXXudutnoz0

python bot_run.py

pause