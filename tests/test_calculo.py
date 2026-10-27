"""Pruebas del motor de cálculo. Ejecutar con: python -m pytest  (o python -m unittest)"""
import unittest

from simulador import calculo as C


class TestSimulador(unittest.TestCase):
    def test_ejemplo_5_2_cuatro_artefactos(self):
        perfil = C.datos()["PERFILES"]["ejemplo"]
        # Solo los 4 artefactos del ejemplo 5.2 (el perfil suma además un cargador de celular).
        items = [C.instancia(i, **o) for i, o in perfil["items"] if i != "cargador"]
        r = C.simular({"items": items, "base_w": perfil["base_w"]})
        self.assertAlmostEqual(r["meses"][0]["total"], 296.4, delta=0.05)   # enero
        self.assertAlmostEqual(r["meses"][5]["total"], 137.0, delta=0.05)   # junio
        self.assertAlmostEqual(r["anual"], 2392.1, delta=0.05)
        anual = {it["id"]: it["anual"] for it in r["items"]}
        self.assertAlmostEqual(anual["heladera"], 350, places=3)
        self.assertAlmostEqual(anual["aire"], 696, places=3)
        self.assertAlmostEqual(anual["tv"], 146, places=3)
        self.assertAlmostEqual(anual["termotanque"], 1095, places=3)

    def test_ejemplo_6_3_tres_escenarios(self):
        t = C.datos()["TARIFAS"]
        self.assertAlmostEqual(C.factura(400, t, "sin_subsidio")["total"], 78650, delta=0.5)
        self.assertAlmostEqual(C.factura(400, t, "social_nacional")["total"], 53240, delta=0.5)
        self.assertAlmostEqual(C.factura(400, t, "social_provincial")["total"], 45617, delta=0.5)
        f = C.factura(400, t, "social_nacional")
        self.assertEqual((f["dentro"], f["fuera"]), (350, 50))

    def test_activo_y_pasivo_tv(self):
        d = C.diaria(C.instancia("tv", potencia_w=80, conectado=8, uso=5, standby_w=3))  # ejemplo 4.3 de la propuesta
        self.assertAlmostEqual(d["act"] * 30, 12.0, places=6)
        self.assertAlmostEqual(d["pas"] * 30, 0.27, places=6)

    def test_subsidio_no_cambia_kwh(self):
        items = [C.instancia("heladera"), C.instancia("aire")]
        r = C.simular({"items": items, "base_w": 10})
        kwh = [m["total"] for m in r["meses"]]
        for esc in r["costos"]:
            self.assertEqual([f["kwh"] for f in r["costos"][esc]["porMes"]], kwh)

    def test_tope_mensual_no_anual(self):
        # 12 meses de 400 kWh: el excedente se paga cada mes, no una sola vez al año
        t = C.datos()["TARIFAS"]
        anual = sum(C.factura(400, t, "social_nacional")["total"] for _ in range(12))
        self.assertAlmostEqual(anual, 53240 * 12, delta=1)

    def test_curva_horaria_suma_igual_que_mensual(self):
        for c in C.datos()["CATALOGO"]:
            inst = C.instancia(c["id"])
            for m in (0, 6):
                dia = sum(C.horaria(inst, m))
                self.assertAlmostEqual(dia * C.DIAS_MES[m], C.mensual(inst)[m]["total"], places=6, msg=c["id"])

    # ---- Cuadro real de EDEA (Res. MIySP 682/2026, consumos desde 1/9/2026) ----

    def test_edea_sin_subsidio_273_kwh(self):
        # Tramo R3 (200 < kWh ≤ 400): cargo fijo 8.795,20 + 273 × (226,995 + CTT 17,506), + 36,501 % de impuestos
        subtotal = 8795.20 + 273 * 226.995 + 273 * 17.506
        f = C.factura(273, C.tarifas_edea(), "sin_subsidio")
        self.assertEqual(f["tramo"], "R3")
        self.assertAlmostEqual(f["total"], subtotal * 1.36501, delta=0.01)

    def test_edea_sef_bloque_150(self):
        # Primeros 150 kWh a 142,9395 (+ CTT 7,445); los 123 restantes a 226,995 (+ CTT 17,506)
        subtotal = 8795.20 + 150 * (142.9395 + 7.445) + 123 * (226.995 + 17.506)
        f = C.factura(273, C.tarifas_edea(), "sef")
        self.assertAlmostEqual(f["total"], subtotal * 1.36501, delta=0.01)
        self.assertEqual((f["dentro"], f["fuera"]), (150, 123))

    def test_edea_tarifa_social(self):
        # R3: primeros 150 a 195,1135 y el resto a 226,995; CTT 2,987; bonificación 8.000; impuestos 32,511 %
        subtotal = 8795.20 + 150 * 195.1135 + 123 * 226.995 + 273 * 2.987 - 8000
        f = C.factura(273, C.tarifas_edea(), "tarifa_social")
        self.assertAlmostEqual(f["total"], subtotal * 1.32511, delta=0.01)

    def test_edea_tramo_r1(self):
        subtotal = 4184.62 + 80 * (211.103 + 17.506)
        f = C.factura(80, C.tarifas_edea(), "sin_subsidio")
        self.assertEqual(f["tramo"], "R1")
        self.assertAlmostEqual(f["total"], subtotal * 1.36501, delta=0.01)

    def test_edea_subsidios_pagan_menos(self):
        t = C.tarifas_edea()
        for kwh in (50, 150, 273, 450, 900):
            sin = C.factura(kwh, t, "sin_subsidio")["total"]
            for esc in ("sef", "tarifa_social", "tarifa_social_sef"):
                self.assertLess(C.factura(kwh, t, esc)["total"], sin, f"{esc} {kwh}")

    # ---- Mi casa: precio fijo por kWh, cards independientes y total = suma de las cards ----

    def test_precio_fijo(self):
        t = C.tarifas_edea()
        # Sin subsidio: casa de referencia de 300 kWh (R3) → (226,995 + 17,506) × 1,36501
        p = C.precio_kwh(t, "sin_subsidio")
        self.assertEqual(p["tramo"], "R3")
        self.assertAlmostEqual(p["precio"], 333.75, delta=0.01)
        self.assertAlmostEqual(p["cargo_fijo"], 8795.20 * 1.36501, delta=0.01)
        # SEF: 150 kWh subsidiados + 150 a precio pleno, con su CTT, promediados
        sef = (150 * (142.9395 + 7.445) + 150 * (226.995 + 17.506)) / 300 * 1.36501
        self.assertAlmostEqual(C.precio_kwh(t, "sef")["precio"], sef, delta=0.01)
        # Tarifa social: el cargo fijo va neto del descuento fijo
        self.assertAlmostEqual(C.precio_kwh(t, "tarifa_social")["cargo_fijo"], (8795.20 - 8000) * 1.32511, delta=0.01)
        # Con subsidio, cada kWh sale más barato
        for esc in ("sef", "tarifa_social", "tarifa_social_sef"):
            self.assertLess(C.precio_kwh(t, esc)["precio"], p["precio"])

    def test_cards_independientes_y_total_suma(self):
        """Cambiar un equipo no cambia la plata de los demás, aunque la casa cambie de tramo,
        y el total sube exactamente lo que sube ese equipo."""
        t = C.tarifas_edea()
        perfil = C.datos()["PERFILES"]["familia"]
        items = [C.instancia(i, **o) for i, o in perfil["items"]]
        for it in items:
            it["estacion"] = "todo"

        def foto():
            r = C.simular({"items": items, "base_w": perfil["base_w"], "tarifas": t})
            p = C.precio_kwh(t, "sin_subsidio")["precio"]
            kwh = r["meses"][3]["total"]
            return ([x["meses"][3]["total"] * p for x in r["items"]], C.costo_casa(kwh, t, "sin_subsidio")["total"],
                    C.factura(kwh, t, "sin_subsidio")["tramo"])

        cal = next(k for k, it in enumerate(items) if it["id"] == "calefactor")
        antes, total_antes, tramo_antes = foto()
        items[cal]["uso"] = items[cal]["conectado"] = 0.5   # la casa baja de 824 a ~674 kWh: de R6 a R5
        despues, total_despues, tramo_despues = foto()
        self.assertNotEqual(tramo_antes, tramo_despues)
        for k, (a, b) in enumerate(zip(antes, despues)):
            if k != cal:
                self.assertAlmostEqual(a, b, places=6)
        self.assertAlmostEqual(total_antes - total_despues, antes[cal] - despues[cal], places=6)

    def test_validacion(self):
        self.assertTrue(C.validar(C.instancia("tv", conectado=3, uso=5)))
        self.assertTrue(C.validar(C.instancia("tv", cantidad=0)))
        self.assertEqual(C.validar(C.instancia("tv")), [])

    def test_catalogo_completo_y_valido(self):
        for c in C.datos()["CATALOGO"]:
            self.assertEqual(C.validar(C.instancia(c["id"])), [], c["id"])


if __name__ == "__main__":
    unittest.main()
