

Delete From tLocTerm
Delete From tLocation
Delete From tContract
Delete From tExposureSet

--Exposure Set
Insert 
    Into tExposureSet (
        ExposureSetSID,
        ExposureSetName,
        StatusCode,
        EnteredDate,
        EditedDate
    )
    Values (
        1,
        'ExposureSet1',
        'TBC',
        getdate(),
        getdate()
    )

--Contract
Insert 
    Into tContract (
        ContractSID,
        ExposureSetSID,
        ContractID,
        ContractTypeCode,
        SubmitStatusCode,
        PerilSetCode,
        CurrencyCode,
        InceptionDate,
        ExpirationDate,
        StatusCode,
        EnteredDate,
        EditedDate
        )
    Values (
        1,
        1,
        'Contract1',
        'TBC',
        'TBC',
        1,
        'USD',
        '01/01/2022',
        '12/31/2022',
        'TBC',
        getdate(),
        getdate()
        )

--LOCATION
Insert 
    Into tLocation (
        LocationSID,
        ContractSID,
        ExposureSetSID,
        LocationID,
        Latitude,
        Longitude,
        AIROccupancyCode,
        AIRConstructionCodeA,
        ReplacementValueA,
        ReplacementValueC,
        ReplacementValueD,
        CurrencyCode,
        CountryCode,
        CountryName,
        InceptionDate,
        ExpirationDate,
        EnteredDate,
        EditedDate,
        StatusCode
        )
    Values
        (1,1,1,'Location1',40.760204,-73.984421,312,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (2,1,1,'Location2',34.134117,-118.321495,321,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (3,1,1,'Location3',36.103092,-115.172501,312,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'TBAC'),
        (4,1,1,'Location4',39.370121,-74.438942,312,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (5,1,1,'Location5',38.907852,-77.072807,321,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (6,1,1,'Location6',36.001465,-78.939133,312,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (7,1,1,'Location7',52.204311,0.113818,321,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (8,1,1,'Location8',41.316307,-72.922585,312,131,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (9,1,1,'Location9',53.815884,-3.055291,341,153,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A'),
        (10,1,1,'Location10',48.858093,2.294694,312,153,1000000,500000,0,'USD','US','USA','01/01/2022','12/31/2022',getdate(),getdate(),'A')

--LocTerm
Insert 
    Into tLocTerm (
        LocTermSID,
        LocationSID,
        ContractSID,
        PerilSetCode,
        LimitTypeCode,
        DeductibleTypeCode
    )
    Values 
        (1,1,1,1,'X','X'),
        (2,2,1,1,'X','X'),
        (3,3,1,1,'X','X'),
        (4,4,1,1,'X','X'),
        (5,5,1,1,'X','X'),
        (6,6,1,1,'X','X'),
        (7,7,1,1,'X','X'),
        (8,8,1,1,'X','X'),
        (9,9,1,1,'X','X'),
        (10,10,1,1,'X','X')


Insert 
    Into tLayer(
        LayerSID,
        ContractSID,
        LayerID,
        PerilSetCode,
        OccLimitTypeCode,
        OccTotalLimit,
        AttachmentPoint,
        OccParticipation,
        DeductibleTypeCode
    )
    Values (
        1,
        1,
        'Layer1',
        1,
        'X',
        20000000,
        10000000,
        0.5,
        'N'
    )

/*
Select * From tExposureSet
Select * From tContract
Select * From tLocation
Select * From tLocTerm
Select * From tLayer
*/


-- loc query
Select  ES.ExposureSetName,
        C.ContractID,
        L.LocationID,
        L.CountryCode,
        PS.PerilSet,
        L.ReplacementValueA,
        L.ReplacementValueC,
        L.ReplacementValueD,
        L.CurrencyCode,
        L.Latitude,
        L.Longitude,
        L.AIROccupancyCode,
        L.AIRConstructionCodeA
From    tLocation As L
Join    tContract As C on L.ContractSID = C.ContractSID
Join    tExposureSet As ES on L.ExposureSetSID = ES.ExposureSetSID
Join    tLocTerm As LT on L.LocationSID = LT.LocationSID
Join    AIRReference_CEDE..tPerilSet As PS on LT.PerilSetCode = PS.PerilSetCode

-- acc query
Select  ES.ExposureSetName,
        C.ContractID,
        C.CurrencyCode,
        L.LayerID,
        PS.PerilSet
From    tContract As C
Join    tExposureSet As ES on C.ExposureSetSID = ES.ExposureSetSID
Join    tLayer as L on C.ContractSID = L.ContractSID
Join    AIRReference_CEDE..tPerilSet As PS on L.PerilSetCode = PS.PerilSetCode



