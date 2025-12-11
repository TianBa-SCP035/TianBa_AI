# -*- coding: utf-8 -*-
import platform, subprocess, tempfile, os, shutil, json

# 如为 Windows，请修改为你本机 Rscript 路径；非 Windows 使用 PATH 中的 Rscript
RSCRIPT_WIN = r"D:\R-4.5.1\R-4.5.1\bin\Rscript.exe"

R_CODE = r'''
args <- commandArgs(trailingOnly=TRUE)
control <- if (length(args)>=1) args[1] else "G1"

# 设置固定随机种子确保结果可重现
set.seed(5)

# 需要的包
if (!requireNamespace("multcomp", quietly=TRUE)) install.packages("multcomp", repos="https://cloud.r-project.org")
if (!requireNamespace("jsonlite", quietly=TRUE)) install.packages("jsonlite",  repos="https://cloud.r-project.org")
if (!requireNamespace("mvtnorm",  quietly=TRUE)) install.packages("mvtnorm",  repos="https://cloud.r-project.org")

suppressPackageStartupMessages(library(multcomp))
suppressPackageStartupMessages(library(jsonlite))
# mvtnorm 不一定要 library()，但为了显式可读性也可加载
suppressPackageStartupMessages(library(mvtnorm))

# 与 Prism 对齐的对比编码（ treatment 对照编码 ）
options(contrasts=c("contr.treatment","contr.poly"))

# 从 stdin 读入 JSON 行表
# 预期格式： [{"group":"G1","volume":22.9}, ...]
df <- jsonlite::fromJSON(paste(readLines("stdin", warn=FALSE), collapse=""))

# 类型与水平顺序（把对照放到第一个水平，其余按字母数字排序，确保稳定）
df$group  <- factor(df$group)
df$volume <- as.numeric(df$volume)
# 如果指定的对照组不存在，使用第一组
if (!(control %in% levels(df$group))) control <- levels(df$group)[1]
df$group  <- factor(df$group, levels=c(control, sort(setdiff(levels(df$group), control))))

# 与 Prism 展示规则近似的小数与边界格式
fmt_p <- function(x){
  if (is.na(x)) return(NA_character_)
  if (x < 1e-4) "<0.0001" else if (x > 0.9999) ">0.9999" else sprintf("%.4f", round(x, 4))
}

# 一元等方差 ANOVA（Prism 的 Dunnett 基于 pooled MSE，而非 Welch）
fit <- aov(volume ~ group, data=df, na.action=na.omit)

# Dunnett 同时比较（双侧），家庭误差率 single-step 校正
# 使用确定性的 Miwa 算法（无随机、与 Prism 行为一致）
gh <- glht(fit, linfct=mcp(group="Dunnett"), alternative="two.sided")
sm <- summary(
  gh,
  test      = adjusted("single-step"),  # Dunnett 同时校正
  algorithm = mvtnorm::Miwa()           # 确定性积分，结果固定
)

# Prism 报告的是校正后的 p 值
p_adj <- as.numeric(sm$test$pvalues)

# 显著性星标（可按需调整）
stars <- ifelse(p_adj < 0.0001, "****",
         ifelse(p_adj < 0.001,  "***",
         ifelse(p_adj < 0.01,  "**",
         ifelse(p_adj < 0.05,  "*", "ns"))))

# 提取对比名中的“处理组名”（如 "G3 - G1 == 0" -> "G3"）
gi <- sub(" -.*$", "", sub(" ==.*$", "", rownames(sm$linfct)))

out <- data.frame(
  group     = gi,
  Summary   = stars,
  `P-Value` = vapply(p_adj, fmt_p, character(1)),
  check.names = FALSE
)

# 若组名包含数字，可按数字排序；否则可注释掉这一行改为原有顺序
out <- out[order(as.integer(sub("^\\D+","", out$group))), , drop=FALSE]

cat(jsonlite::toJSON(out, dataframe="rows", auto_unbox=TRUE, rownames=FALSE))
'''

def _pick_rscript():
    if platform.system() == "Windows":
        if os.path.isfile(RSCRIPT_WIN):
            return RSCRIPT_WIN
        raise FileNotFoundError(f"未找到 Rscript：{RSCRIPT_WIN}")
    r = shutil.which("Rscript")
    if not r:
        raise FileNotFoundError("PATH 中未找到 Rscript")
    return r

def calculate_dunnett_json(json_rows: str, control="G1"):
    """输入：长表 JSON，如 '[{"group":"G1","volume":22.9}, ...]'；输出：list[dict] 三列结果（group/Summary/P-Value）"""
    rscript = _pick_rscript()
    with tempfile.NamedTemporaryFile('w', suffix='.R', delete=False, encoding='utf-8') as fR:
        fR.write(R_CODE); r_file = fR.name
    try:
        proc = subprocess.run([rscript, r_file, control], input=json_rows,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "Rscript 执行失败（无错误信息）")
        return json.loads(proc.stdout)
    finally:
        try: os.remove(r_file)
        except OSError: pass

def format_result_table(results, control="G1"):
    """将结果格式化为简洁表格打印"""
    if not results:
        print("无结果"); return
    print(f"{control} vs group  Summary  P-Value")
    print("-" * 32)
    for r in results:
        print(f"{control} vs {r['group']:4}  {r['Summary']:7}  {r['P-Value']}")

# ===== 示例 =====
if __name__ == "__main__":
    # 示例数据（长表 JSON 输入）
    data = {
    "G1":  [898, 491, 642, 873, 1047],
    "G3":  [853, 1811, 1280, 703, 554],
    "G4":  [482, 752, 962, 831, 1450],
    "G5":  [527, 445, 1235, 1002, 1698],
    "G6":  [1482, 1703, 864, 1333, 1562],
    "G8":  [61, 217, 0, 0, 430],
    "G9":  [0, 121, 0, 90, 0],
    "G10": [1013, 623, 576, 486, 853],
    "G11": [711, 299, 543, 256, 461],
    }
    rows = [{"group": g, "volume": float(v)} for g, arr in data.items() for v in arr]
    payload = json.dumps(rows, ensure_ascii=False)

    result = calculate_dunnett_json(payload, control="G1")
    format_result_table(result, control="G1")
