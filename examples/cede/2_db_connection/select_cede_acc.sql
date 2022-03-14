Select  ES.ExposureSetName,
        C.ContractID,
        C.CurrencyCode,
        L.LayerID,
        PS.PerilSet,
        L.AttachmentPoint,
        L.OccTotalLimit,
        L.OccParticipation
From    tContract As C
Join    tExposureSet As ES on C.ExposureSetSID = ES.ExposureSetSID
Join    tLayer as L on C.ContractSID = L.ContractSID
Join    AIRReference_CEDE..tPerilSet As PS on L.PerilSetCode = PS.PerilSetCode
