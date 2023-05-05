from django.test import SimpleTestCase
from app import calc

class calcTest(SimpleTestCase):
    
    def teste_sum(self):
        res = calc.sum(3,4)

        self.assertEqual(res,7)

    def teste_division(self):
        res = calc.divison(10,2)

        self.assertEqual(res,5)