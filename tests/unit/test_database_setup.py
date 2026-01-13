import pytest

@pytest.mark.asyncio
async def test_configured_symbols_table_exists(test_db):
    """Test que la table configured_symbols existe"""
    cursor = await test_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='configured_symbols'"
    )
    result = await cursor.fetchone()
    assert result is not None
    assert result[0] == 'configured_symbols'

@pytest.mark.asyncio
async def test_taskexecutions_table_exists(test_db):
    """Test que la table taskexecutions existe"""
    cursor = await test_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='taskexecutions'"
    )
    result = await cursor.fetchone()
    assert result is not None
    assert result[0] == 'taskexecutions'
