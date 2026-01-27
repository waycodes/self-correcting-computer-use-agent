# Reproducibility

This project follows strict reproducibility conventions to ensure experiments can be replicated.

## Seed Control

Use `sca.utils.repro.set_seed()` at the start of any run:

```python
from sca.utils.repro import set_seed

seed_state = set_seed(42)
```

## Run Manifests

Every run should emit a manifest capturing:
- Git SHA
- Package version
- Seed state
- Full config

```python
from sca.logging.run_manifest import RunManifest

manifest = RunManifest(
    run_id="my-run-001",
    seed_state=seed_state,
    config={"task": "example", "max_steps": 100},
)
manifest.save(Path("outputs/manifest.json"))
```

## Environment Variables

Set `PYTHONHASHSEED` for full determinism:

```bash
PYTHONHASHSEED=42 python -m sca.cli run ...
```
