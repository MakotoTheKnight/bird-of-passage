from db import DatabaseConnection


def test_database_connection_initialization():
    # given - initial, empty database
    db_name = ":memory:"
    # when
    database = DatabaseConnection(db_name)
    # then
    # get the cursor to find the table _yoyo_migration.
    cursor = database.db.cursor()
    result = cursor.execute("select * from _yoyo_migration where migration_id = '0001_create_initial_schema'")
    actual = result.fetchall()
    assert actual is not False