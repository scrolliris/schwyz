def test_vars():
    """
    Returns env var names to update in testing

    These values are updated with values prefixed as `TEST_`.
    See .env.sample.
    """
    return [
        'ENV',
        'WSGI_URL_SCHEME',
        'VIEW_TYPE',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GCP_ACCOUNT_CREDENTIALS',
        'DYNAMODB_ENDPOINT_URL',
        'DYNAMODB_REGION_NAME',
        'DYNAMODB_TABLE_NAME',
        'DATASTORE_EMULATOR_HOST',
        'DATASTORE_ENTITY_KIND',
    ]
