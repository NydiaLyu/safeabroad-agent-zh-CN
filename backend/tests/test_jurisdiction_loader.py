from backend.services.jurisdiction_service import JurisdictionService


def test_load_au_nsw_jurisdiction_pack():
    pack = JurisdictionService().load("AU-NSW")
    assert pack["id"] == "AU-NSW"
    assert pack["emergency"]["emergency_number"] == "000"

