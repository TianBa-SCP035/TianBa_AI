"""
受试品信息查询SQL
包含受试品信息相关查询
"""

# 受试品信息查询（按 项目ID → LIKE 匹配 实验号）
SQL_SUPPLIES_INFO = """
SELECT
  /* —— 基本信息（统一做无效值归一化） —— */
  CASE
    WHEN rsp.NAME IS NULL
      OR TRIM(rsp.NAME) = ''
      OR TRIM(rsp.NAME) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.NAME
  END AS `名称`,
  CASE
    WHEN rsp.simplename IS NULL
      OR TRIM(rsp.simplename) = ''
      OR TRIM(rsp.simplename) IN ('0', 'NA', '/', '\\\\')
    THEN 
      CASE
        WHEN rsp.name IS NULL
          OR TRIM(rsp.name) = ''
          OR TRIM(rsp.name) IN ('0', 'NA', '/', '\\\\') THEN '-'
        ELSE rsp.name
      END
    ELSE rsp.simplename
  END AS `代号`,
  CASE
    WHEN rsp.suppliesType IS NULL
      OR TRIM(rsp.suppliesType) = ''
      OR TRIM(rsp.suppliesType) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.suppliesType
  END AS `来源`,
  CASE
    WHEN rsp.projectno IS NULL
      OR TRIM(rsp.projectno) = ''
      OR TRIM(rsp.projectno) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.projectno
  END AS `项目编号`,
  CASE
    WHEN rsp.testno IS NULL
      OR TRIM(rsp.testno) = ''
      OR TRIM(rsp.testno) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.testno
  END AS `实验号`,
  CASE
    WHEN rsp.properties IS NULL
      OR TRIM(rsp.properties) = ''
      OR TRIM(rsp.properties) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.properties
  END AS `性状`,
  /* 纯度：有效时加 %，否则 '-' */
  CASE
    WHEN rsp.purity IS NULL
      OR TRIM(rsp.purity) = ''
      OR TRIM(rsp.purity) IN ('0', 'NA', '/', '\\\\')
      OR rsp.purity = 0 THEN
      '-'
    ELSE
      CONCAT(rsp.purity, '%')
  END AS `纯度`,
  CASE
    WHEN rsp.lot_number IS NULL
      OR TRIM(rsp.lot_number) = ''
      OR TRIM(rsp.lot_number) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.lot_number
  END AS `批号`,
  CASE
    WHEN rsp.material_lot_number IS NULL
      OR TRIM(rsp.material_lot_number) = ''
      OR TRIM(rsp.material_lot_number) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.material_lot_number
  END AS `货号`,
  /* 规格：models/modelsunit 任一有效则拼接；都无效返回 '-' */
  CASE
    WHEN (
        rsp.models IS NULL
        OR TRIM(rsp.models) = ''
        OR TRIM(rsp.models) IN ('0', 'NA', '/', '\\\\')
      )
      AND (
        rsp.modelsunit IS NULL
        OR TRIM(rsp.modelsunit) = ''
        OR TRIM(rsp.modelsunit) IN ('0', 'NA', '/', '\\\\')
      ) THEN
      '-'
    ELSE
      CONCAT(
        CASE
          WHEN rsp.models IS NULL
            OR TRIM(rsp.models) = ''
            OR TRIM(rsp.models) IN ('0', 'NA', '/', '\\\\') THEN
            ''
          ELSE
            rsp.models
        END,
        CASE
          WHEN rsp.modelsunit IS NULL
            OR TRIM(rsp.modelsunit) = ''
            OR TRIM(rsp.modelsunit) IN ('0', 'NA', '/', '\\\\') THEN
            ''
          ELSE
            rsp.modelsunit
        END
      )
  END AS `规格`,
  /* 浓度：粉末 → '-'；否则拼 potency+unit（无效则 '-'） */
  CASE
    WHEN rsp.properties = '粉末' THEN
      '-'
    WHEN (
        rsp.potency IS NULL
        OR TRIM(rsp.potency) = ''
        OR TRIM(rsp.potency) IN ('0', 'NA', '/', '\\\\')
        OR rsp.potency = 0
      )
      AND (
        rsp.potencyunit IS NULL
        OR TRIM(rsp.potencyunit) = ''
        OR TRIM(rsp.potencyunit) IN ('0', 'NA', '/', '\\\\')
      ) THEN
      '-'
    WHEN rsp.potency IS NULL
      OR TRIM(rsp.potency) = ''
      OR TRIM(rsp.potency) IN ('0', 'NA', '/', '\\\\')
      OR rsp.potency = 0 THEN
      '-'
    ELSE
      CONCAT(rsp.potency, rsp.potencyunit)
  END AS `浓度`,
  /* —— 贮存条件：保存条件 +（可选）避光/干燥，用逗号拼；全无效时为 '-' —— */
  CASE
    WHEN (
        rsp.storagecondition IS NULL
        OR TRIM(rsp.storagecondition) = ''
        OR TRIM(rsp.storagecondition) IN ('0', 'NA', '/', '\\\\')
      )
      AND (
        rsp.issunblock IS NULL
        OR TRIM(rsp.issunblock) = ''
        OR TRIM(rsp.issunblock) IN ('0', '无要求', 'NA', '/', '\\\\')
      )
      AND (
        rsp.isdrystorage IS NULL
        OR TRIM(rsp.isdrystorage) = ''
        OR TRIM(rsp.isdrystorage) IN ('0', '无要求', 'NA', '/', '\\\\')
      ) THEN
      '-'
    ELSE
      CONCAT_WS(
        ', ',
        CASE
          WHEN rsp.storagecondition IS NULL
            OR TRIM(rsp.storagecondition) = ''
            OR TRIM(rsp.storagecondition) IN ('0', 'NA', '/', '\\\\') THEN
            NULL
          ELSE
            rsp.storagecondition
        END,
        CASE
          WHEN rsp.issunblock IS NULL
            OR TRIM(rsp.issunblock) = ''
            OR TRIM(rsp.issunblock) IN ('0', '无要求', 'NA', '/', '\\\\') THEN
            NULL
          ELSE
            '避光'
        END,
        CASE
          WHEN rsp.isdrystorage IS NULL
            OR TRIM(rsp.isdrystorage) = ''
            OR TRIM(rsp.isdrystorage) IN ('0', '无要求', 'NA', '/', '\\\\') THEN
            NULL
          ELSE
            '干燥'
        END
      )
  END AS `贮存条件`,
  CASE
    WHEN rsp.manufacturer IS NULL
      OR TRIM(rsp.manufacturer) = ''
      OR TRIM(rsp.manufacturer) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.manufacturer
  END AS `生产单位`,
  CASE
    WHEN rsp.customername IS NULL
      OR TRIM(rsp.customername) = ''
      OR TRIM(rsp.customername) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.customername
  END AS `供货单位`,
  CASE
    WHEN rsp.mfg IS NULL
      OR TRIM(rsp.mfg) = ''
      OR TRIM(rsp.mfg) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.mfg
  END AS `生产日期`,
  CASE
    WHEN rsp.validity IS NULL
      OR TRIM(rsp.validity) = ''
      OR TRIM(rsp.validity) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.validity
  END AS `有效期`,
  CASE
    WHEN rsp.sdname IS NULL
      OR TRIM(rsp.sdname) = ''
      OR TRIM(rsp.sdname) IN ('0', 'NA', '/', '\\\\') THEN
      '-'
    ELSE
      rsp.sdname
  END AS `SD`
FROM m_reagent_supplies rsp
WHERE
  rsp.testno   LIKE :full_like
  OR (
      rsp.projectno LIKE :prefix_like
      AND NOT EXISTS (
          SELECT 1 FROM m_reagent_supplies r2
          WHERE r2.testno LIKE :full_like
      )
  );
"""