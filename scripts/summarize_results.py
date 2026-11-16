"""Summarize recorded runner CSVs; no LLM calls or corpus access."""
import argparse
import csv
from pathlib import Path

VERSIONS = ('B0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6')
ROOT = Path(__file__).resolve().parents[1]


def fraction(items, predicate):
    return sum(predicate(item) for item in items) / len(items) if items else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, default=ROOT / 'experiments')
    args = parser.parse_args()
    print('Version | Recall@5 | Answerable kept | Unanswerable rejected | Accuracy')
    found = 0
    for version in VERSIONS:
        path = args.results_dir / f'results_{version}.csv'
        if not path.exists():
            continue
        with path.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        if not rows or any(not r.get('category') or not r.get('correct') for r in rows):
            raise ValueError(f'{path}: missing labeled evaluation results')
        answerable = [r for r in rows if r['category'] != 'unanswerable']
        unanswerable = [r for r in rows if r['category'] == 'unanswerable']
        values = (
            fraction(answerable, lambda r: r['retrieval_hit'].lower() == 'true'),
            fraction(answerable, lambda r: bool(r['retrieved'])),
            fraction(unanswerable, lambda r: not r['retrieved']),
            fraction(rows, lambda r: r['correct'].lower() == 'true'),
        )
        print(version + ' | ' + ' | '.join(f'{value:.1%}' for value in values))
        found += 1
    if not found:
        raise SystemExit(f'No result files found in {args.results_dir}')


if __name__ == '__main__':
    main()
