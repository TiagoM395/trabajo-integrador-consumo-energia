"""Pruebas de la extracción de datos de la factura (texto de ejemplo, sin datos reales)."""
import datetime as dt
import unittest

from simulador import factura as F

EJEMPLO = """
DISTRIBUIDORA DE ENERGIA - FACTURA B
Titular: XXXXX  Domicilio: XXXXX
Período de consumo: 01/08/2026 al 30/09/2026
Lectura actual 15.432   Lectura anterior 15.112
Consumo del período 320 kWh
Cargo variable 320 kWh x $ 150,00/kWh
Total a pagar $ 63.250,40
Vencimiento: 15/10/2026
"""


class TestFactura(unittest.TestCase):
    def test_numero_argentino(self):
        self.assertEqual(F.numero_ar("1.234,56"), 1234.56)
        self.assertEqual(F.numero_ar("320"), 320)
        self.assertEqual(F.numero_ar("15.432"), 15432)

    def test_extrae_campos(self):
        d = F.extraer(EJEMPLO)
        self.assertEqual(d["kwh"], 320)
        self.assertEqual(d["kwh_conf"], "alta")
        self.assertEqual((d["desde"], d["hasta"]), (dt.date(2026, 8, 1), dt.date(2026, 9, 30)))
        self.assertEqual(d["dias"], 60)
        self.assertAlmostEqual(d["importe"], 63250.40)
        self.assertEqual(d["vencimiento"], dt.date(2026, 10, 15))
        self.assertTrue(any("bimestral" in a for a in d["avisos"]))
        self.assertEqual(F.mes_del_periodo(d["desde"], d["hasta"]), 7)  # agosto

    def test_lecturas_si_no_hay_consumo(self):
        d = F.extraer("Lectura actual 1200\nLectura anterior 1000\n")
        self.assertEqual((d["kwh"], d["kwh_conf"]), (200, "media"))

    def test_no_confunde_precio_con_consumo(self):
        d = F.extraer("Precio 150,00 $/kWh\n")
        self.assertIsNone(d["kwh"])

    def test_subsidio(self):
        self.assertEqual(F.extraer("Tarifa: T1 Residencial - Tarifa Social")["escenario"], "tarifa_social")
        self.assertEqual(F.extraer("Segmentacion: Nivel 2")["escenario"], "sef")
        self.assertIsNone(F.extraer("Residencial T1-R3")["escenario"])

    def test_importe_del_qr(self):
        import base64, json
        p = base64.b64encode(json.dumps({"fecha": "2026-10-01", "importe": 1500.5, "nroDocRec": 1}).encode()).decode()
        d = F.extraer("Total a pagar $ 1.500,50", [{"formato": "QRCode", "texto": "https://www.afip.gob.ar/fe/qr/?p=" + p}])
        self.assertEqual((d["importe"], d["importe_conf"]), (1500.5, "alta"))
        self.assertEqual(d["codigos"], ["QRCode"])  # el texto del código (con datos personales) no se guarda


if __name__ == "__main__":
    unittest.main()
