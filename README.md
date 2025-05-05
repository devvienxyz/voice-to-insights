# [voice-to-insights](https://github.com/devvienxyz/voice-to-insights)

Record voice notes -> Get clean summaries + Bullet action items

[![codecov](https://codecov.io/gh/devvienxyz/voice-to-insights/branch/main/graph/badge.svg)](https://codecov.io/gh/devvienxyz/voice-to-insights)

## Setup

```bash
./scripts/setup.sh
```

## Development

```bash
docker compose -f docker-compose.dev.yml up --build

# or, without docker:
# streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0 --server.runOnSave=true
```

## Testing

```bash
tox              # run all
tox -e lint      # lint and format check (ruff)
tox -e typecheck # static type checking (mypy)
tox -e py311     # run tests
```

## Support my work

If you find my projects helpful, consider supporting me:

<a href="https://www.buymeacoffee.com/devvienxyz" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="200" />
</a>
