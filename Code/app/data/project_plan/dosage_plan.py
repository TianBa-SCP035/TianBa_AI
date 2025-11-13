"""
给药方案查询SQL
包含给药方案相关查询
"""

# 给药方案查询（按项目ID）
SQL_DOSAGE_PLAN = """
SELECT
  p.group_category     AS `组别`,
  p.treatment_method   AS `受试品`,
  p.animals_number     AS `动物只数`,
  p.dose               AS `剂量`,
  (
    SELECT GROUP_CONCAT(
             rt.sname
             ORDER BY FIND_IN_SET(
               rt.id,
               REPLACE(REPLACE(REPLACE(COALESCE(p.dose_mode, ''), '[',''),']',''), ' ', '')
             )
             SEPARATOR ' + '
           )
    FROM org_tag rt
    WHERE FIND_IN_SET(
            rt.id,
            REPLACE(REPLACE(REPLACE(COALESCE(p.dose_mode, ''), '[',''),']',''), ' ', '')
          ) > 0
  ) AS `给药途径`,
  (
    SELECT GROUP_CONCAT(
             fr.sname
             ORDER BY FIND_IN_SET(
               fr.id,
               REPLACE(REPLACE(REPLACE(COALESCE(p.dose_frequency, ''), '[',''),']',''), ' ', '')
             )
             SEPARATOR ' + '
           )
    FROM org_tag fr
    WHERE FIND_IN_SET(
            fr.id,
            REPLACE(REPLACE(REPLACE(COALESCE(p.dose_frequency, ''), '[',''),']',''), ' ', '')
          ) > 0
  ) AS `给药频率`,
  p.dose_times         AS `给药次数`
FROM project_entry_effect_drug p
WHERE p.project_id = :project_id
ORDER BY p.group_category, p.treatment_method;
"""