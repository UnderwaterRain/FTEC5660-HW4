"""Run archived configurations as separate processes, using paid DeepSeek calls."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ('B0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variants', nargs='+', choices=VERSIONS, default=list(VERSIONS))
    parser.add_argument('--data-folder', type=Path, default=ROOT / 'public_test')
    parser.add_argument('--results-dir', type=Path, default=ROOT / 'reruns')
    args = parser.parse_args()
    data = args.data_folder.resolve()
    destination = args.results_dir.resolve()
    if not data.is_dir():
        parser.error(f'Data folder does not exist: {data}')
    if destination == (ROOT / 'experiments').resolve():
        parser.error('Use a different results directory to preserve archived observations.')
    destination.mkdir(parents=True, exist_ok=True)
    for version in args.variants:
        script = ROOT / 'experiments' / f'hw4_{version}.py'
        output = destination / f'results_{version}.csv'
        log = destination / f'run_{version}.log'
        if output.exists() or log.exists():
            parser.error(f'{version}: output already exists; choose a new --results-dir.')
        print(f'Running {version}; model calls may incur charges. Log: {log}', flush=True)
        with log.open('w', encoding='utf-8') as handle:
            try:
                completed = subprocess.run(
                    [sys.executable, '-u', str(script), '--data-folder', str(data),
                     '--output', str(output)],
                    cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                    timeout=1800, check=False,
                )
            except subprocess.TimeoutExpired:
                raise SystemExit(f'{version} exceeded 30 minutes; see {log}')
        if completed.returncode or not output.exists():
            raise SystemExit(f'{version} failed; see {log}')
        print(f'Completed {version}: {output}', flush=True)
    print('Summarize with:')
    print(f'python scripts/summarize_results.py --results-dir "{destination}"')


if __name__ == '__main__':
    main()
