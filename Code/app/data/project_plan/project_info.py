"""
项目信息查询SQL
包含项目基础信息查询
"""

# 项目信息查询（按项目编号前缀）
SQL_PROJECT_INFO = """
SELECT
    p.id AS `项目ID`, 
    LEFT(p.snum, LENGTH(p.snum) - 2) AS `项目编号`,
    p.snum AS `实验编号`, 
    p.sname AS `项目名称`,
    CASE 
        WHEN ppe.project_purpose IS NULL 
             OR CHAR_LENGTH(TRIM(ppe.project_purpose)) < 3 
        THEN p.sname 
        ELSE ppe.project_purpose
    END AS `项目目的`,
    oe.sname AS `负责人`, 
    oe.email AS `负责人邮箱`,
    oe_in.sname AS `体内实验负责人`,
    p.customer_name AS `客户名称`,
    up.entrust_people AS `委托单位负责人`,
    DATE_FORMAT(p.start_date, '%Y年%m月%d日') AS `开始日期`,
    DATE_FORMAT(p.end_date, '%Y年%m月%d日') AS `结束日期`,
    c.cell_names AS `细胞名称`,           
    an.sname AS `动物名称`, 
    st.sname AS `动物品系`, 
    CASE 
        WHEN pea.mouse_age IS NOT NULL AND pea.mouse_age <> 0 
            THEN pea.mouse_age
        ELSE CONCAT(pea.rat_age_low, '-', pea.rat_age_top, '周')
    END AS `鼠龄`,
    wt.sname AS `体重范围`, 
    CASE pea.sex
        WHEN 0 THEN '雌鼠'
        WHEN 1 THEN '雄鼠'
        ELSE '未知'
    END AS `性别`,
    pea.order_number AS `订购数量`, 
    ppe.group_number AS `入组数量`,
    ppe.groups AS `组数`,
    ppe.animal_number AS `每组数量`,
    ppe.group_condition AS `分组条件`
FROM project p
LEFT JOIN project_entry_effect_animal pea
    ON p.id = pea.project_id
LEFT JOIN org_tag AS an
    ON pea.animal_name = an.id
LEFT JOIN org_tag AS st
    ON pea.animal_strain = st.id
LEFT JOIN org_tag AS wt
    ON pea.weight_range = wt.id
LEFT JOIN united_project up
    ON p.snum LIKE CONCAT('%', up.snum, '%')
LEFT JOIN org_emp oe
    ON up.sd = oe.id
LEFT JOIN project_entry_pharmacological_effect ppe
    ON p.id = ppe.project_id
-- 细胞名称聚合（不影响主查询分组）
LEFT JOIN (
    SELECT
        pec.project_id,
        GROUP_CONCAT(DISTINCT oc.sname ORDER BY oc.sname SEPARATOR ',') AS cell_names
    FROM project_entry_effect_cell AS pec
    JOIN target_tag AS tt
        ON tt.project_effect_cell_id = pec.id
    JOIN org_tag AS oc
        ON oc.id = tt.tag_id
       AND oc.tag_type = 94
    GROUP BY pec.project_id
) AS c
    ON c.project_id = p.id
-- 体内实验负责人：每项目取 project_member 中 role=2524 的最新一条
LEFT JOIN (
    SELECT project_id, MAX(id) AS max_pm_id
    FROM project_member
    WHERE project_role = 2524
    GROUP BY project_id
) pm_last
    ON pm_last.project_id = p.id
LEFT JOIN project_member pm_in
    ON pm_in.id = pm_last.max_pm_id
LEFT JOIN org_emp oe_in
    ON oe_in.id = pm_in.rele_id
WHERE p.snum LIKE CONCAT(:project_code, '%');
"""