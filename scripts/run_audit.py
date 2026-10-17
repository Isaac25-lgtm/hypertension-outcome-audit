"""Run the released-data audit end to end: tables -> results/tables, figure -> results/figures."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from htn_audit import audit, figures  # noqa: E402

res = audit.run()
for name, t in res["tables"].items():
    if name in ("schema", "age_label_audit"):
        continue
    print(f"\n== {name} ==")
    print(t.to_string(index=False))
print("\n== anomalies ==")
print(json.dumps(res["anomalies"], indent=2))
figures.reconciliation_figure(res["tables"]["followup_reconciliation"], res["tables"]["regression_bounds"])
print("figure written")
