

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
    Values(
        1,
        1,
        1,
        'Location1',
        1000000,
        500000,
        0,
        'USD',
        'US',
        'USA',
        '01/01/2022',
        '12/31/2022',
        getdate(),
        getdate(),
        'TBC'
    )

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
    Values (
        1,
        1,
        1,
        1,
        'X',
        'X'
    )

/*
Select * From tExposureSet
Select * From tContract
Select * From tLocation
Select * From tLocTerm
*/

Select  ES.ExposureSetName,
        C.ContractID,
        L.LocationID,
        L.CountryCode,
        PS.PerilSet,
        L.ReplacementValueA,
        L.ReplacementValueC,
        L.ReplacementValueD,
        L.CurrencyCode
From    tLocation As L
Join    tContract As C on L.ContractSID = C.ContractSID
Join    tExposureSet As ES on L.ExposureSetSID = ES.ExposureSetSID
Join    tLocTerm As LT on L.LocationSID = LT.LocationSID
Join    AIRReference_CEDE..tPerilSet As PS on LT.PerilSetCode = PS.PerilSetCode



