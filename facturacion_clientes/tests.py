from django.test import LiveServerTestCase
from django.urls import resolve
import pytest
from .views import importar_resumen_bancario
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class TestsUI(LiveServerTestCase):
    
    def setUp(self):  
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)

    def tearDown(self):  
        self.browser.quit()

    def test_resuelve_url_importacion_resumen_bancario(self):
        found = resolve('/importar_resumen_bancario/')
        self.assertEqual(found.func, importar_resumen_bancario)

    @pytest.mark.xfail
    def test_importar_resumen_bancario(self):
        
        self.browser.get('http://localhost:8000/importar_resument_bancario')

        assert 'Importar resumen bancario' in self.browser.title