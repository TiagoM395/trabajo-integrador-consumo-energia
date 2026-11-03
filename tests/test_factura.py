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


# Misma estructura que la boleta de EDEA (números inventados que cierran las sumas).
BOLETA_EDEA = """
Estado anterior al 06/07/2026: 1000
Estado actual al 04/09/2026: 1400
Consumo: 400 R
Total a Facturar: 400
533
kWh
3/26
410
kWh
4/26
PERIODO: 05/26 CUOTA 1 de 2
FECHA VENCIMIENTO: 02/10/2026
CONSUMOS ENTRE:
06/07/2026 Y 04/09/2026
TOTAL A PAGAR: $*****71.786,82
FECHA C. FIJO C. VARIABLE KWH DIAS
07/07/26 8464,300 125,2182 120 25
01/08/26 8670,580 127,5641 80 35
C.F +ENERGIA SIN SUBSIDIO 57.695,40
CARGO FIJO RESIDENCIAL 8.795,20
CARGO VARIABLE RESIDENC. 200,00 45.399,00
CTT 200,00 3.501,20
*SUBSIDIO ESTADO NACIONAL -10.000,00
* SUBTOTAL COSTO ENERGIA 47.695,40
IVA CONSUMIDOR FINAL    % 21,00 10.016,03
LEY 10740 8.585,17
LEY 11769 ART 74        % 0,001 0,48
LEY 11769 ART 75        % 6,00 2.861,72
LEY 11769 FDO. COMP.    % 5,50 2.623,25
LEY PROV. 7290          % 0,01 4,77
LEY PROV. 9038          % 0,00 0,00
* SUBTOTAL IMPUESTOS 24.091,42
TOTAL FACTURA 71.786,82
SEGMENTACION N3/SEF -Subsidio Estado Nacional $ 10000.00
Usted puede consultar por su inclusion en la Tarifa Social en la pagina web
Esta factura se emite con el cuadro tarifario Res. MyP 682/26
"""


class TestBoletaEdea(unittest.TestCase):
    def setUp(self):
        self.d = F.extraer(BOLETA_EDEA)

    def test_consumo_no_sale_del_grafico(self):
        self.assertEqual((self.d["kwh"], self.d["kwh_conf"]), (400, "alta"))

    def test_consumo_por_estados_del_medidor(self):
        d = F.extraer("Estado anterior al 01/01/2026: 1000\nEstado actual al 01/03/2026: 1250\n533\nkWh\n")
        self.assertEqual((d["kwh"], d["kwh_conf"]), (250, "media"))

    def test_segmentacion(self):
        self.assertEqual((self.d["escenario"], self.d["escenario_conf"]), ("sef", "alta"))
        n1 = BOLETA_EDEA.replace("N3/SEF", "N1/NO SEF")
        self.assertEqual(F.extraer(n1)["escenario"], "sin_subsidio")

    def test_cuota_y_cuadro(self):
        self.assertEqual(self.d["cuotas"], 2)
        self.assertEqual(self.d["dias"], 60)
        self.assertIn("682/26", self.d["cuadro"])

    def test_conceptos(self):
        c = self.d["conceptos"]
        self.assertEqual([x["concepto"] for x in c["cargos"]],
                         ["CARGO FIJO RESIDENCIAL", "CARGO VARIABLE RESIDENC", "CTT", "SUBSIDIO ESTADO NACIONAL"])
        self.assertEqual(c["cargos"][1]["kwh"], 200)
        self.assertAlmostEqual(c["cargos"][3]["monto"], -10000)
        self.assertAlmostEqual(c["subtotal"], 47695.40)
        ley = next(i for i in c["impuestos"] if i["concepto"] == "LEY 10740")
        self.assertAlmostEqual(ley["monto"], 8585.17)
        self.assertEqual(next(i for i in c["impuestos"] if "ART 75" in i["concepto"])["pct"], 6)
        self.assertAlmostEqual(c["total_factura"], 71786.82)

    def test_historial_y_tarifas(self):
        self.assertEqual(self.d["historial"], [{"periodo": "3/26", "kwh": 533}, {"periodo": "4/26", "kwh": 410}])
        self.assertEqual(len(self.d["tarifas"]), 2)
        self.assertEqual((self.d["tarifas"][0]["cf"], self.d["tarifas"][0]["kwh"]), (8464.3, 120))

    def test_conceptos_que_no_cierran(self):
        self.assertIsNone(F.conceptos(BOLETA_EDEA.replace("CTT 200,00 3.501,20", "CTT 200,00 3.901,20")))


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
        self.assertEqual(d["avisos"], [])  # el período bimestral es lo normal: no es un aviso
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
