from datetime import date, time, datetime
import unittest

from afis_app.constants import STATUS_CANCELADO, STATUS_FINALIZADO, STATUS_MONITORADO
from afis_app.services import AlertaService, TalaoService


class TalaoServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = TalaoService()

    def _base_form_data(self):
        return {
            "delegacia": "1 DP",
            "autoridade": "DELEGADO A",
            "solicitante": "UNIDADE B",
            "endereco": "RUA X, 123",
            "boletim": "",
            "natureza": "",
            "data_bo": "",
            "vitimas": "",
            "equipe": "",
            "operador": "OPERADOR 1",
            "observacao": "",
            "status": STATUS_MONITORADO,
        }

    def test_prepare_new_talao_sets_now_and_status(self):
        form_data = self._base_form_data()
        now = datetime(2026, 2, 23, 14, 35)

        normalized, missing, returned_now = self.service.prepare_new_talao(form_data, now=now)

        self.assertEqual([], missing)
        self.assertEqual(now, returned_now)
        self.assertEqual("2026-02-23", normalized["data_solic"])
        self.assertEqual("14:35", normalized["hora_solic"])
        self.assertEqual(STATUS_MONITORADO, normalized["status"])

    def test_prepare_update_talao_requires_fields_by_status(self):
        form_data = self._base_form_data()
        form_data["data_solic"] = "23/02/2026"
        form_data["hora_solic"] = "14:35"
        form_data["status"] = STATUS_CANCELADO

        _, missing = self.service.prepare_update_talao(form_data)

        self.assertIn("Observação", missing)

    def test_prepare_finalize_from_record_builds_valid_payload(self):
        record = {
            "delegacia": "1 DP",
            "autoridade": "DELEGADO A",
            "solicitante": "UNIDADE B",
            "endereco": "RUA X, 123",
            "boletim": "2026-1234",
            "natureza": "FURTO",
            "data_bo": date(2026, 2, 22),
            "vitimas": "JOAO",
            "equipe": "EQUIPE 1",
            "operador": "OPERADOR 1",
            "status": STATUS_MONITORADO,
            "observacao": "",
            "data_solic": date(2026, 2, 23),
            "hora_solic": time(14, 35),
        }

        normalized, missing = self.service.prepare_finalize_from_record(record)

        self.assertEqual([], missing)
        self.assertEqual("2026-02-23", normalized["data_solic"])
        self.assertEqual("14:35", normalized["hora_solic"])
        self.assertEqual("2026-02-22", normalized["data_bo"])
        self.assertEqual(STATUS_FINALIZADO, normalized["status"])


class AlertaServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = AlertaService()

    def test_is_edit_blocked_status(self):
        self.assertTrue(self.service.is_edit_blocked_status(STATUS_FINALIZADO))
        self.assertTrue(self.service.is_edit_blocked_status(STATUS_CANCELADO))
        self.assertFalse(self.service.is_edit_blocked_status(STATUS_MONITORADO))

    def test_is_monitorado_case_insensitive(self):
        self.assertTrue(self.service.is_monitorado("monitorado"))
        self.assertTrue(self.service.is_monitorado(" MONITORADO "))
        self.assertFalse(self.service.is_monitorado("cancelado"))

    def test_build_monitoring_question_formats_talao_and_boletim(self):
        text = self.service.build_monitoring_question(2026, 7, "")

        self.assertIn("0007/2026", text)
        self.assertIn("sem boletim", text)


if __name__ == "__main__":
    unittest.main()
