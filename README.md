# Automation Framework to test API requests using pytest

## Description:

Basic pytest API testing framework. Framework displays how to test different http requests
and scenarios utilising https://simple-books-api.glitch.me as a testing sandbox.

Framework utilises functionality of the Allure reporter. Reports are stored and displayed via GitHub Pages.
Also, there is an integrated Slack notification when GitHub Actions runs. 

### 1. Install environment:
```
  python -m pip install --upgrade pip
  pip install pipenv
  pipenv install --system
```

### 2. Run playwright tests:
Run all set of tests:
```
pytest
```
Run one particular test:
```
pytest -k <name of the test>
```

### 3. Generate allure report:
Test report is generated automatically after each test run overriding the previous report. 
Use this command to see the report:
```
allure serve reports
```
