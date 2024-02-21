## Run

```bash
gunicorn -w 4 -b 0.0.0.0:4050 --timeout 3600 app:app
```

Or

```bash
gunicorn -w 4 -b 0.0.0.0:4050 --reload --timeout 3600 app:app
```