from behave import fixture, use_fixture
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def before_all(context):
    context.fixtures = ['datos_iniciales.yaml']

@fixture
def browser(context, timeout=30, **kwargs):
    options = Options()
    options.headless = True
    context.browser = webdriver.Firefox(options=options)
    context.add_cleanup(context.browser.quit)
    return context.browser

def before_tag(context, tag):
    if tag == "fixture.browser":
        use_fixture(browser, context, timeout=10)