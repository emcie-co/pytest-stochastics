# pytest-stochastics

A pytest plugin for running stochastic tests with configurable policies.

> Definition: Stochastic Test - A test that may occasionally fail due to the non-deterministic character of the test subject. Evaluated by an `at_least` of out `out_of` model.

## Features

- Run stochastic tests multiple times with customizable pass/fail criteria
- Configure different test plans with fallback options

## Installation

You can install pytest-stochastics using pip:

```bash
pip install git+https://github.com/emcie-co/pytest-stochastics.git#egg=pytest_stochastics
# or
pip install git+ssh://git@github.com/emcie-co/pytest-stochastics.git#egg=pytest_stochastics
```

Or if you're using Poetry:

```bash
poetry add git+https://github.com/emcie-co/pytest-stochastics.git
# or
poetry add git+ssh://git@github.com/emcie-co/pytest-stochastics.git
```

## Usage

### Configuration

Create a `pytest_stochastics_config.json` file in your project root with your test configuration:

```json
{
    "test_plans": [
        {
            "plan": "weak",
            "policy_tests": [
                {
                    "policy": "always",
                    "tests": [
                        "tests/test_abc/test_1", 
                    ]
                },
                {
                    "policy": "mostly",
                    "tests": [
                        "tests/test_abc/test_2",
                        "tests/test_abc/test_3"
                    ]
                }
            ]
        },
        {
            "plan": "strong",
            "policy_tests": [
                {
                    "policy": "always",
                    "tests": [
                        "tests/test_abc/test_2"
                    ]
                }
            ]
        }
    ],
    "policies": [
        {
            "policy": "always",
            "at_least": 3,
            "out_of": 3
        },
        {
            "policy": "mostly",
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

To specify a plan:

```bash
pytest --plan="name of plan"
```
