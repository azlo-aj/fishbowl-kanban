def get_code():
        sql_code = """SELECT  WO.num AS WONum, WOITEM.TYPEID,  wostatus.name AS woStatus, 
        PART.NUM AS BOMITEMPART, PART.DESCRIPTION AS PARTDESCRIPTION, 
        COALESCE(BOMITEM.DESCRIPTION, '') AS BOMITEMDESCRIPTION, 
        (WOITEM.QTYTARGET / WO.QTYTARGET) AS WOITEMQTY, 
        WOITEM.QTYTARGET AS WOITEMTOTAL, MOITEM.DESCRIPTION AS ITEMNAME, 
        wo.qtyOrdered, WO.dateScheduled AS dateScheduledFulfillment,
        qtyonhand.qty AS invQTY, PART.CUSTOMFIELDS AS CSTMFLD, 
        WOITEM.ID AS BOMITEMID
        
FROM    wo
        INNER JOIN woitem ON wo.id = woitem.woid
        INNER JOIN moitem ON woitem.moitemid = moitem.id
        LEFT JOIN qtyonhand ON woitem.partId = qtyonhand.partid
        LEFT JOIN wostatus ON wostatus.id = wo.statusid
        LEFT JOIN bomitem ON moitem.bomitemid = bomitem.id
        LEFT JOIN part ON woitem.partid = part.id

WHERE   wo.dateScheduled BETWEEN $RANGE{Select_date_range|This week|Date}
        AND wostatus.name NOT LIKE 'FULFILLED'

ORDER BY COALESCE(moitem.sortidinstruct, 500), TYPEID ASC, BOMITEMPART DESC"""
        return sql_code