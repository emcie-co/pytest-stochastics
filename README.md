# pytest-stochastics

A pytest plugin for running stochastic tests with configurable thresholds.

## Features

- Run stochastic tests multiple times with customizable pass/fail criteria
- Configure different test plans with fallback options

## Installation

You can install pytest-stochastics using pip:

```bash
pip install git+https://github.com/emcie-co/pytest-stochastics.git#egg=pytest_stochastics
```

Or if you're using Poetry:

```bash
poetry add git+https://github.com/emcie-co/pytest-stochastics.git#egg=pytest_stochastics
```

## Usage

### Configuration

Create a `pytest_stochastics_config.json` file in your project root with your test configuration:

```json
{
    "plan_tests": [
        {
            "plan": "weak",
            "threshold_tests": [
                {
                    "threshold": "always",
                    "tests": [
                        "tests/test_abc/test_1", 
                    ]
                },
                {
                    "threshold": "mostly",
                    "tests": [
                        "tests/test_abc/test_2",
                        "tests/test_abc/test_3"
                    ]
                }
            ]
        },
        {
            "plan": "strong",
            "threshold_tests": [
                {
                    "threshold": "always",
                    "tests": [
                        "tests/test_abc/test_2"
                    ]
                }
            ]
        }
    ],
    "thresholds": [
        {
            "threshold": "always",
            "at_least": 3,
            "out_of": 3
        },
        {
            "threshold": "mostly",
            "at_least": 2,
            "out_of": 3
        }
    ],
    "plan_fallbacks": [
        {
            "plan": "strong",
            "overrides": "weak"
        }
    ]
}
```

### Running Tests

Run your tests as usual with pytest:

```bash
pytest
```
> **You may override the default behaviour by defining a custom plan named `default`.**

To specify a different plan:

```bash
pytest --plan another_plan
```
