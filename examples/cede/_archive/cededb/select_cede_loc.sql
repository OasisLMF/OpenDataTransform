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
