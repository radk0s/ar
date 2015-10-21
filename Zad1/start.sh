#!/bin/sh
#PBS -l nodes=2:ppn=4
#PBS -l walltime=10:30:33

module load libs/boost/1.52.0
pip install --user mpi4py
module load mvapich2
module load mpiexec

mpiexec -np 3 pingpong.py