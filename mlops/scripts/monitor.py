"""Monitor simple: escribe eventos métricos en `mlops/monitor.log`."""
import argparse
import datetime
import os


LOG_PATH = 'mlops/monitor.log'


def log_event(message):
    os.makedirs('mlops', exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat() + 'Z'
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{ts} - {message}\n")
    print('Evento registrado en', LOG_PATH)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', required=True)
    args = parser.parse_args()
    log_event(args.message)
