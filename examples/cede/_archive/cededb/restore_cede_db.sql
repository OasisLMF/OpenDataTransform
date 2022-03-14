RESTORE FILELISTONLY
    FROM DISK = '/tmp/cede-9-sample-database/AIRExposure_CEDE.bak'

RESTORE DATABASE AIRExposure_CEDE
    FROM DISK = '/tmp/cede-9-sample-database/AIRExposure_CEDE.bak'
    WITH
        MOVE 'AIRExposure_CEDE' TO '/var/opt/mssql/data/AIRExposure_CEDE_8.0_Test1.mdf',
        MOVE 'AIRExposure_CEDE_log' TO '/var/opt/mssql/data/AIRExposure_CEDE_8.0_Test1.ldf'

RESTORE FILELISTONLY
    FROM DISK = '/tmp/cede-9-sample-database/AIRReference_CEDE.bak'

RESTORE DATABASE AIRReference_CEDE
    FROM DISK = '/tmp/cede-9-sample-database/AIRReference_CEDE.bak'
    WITH
        MOVE 'AIRReference' TO '/var/opt/mssql/data/AIRReference_CEDE.mdf',
        MOVE 'AIRReference_log' TO '/var/opt/mssql/data/AIRReference_CEDE.ldf'

