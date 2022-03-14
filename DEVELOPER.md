## Building and Testing Open Robo-Advisor

Some notes for developers.

### Testing

```
pdm run pytest
```

### Type Checking

```
pdm run mypy --strict src tests
```

### Uploading to Pypi

First, build:

```
pdm build
```

Then, upload to test:

```
pdm run twine upload --repository testpypi dist/*
```

Verify test, then upload to production:

```
pdm run twine upload dist/*
```
