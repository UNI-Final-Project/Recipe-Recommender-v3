import os
import subprocess


def run(cmd):
    print('RUN:', cmd)
    r = subprocess.run(cmd, shell=True)
    assert r.returncode == 0


def test_embeddings_eval():
    # modo simulado (sin clave) debe ejecutarse retorna 0
    run('python -m mlops.scripts.evaluate_embeddings --model testembedding-3small')


def test_llm_eval():
    run('python -m mlops.scripts.evaluate_llm --model gpt-4.1')
