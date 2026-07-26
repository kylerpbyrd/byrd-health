from data_service.migrations.versions import _001_initial_schema


def test_upgrade_downgrade_has_both():
    assert hasattr(_001_initial_schema, "upgrade")
    assert hasattr(_001_initial_schema, "downgrade")
    assert callable(_001_initial_schema.upgrade)
    assert callable(_001_initial_schema.downgrade)


def test_revision_identifiers():
    assert _001_initial_schema.revision == "001"
    assert _001_initial_schema.down_revision is None
