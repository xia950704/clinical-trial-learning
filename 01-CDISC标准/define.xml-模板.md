---
tags: [CDISC, define.xml, 临床试验, 数据标准, FDA提交, 元数据]
status: active
created: 2026-06-25
updated: 2026-06-25
vault_link: 01-CDISC标准/define.xml-模板.md
---

# define.xml 模板 — CDISC 元数据定义文件

> 临床试验数据提交的元数据核心：描述每个数据集和变量的来源、类型、标签

---

## 一、什么是 define.xml？

**define.xml** 是 CDISC 标准中描述 SDTM/ADaM 数据集元数据的 XML 文件，是 FDA/EMA 数据提交的**必需文件**。

| 用途 | 说明 |
|------|------|
| **FDA/EMA 提交** | 与 SDTM/ADaM 数据集一起提交，描述数据结构和变量定义 |
| **变量追溯** | 每个变量标注来源（原始数据 → SDTM → ADaM） |
| **审核辅助** | 监管机构通过 define.xml 理解数据含义和衍生逻辑 |
| **数据复用** | 后续分析、荟萃分析时可快速理解数据结构 |

### 1.1 版本演进

| 版本 | 发布时间 | 说明 |
|------|---------|------|
| define.xml 2.0 | 2009 | 初始版本，仅支持 SDTM |
| define.xml 2.1 | 2011 | 增加 ADaM 支持 |
| define.xml 3.0 | 2017 | 重大更新，支持复杂元数据 |
| define.xml 3.1 | 2020 | 当前主流版本（FDA 推荐） |

> ⚠️ **FDA 当前要求**：2024 年起，FDA 要求使用 define.xml 3.1 版本提交。

---

## 二、define.xml 结构详解

### 2.1 整体结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DefineXML xmlns="http://www.cdisc.org/ns/def/v31" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           version="3.1">
  
  <!-- 研究级元数据 -->
  <Study id="TDF001">
    <MetaDataVersion 
        name="TDF001_V1" 
        label="Study TDF001 Define-XML Version 1" 
        description="Initial submission version">
      
      <!-- 数据集定义 -->
      <Dataset name="DM" label="Demographics" class="INDS" structure="record" 
               purpose="Tabulation" templateType="DM">
        <Variable name="STUDYID" ... />
        <Variable name="USUBJID" ... />
        ...
      </Dataset>
      
      <Dataset name="ADSL" label="Subject Level Analysis Dataset" 
               class="ADSL" structure="record" purpose="Analysis">
        <Variable name="STUDYID" ... />
        <Variable name="USUBJID" ... />
        ...
      </Dataset>
      
      <!-- 代码列表定义 -->
      <CodeList name="CL.ARM" label="Treatment Arm" 
                DataType="text" SdtmRole="nullflavor">
        <EnumeratedValue value="A" label="Drug X - 50mg">
        <EnumeratedValue value="B" label="Placebo">
      </CodeList>
      
    </MetaDataVersion>
  </Study>
</DefineXML>
```

### 2.2 核心元素说明

| 元素 | 说明 | 示例 |
|------|------|------|
| `<DefineXML>` | 根元素，声明命名空间和版本 | `version="3.1"` |
| `<Study>` | 研究级容器，`id` 为研究标识 | `id="TDF001"` |
| `<MetaDataVersion>` | 元数据版本，可有多版本 | `name="TDF001_V1"` |
| `<Dataset>` | 数据集定义 | `name="DM"`, `label="Demographics"` |
| `<Variable>` | 变量定义 | `name="USUBJID"` |
| `<CodeList>` | 代码列表（枚举值） | 定义变量的允许值 |

### 2.3 Dataset 属性详解

| 属性 | 说明 | 示例 |
|------|------|------|
| `name` | 数据集名称（文件前缀） | `DM`, `AE`, `ADSL`, `ADLB` |
| `label` | 数据集描述 | `Demographics`, `Adverse Events` |
| `class` | CDISC 类 | `INDS` (Intervention), `FINDS` (Finding), `ADSL` (Analysis) |
| `structure` | 结构类型 | `record` (记录级), `subject` (受试者级) |
| `purpose` | 用途 | `Tabulation` (SDTM), `Analysis` (ADaM), `Reference` |
| `templateType` | 模板类型（SDTM） | `DM`, `AE`, `VS`, `LB` 等 |

### 2.4 Variable 属性详解

| 属性 | 说明 | 示例 |
|------|------|------|
| `name` | 变量名 | `USUBJID`, `AETERM`, `AVAL` |
| `label` | 变量描述 | `Unique Subject Identifier` |
| `DataType` | 数据类型 | `text`, `integer`, `float`, `date` |
| `SdtmRole` | SDTM 角色 | `identifier`, `topic`, `timing`, `result`, `qualifier` |
| `Origin` | 来源 | `DM.USUBJID`, `derived`, `adsl.TRTE` |
| `Length` | 最大长度 | `200`, `8` |
| `Display` | 显示格式 | `DATE9.`, `BESTDTC` |

---

## 三、元数据变量说明

### 3.1 变量来源类型（Origin）

| 来源类型 | 说明 | 示例 |
|----------|------|------|
| **Assigned** | 手动分配的值 | `STUDYID = "TDF001"` |
| **Pre-existing** | 原始数据中的值 | `DM.USUBJID` |
| **Derived** | 衍生计算 | `CHG = AVAL - BASE` |
| **Computational** | 计算得出（如日期） | `TRTSDT` 从 `RFSTDTC` 转换 |
| **External** | 外部数据源 | `参考范围来自实验室手册` |

### 3.2 变量角色（SdtmRole）

| 角色 | 说明 | 示例 |
|------|------|------|
| **Identifier** | 唯一标识 | `STUDYID`, `USUBJID`, `SITEID` |
| **Topic** | 观测主题 | `AETERM`, `VSTEST`, `LBTEST` |
| **Timing** | 时间信息 | `AESTDTC`, `VSDTC`, `EXSTDTC` |
| **Result** | 观测结果 | `VSORRES`, `LBORRES`, `AVAL` |
| **Qualifier** | 补充限定 | `AEREL`, `AESEV`, `ANRIND` |

### 3.3 数据类型（DataType）

| 类型 | 说明 | 示例 |
|------|------|------|
| `text` | 字符型 | `AETERM`, `USUBJID` |
| `integer` | 整型 | `AESEQ`, `LBORRES`（整数） |
| `float` | 浮点型 | `VSORRES`（血压） |
| `date` | 日期型 | `AESTDTC`, `TRTSDT` |
| `datetime` | 日期时间 | `AESTDTC`（带时间戳） |

### 3.4 变量来源标注规则

| 场景 | Origin 标注 | 示例 |
|------|-------------|------|
| 直接来自 SDTM | `domain.variable` | `AE.AETERM` |
| 来自多个 SDTM 域 | `domain1.variable, domain2.variable` | `DM.AGE, LB.LBORRES` |
| 衍生变量 | `derived` | `CHG` |
| 分配常量 | `Assigned` | `STUDYID = "TDF001"` |
| 外部参考 | `External` | `ANRIND` 参考实验室手册 |

---

## 四、生成工具

### 4.1 R {xportr} 包（推荐）

**{xportr}** 是 CDISC Pharmaverse 项目的官方包，与 {admiral} 配套使用。

#### 安装

```r
# 从 CRAN 安装
install.packages("xportr")

# 或从 GitHub 安装开发版
# remotes::install_github("pharmaverse/xportr")
```

#### 基本用法

```r
library(xportr)
library(haven)
library(dplyr)

# 加载 SDTM 数据集
dm <- read_xpt("sdtm/dm.xpt")
ae <- read_xpt("sdtm/ae.xpt")
vs <- read_xpt("sdtm/vs.xpt")
lb <- read_xpt("sdtm/lb.xpt")

# 加载变量标签（从 spec 表或手动定义）
# 方法1：从 spec Excel 表读取
spec_df <- readxl::read_excel("metadata/specs.xlsx")

# 方法2：手动定义变量标签
var_labels <- list(
  STUDYID = "Study Identifier",
  USUBJID = "Unique Subject Identifier",
  SITEID = "Site Identifier",
  SUBJID = "Subject Identifier",
  ARM = "Description of Arm",
  ARMCD = "Arm Code",
  AGE = "Age",
  AGEU = "Age Units",
  RACE = "Race",
  SEX = "Sex",
  ETHNIC = "Ethnicity"
)

# 应用变量标签
dm <- var_labels %>% 
  purrr::walk2(dm, ~label<-.x1, .y)

# 生成 define.xml
xportr_write(
  dataset = dm,
  path = "define.xml",
  study_id = "TDF001",
  metadata_version = "TDF001_V1",
  label = "Demographics Domain",
  class = "INDS",
  purpose = "Tabulation"
)
```

#### 批量生成 define.xml

```r
# 从 LiamHobby/Admiral-Hackathon 模式
generate_define_xml <- function(sdtm_path = "sdtm", output_path = "define.xml") {
  library(xportr)
  library(haven)
  library(purrr)
  
  # 定义域信息
  domains <- tibble::tibble(
    file = list.files(sdtm_path, pattern = "\\.xpt$", full.names = TRUE),
    name = stringr::str_remove(basename(.x), "\\.xpt$"),
    label = c(
      "Demographics", "Adverse Events", "Vital Signs", "Laboratory Results",
      "Exposure", "Disposition", "Medical History", "Concomitant Medications",
      "Subject Visits"
    )[1:length(.x)],
    class = c("INDS", "EVNT", "FINDS", "FINDS", "EX", "DS", "FINDS", "CM", "FINDS"),
    purpose = "Tabulation"
  )
  
  # 加载所有数据集
  datasets <- domains$file %>%
    set_names(domains$name) %>%
    map(read_xpt) %>%
    map(convert_blanks_to_na)
  
  # 生成 define.xml
  define_xml_path <- file.path(output_path, "define.xml")
  
  xportr_write(
    dataset = datasets$DM,
    path = define_xml_path,
    study_id = "TDF001",
    metadata_version = "TDF001_V1",
    label = "Demographics",
    class = "INDS",
    purpose = "Tabulation",
    append = FALSE  # 第一个数据集，不追加
  )
  
  # 追加其他数据集
  map2(
    datasets[-1], 
    domains$name[-1],
    ~xportr_write(
      dataset = .x,
      path = define_xml_path,
      study_id = "TDF001",
      metadata_version = "TDF001_V1",
      label = domains$label[domains$name == .y],
      class = domains$class[domains$name == .y],
      purpose = "Tabulation",
      append = TRUE
    )
  )
  
  message("define.xml generated: ", define_xml_path)
  return(define_xml_path)
}
```

### 4.2 SAS 宏（工业界标准）

SAS 是工业界 80%+ 的临床试验数据处理工具，定义 XML 生成有成熟的宏方案。

#### 方法1：PROC DATASETS + 自定义宏

```sas
/* 定义变量标签 */
proc datasets lib=work nolist;
  modify DM;
    label STUDYID = "Study Identifier"
          USUBJID = "Unique Subject Identifier"
          SITEID = "Site Identifier"
          SUBJID = "Subject Identifier"
          ARM = "Description of Arm"
          ARMCD = "Arm Code"
          AGE = "Age"
          AGEU = "Age Units"
          RACE = "Race"
          SEX = "Sex";
  quit;

/* 生成 define.xml 的 SAS 宏（简化版）*/
%macro generate_define_xml(dataset=, lib=work, output=define.xml, study_id=TDF001);

  /* 获取变量信息 */
  proc contents data=&lib..&dataset. out=vars(keep=name label type length format) 
                noprint;
  run;

  /* 创建 XML 头部 */
  data _null_;
    file "&output." encoding=utf-8;
    put '<?xml version="1.0" encoding="UTF-8"?>';
    put '<DefineXML version="3.1">';
    put '  <Study id="' "&study_id." '">';
    put '    <MetaDataVersion name="' "&study_id._V1" '" label="Study ' 
        "&study_id." ' Define-XML Version 1">';
    put '      <Dataset name="' "&dataset." '" label="' "&dataset." '" ';
    put '               class="INDS" structure="record" purpose="Tabulation">';
  run;

  /* 写入变量信息 */
  proc sql;
    create table vars_ordered as
    select name, label, type, length, format
    from vars
    order by varnum;
  quit;

  data _null_;
    set vars_ordered;
    file "&output." encoding=utf-8 mod;
    
    /* 变量类型映射 */
    if type = 1 then datatype = "text";
    else if type = 2 then datatype = "float";
    else datatype = "unknown";
    
    put '        <Variable name="' name '"'
        ' label="' cox(label, " ") '"'
        ' dataType="' datatype '"'
        ' length="' put(length, best.) '"'
        '>';
    
    /* 来源标注 */
    if upcase(name) = "STUDYID" then 
      put '          <Origin type="Assigned">Study ID from protocol</Origin>';
    else if upcase(name) = "USUBJID" then 
      put '          <Origin type="Pre-existing">DM.USUBJID</Origin>';
    else 
      put '          <Origin type="Pre-existing">' 
          upcase("&dataset.") '.' upcase(name) '</Origin>';
    
    put '        </Variable>';
  run;

  /* 写入 XML 尾部 */
  data _null_;
    file "&output." encoding=utf-8 mod;
    put '      </Dataset>';
    put '    </MetaDataVersion>';
    put '  </Study>';
    put '</DefineXML>';
  run;

%mend generate_define_xml;

/* 调用宏 */
%generate_define_xml(dataset=DM, output=/path/to/define.xml, study_id=TDF001);
```

#### 方法2：使用 CDISC 官方 SAS 宏

CDISC 提供官方 SAS 宏用于 define.xml 生成：

```sas
/* 需要 CDISC 提供的 define.xml 生成宏包 */
%include "/path/to/cdisc_macros/sdtm_define_gen.sas";

/* 生成 SDTM define.xml */
%SDTM_DEFINE_GEN(
  libref=WORK,
  datasets=DM AE VS LB EX DS,
  output_path=/path/to/output,
  study_id=TDF001,
  version=3.1
);

/* 生成 ADaM define.xml */
%ADAM_DEFINE_GEN(
  libref=WORK,
  datasets=ADSL ADAE ADVS ADLB,
  output_path=/path/to/output,
  study_id=TDF001,
  version=3.1,
  trace_level=2
);
```

### 4.3 工具对比

| 特性 | R {xportr} | SAS 宏 | Python |
|------|-----------|--------|--------|
| **学习曲线** | 低（tidyverse 风格） | 中（需 SAS 基础） | 低 |
| **工业采用率** | 增长中 | 80%+ | 新兴 |
| **官方支持** | CDISC Pharmaverse | CDISC 官方 | 社区 |
| **ADaM 支持** | 完整 | 完整 | 基础 |
| **追溯性** | 自动追踪 {admiral} 衍生 | 需手动标注 | 需手动 |
| **成本** | 免费 | 需 SAS 许可证 | 免费 |

---

## 五、验证方法

### 5.1 define.xml 验证工具

| 工具 | 类型 | 说明 |
|------|------|------|
| **Pinnacle 21** | 商业软件 | FDA 官方推荐验证工具，有免费社区版 |
| **CDISC Validator** | 免费工具 | CDISC 官方验证器 |
| **{checkmate}** | R 包 | 基础 XML 结构验证 |
| **自定义脚本** | 自研 | 业务规则验证 |

### 5.2 Pinnacle 21 验证流程

```bash
# 1. 下载 Pinnacle 21 Community (免费)
# https://pinnacle21.com/products/community

# 2. 验证 define.xml
# GUI: 打开 P21 → File → Import → 选择 define.xml + 数据集
# CLI: 
java -jar p21-validator.jar \
  --define define.xml \
  --datasets sdtm/*.xpt \
  --output validation_report.html

# 3. 检查验证结果
# - GREEN: 通过
# - YELLOW: 警告（可提交）
# - RED: 错误（必须修复）
```

### 5.3 R 验证脚本

```r
# define.xml 结构验证
validate_define_xml <- function(define_xml_path) {
  library(xml2)
  library(rvest)
  
  doc <- read_xml(define_xml_path)
  
  # 检查根元素
  root <- xml_root(doc)
  if (xml_name(root) != "DefineXML") {
    stop("根元素必须是 DefineXML")
  }
  
  # 检查版本
  version <- xml_attr(root, "version")
  if (!version %in% c("2.1", "3.0", "3.1")) {
    warning(paste("define.xml 版本", version, "可能不被 FDA 接受"))
  }
  
  # 检查命名空间
  ns <- xml_attr(root, "xmlns")
  if (is.na(ns)) {
    stop("缺少 xmlns 命名空间声明")
  }
  
  # 检查 Study 元素
  study <- xml_find_first(doc, "//Study")
  if (is.na(study)) {
    stop("缺少 Study 元素")
  }
  study_id <- xml_attr(study, "id")
  message("研究 ID: ", study_id)
  
  # 检查 MetaDataVersion
  mdv <- xml_find_first(doc, "//MetaDataVersion")
  if (is.na(mdv)) {
    stop("缺少 MetaDataVersion 元素")
  }
  
  # 检查所有 Dataset
  datasets <- xml_find_all(doc, "//Dataset")
  message("数据集数量: ", length(datasets))
  
  dataset_names <- xml_attr(datasets, "name")
  if (any(duplicated(dataset_names))) {
    stop("存在重复的数据集名称")
  }
  
  # 检查所有 Variable
  variables <- xml_find_all(doc, "//Variable")
  message("变量总数: ", length(variables))
  
  # 检查必需的变量标签
  missing_labels <- variables[xml_attr(variables, "label") == ""]
  if (length(missing_labels) > 0) {
    warning("以下变量缺少标签: ", 
            paste(xml_attr(missing_labels, "name"), collapse = ", "))
  }
  
  # 检查 Origin 元素
  origins <- xml_find_all(doc, "//Origin")
  message("来源标注数量: ", length(origins))
  
  # 检查 CodeList
  codelists <- xml_find_all(doc, "//CodeList")
  message("代码列表数量: ", length(codelists))
  
  message("✅ define.xml 基础结构验证通过")
  return(TRUE)
}

# 使用
validate_define_xml("define.xml")
```

### 5.4 业务规则验证

```r
# 业务规则验证（自定义）
validate_business_rules <- function(define_xml_path, sdtm_path = "sdtm") {
  library(xml2)
  library(haven)
  library(dplyr)
  
  doc <- read_xml(define_xml_path)
  variables <- xml_find_all(doc, "//Variable")
  
  errors <- list()
  
  for (var in variables) {
    var_name <- xml_attr(var, "name")
    var_type <- xml_attr(var, "dataType")
    origin <- xml_find_first(var, "Origin")
    origin_type <- xml_attr(origin, "type")
    
    # 规则1: USUBJID 必须是 identifier 角色
    if (var_name == "USUBJID") {
      role <- xml_attr(var, "sdtmRole")
      if (tolower(role) != "identifier") {
        errors[[length(errors) + 1]] <- paste(
          "USUBJID 的 sdtmRole 应为 identifier，当前为:", role
        )
      }
    }
    
    # 规则2: 日期变量必须有日期格式
    if (grepl("DTC|DT$", var_name, ignore.case = TRUE)) {
      display <- xml_attr(var, "display")
      if (is.na(display) || !grepl("DATE", display, ignore.case = TRUE)) {
        errors[[length(errors) + 1]] <- paste(
          var_name, "是日期变量但缺少 DATE 格式"
        )
      }
    }
    
    # 规则3: 衍生变量必须有 Origin type="derived"
    if (origin_type == "derived") {
      desc <- xml_text(origin)
      if (nchar(trimws(desc)) == 0) {
        errors[[length(errors) + 1]] <- paste(
          var_name, "是衍生变量但缺少衍生逻辑描述"
        )
      }
    }
  }
  
  if (length(errors) > 0) {
    message("❌ 发现 ", length(errors), " 个业务规则错误:")
    walk(errors, message)
    return(FALSE)
  }
  
  message("✅ 业务规则验证通过")
  return(TRUE)
}
```

### 5.5 验证检查清单

| 检查项 | 说明 | 工具 |
|--------|------|------|
| **XML 格式** | 符合 XML 1.0 规范 | 任何 XML 解析器 |
| **命名空间** | 正确的 CDISC 命名空间 | P21, 自定义脚本 |
| **版本** | FDA 接受的版本（3.1） | P21 |
| **必需元素** | Study, MetaDataVersion, Dataset, Variable | 自定义脚本 |
| **变量标签** | 所有变量有 label | P21, 自定义脚本 |
| **数据类型** | 与实际数据一致 | P21 |
| **长度** | 不超过实际数据长度 | P21 |
| **Origin** | 所有变量有来源标注 | 自定义脚本 |
| **CodeList** | 代码化变量有枚举值 | P21 |
| **追溯性** | ADaM 变量可追溯到 SDTM | 自定义脚本 |

---

## 六、实战模板代码

### 6.1 完整 define.xml 生成管道（R）

```r
# =============================================================================
# define.xml 完整生成管道
# 来源：基于 LiamHobby/Admiral-Hackathon 和 CDISC Pharmaverse 最佳实践
# =============================================================================

generate_full_define_xml <- function(
  study_id = "TDF001",
  sdtm_path = "sdtm",
  adam_path = "adam",
  output_path = "define.xml",
  metadata_version = "V1"
) {
  library(xportr)
  library(haven)
  library(dplyr)
  library(purrr)
  library(stringr)
  library(readxl)
  library(xml2)
  
  # ---- 1. 加载变量标签规格表 ----
  # 从 Excel 规格表读取（推荐方式）
  # 规格表格式：
  # | Dataset | Variable | Label | Type | Length | Format | Origin |
  spec_path <- file.path("metadata", "define_specs.xlsx")
  
  if (file.exists(spec_path)) {
    spec_df <- read_excel(spec_path, col_types = "text") %>%
      filter(!is.na(Dataset) & Dataset != "")
    message("✅ 从规格表加载 ", nrow(spec_df), " 个变量定义")
  } else {
    warning("⚠️ 未找到规格表，使用默认标签")
    spec_df <- NULL
  }
  
  # ---- 2. 定义域元数据 ----
  sdtm_domains <- tibble::tibble(
    file = c("dm.xpt", "ae.xpt", "vs.xpt", "lb.xpt", "ex.xpt", 
             "ds.xpt", "mh.xpt", "cm.xpt", "sv.xpt"),
    name = c("DM", "AE", "VS", "LB", "EX", "DS", "MH", "CM", "SV"),
    label = c(
      "Demographics", "Adverse Events", "Vital Signs", "Laboratory Results",
      "Exposure", "Disposition", "Medical History", "Concomitant Medications",
      "Subject Visits"
    ),
    class = c("INDS", "EVNT", "FINDS", "FINDS", "EX", "DS", "FINDS", "CM", "FINDS"),
    purpose = "Tabulation"
  )
  
  adam_datasets <- tibble::tibble(
    file = c("adsl.xpt", "adae.xpt", "advs.xpt", "adlb.xpt"),
    name = c("ADSL", "ADAE", "ADVS", "ADLB"),
    label = c(
      "Subject Level Analysis Dataset",
      "Adverse Events Analysis Dataset",
      "Vital Signs Analysis Dataset",
      "Laboratory Analysis Dataset"
    ),
    class = c("ADSL", "ADAE", "ADVS", "ADLB"),
    purpose = "Analysis"
  )
  
  # ---- 3. 加载并处理数据集 ----
  load_and_process <- function(path, type = "sdtm") {
    datasets <- list()
    
    items <- if (type == "sdtm") sdtm_domains else adam_datasets
    
    for (i in seq_len(nrow(items))) {
      file_path <- file.path(path, items$file[i])
      if (file.exists(file_path)) {
        ds <- read_xpt(file_path)
        ds <- convert_blanks_to_na(ds)
        
        # 应用变量标签
        if (!is.null(spec_df)) {
          vars_for_ds <- spec_df %>% filter(Dataset == items$name[i])
          for (j in seq_len(nrow(vars_for_ds))) {
            var_name <- vars_for_ds$Variable[j]
            var_label <- vars_for_ds$Label[j]
            if (var_name %in% names(ds)) {
              label(ds[[var_name]]) <- var_label
            }
          }
        }
        
        datasets[[items$name[i]]] <- ds
        message("  ✓ Loaded: ", items$name[i])
      } else {
        warning("⚠️ 文件不存在: ", file_path)
      }
    }
    
    return(datasets)
  }
  
  message("\n📂 加载 SDTM 数据集:")
  sdtm_datasets <- load_and_process(sdtm_path, "sdtm")
  
  message("\n📂 加载 ADaM 数据集:")
  adam_datasets_loaded <- load_and_process(adam_path, "adam")
  
  # ---- 4. 生成 define.xml ----
  all_datasets <- c(sdtm_datasets, adam_datasets_loaded)
  all_info <- bind_rows(
    sdtm_domains %>% filter(name %in% names(sdtm_datasets)),
    adam_datasets %>% filter(name %in% names(adam_datasets_loaded))
  )
  
  # 确保输出目录存在
  output_dir <- dirname(output_path)
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  
  # 生成第一个数据集（不追加）
  first_ds_name <- names(all_datasets)[1]
  first_ds_info <- all_info %>% filter(name == first_ds_name) %>% slice(1)
  
  xportr_write(
    dataset = all_datasets[[first_ds_name]],
    path = output_path,
    study_id = study_id,
    metadata_version = paste0(study_id, "_", metadata_version),
    label = first_ds_info$label,
    class = first_ds_info$class,
    purpose = first_ds_info$purpose,
    append = FALSE
  )
  message("  ✓ Written: ", first_ds_name)
  
  # 追加剩余数据集
  for (ds_name in names(all_datasets)[-1]) {
    ds_info <- all_info %>% filter(name == ds_name) %>% slice(1)
    
    xportr_write(
      dataset = all_datasets[[ds_name]],
      path = output_path,
      study_id = study_id,
      metadata_version = paste0(study_id, "_", metadata_version),
      label = ds_info$label,
      class = ds_info$class,
      purpose = ds_info$purpose,
      append = TRUE
    )
    message("  ✓ Appended: ", ds_name)
  }
  
  message("\n✅ define.xml 生成完成: ", output_path)
  
  # ---- 5. 验证 ----
  message("\n🔍 验证 define.xml:")
  validate_define_xml(output_path)
  
  return(output_path)
}

# 运行管道
# generate_full_define_xml(
#   study_id = "TDF001",
#   sdtm_path = "sdtm",
#   adam_path = "adam",
#   output_path = "output/define.xml"
# )
```

### 6.2 手动编写 define.xml 模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DefineXML xmlns="http://www.cdisc.org/ns/def/v31" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           version="3.1">
  
  <Study id="TDF001">
    <MetaDataVersion 
        name="TDF001_V1" 
        label="Study TDF001 Define-XML Version 1" 
        description="Initial submission version">
      
      <!-- ==================== SDTM 数据集 ==================== -->
      
      <!-- DM - Demographics -->
      <Dataset name="DM" label="Demographics" class="INDS" 
               structure="record" purpose="Tabulation" templateType="DM">
        <Variable name="STUDYID" label="Study Identifier" dataType="text" 
                  length="200" sdtmRole="identifier">
          <Origin type="Assigned">Study ID from protocol</Origin>
        </Variable>
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">DM.USUBJID</Origin>
        </Variable>
        <Variable name="SITEID" label="Site Identifier" dataType="text" 
                  length="8" sdtmRole="identifier">
          <Origin type="Pre-existing">DM.SITEID</Origin>
        </Variable>
        <Variable name="SUBJID" label="Subject Identifier" dataType="text" 
                  length="8" sdtmRole="identifier">
          <Origin type="Pre-existing">DM.SUBJID</Origin>
        </Variable>
        <Variable name="ARM" label="Description of Arm" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">DM.ARM</Origin>
        </Variable>
        <Variable name="ARMCD" label="Arm Code" dataType="text" 
                  length="8" sdtmRole="topic">
          <Origin type="Pre-existing">DM.ARMCD</Origin>
        </Variable>
        <Variable name="AGE" label="Age" dataType="integer" length="8" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.AGE</Origin>
        </Variable>
        <Variable name="AGEU" label="Age Units" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">DM.AGEU</Origin>
        </Variable>
        <Variable name="RACE" label="Race" dataType="text" length="200" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.RACE</Origin>
        </Variable>
        <Variable name="SEX" label="Sex" dataType="text" length="1" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.SEX</Origin>
        </Variable>
        <Variable name="ETHNIC" label="Ethnicity" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">DM.ETHNIC</Origin>
        </Variable>
        <Variable name="DTHFL" label="Subject Death Flag" dataType="text" 
                  length="1" sdtmRole="qualifier">
          <Origin type="Pre-existing">DM.DTHFL</Origin>
        </Variable>
        <Variable name="RFSTDTC" label="Subject Reference Start Date" 
                  dataType="datetime" length="200" sdtmRole="timing">
          <Origin type="Pre-existing">DM.RFSTDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
        <Variable name="RFENDTC" label="Subject Reference End Date" 
                  dataType="datetime" length="200" sdtmRole="timing">
          <Origin type="Pre-existing">DM.RFENDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
      </Dataset>
      
      <!-- AE - Adverse Events -->
      <Dataset name="AE" label="Adverse Events" class="EVNT" 
               structure="record" purpose="Tabulation" templateType="AE">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">AE.USUBJID</Origin>
        </Variable>
        <Variable name="AESEQ" label="Sequence Number" dataType="integer" 
                  length="8" sdtmRole="identifier">
          <Origin type="Pre-existing">AE.AESEQ</Origin>
        </Variable>
        <Variable name="AETERM" label="Reported Term for the Adverse Event" 
                  dataType="text" length="200" sdtmRole="topic">
          <Origin type="Pre-existing">AE.AETERM</Origin>
        </Variable>
        <Variable name="AESEV" label="Severity/Intensity" dataType="text" 
                  length="8" sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AESEV</Origin>
        </Variable>
        <Variable name="AESER" label="Serious Adverse Event" dataType="text" 
                  length="1" sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AESER</Origin>
        </Variable>
        <Variable name="AEREL" label="Causality" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AEREL</Origin>
        </Variable>
        <Variable name="AEACN" label="Action Taken with Drug" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AEACN</Origin>
        </Variable>
        <Variable name="AESTDTC" label="Start Date/Time of Adverse Event" 
                  dataType="datetime" length="200" sdtmRole="timing">
          <Origin type="Pre-existing">AE.AESTDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
        <Variable name="AEENDTC" label="End Date/Time of Adverse Event" 
                  dataType="datetime" length="200" sdtmRole="timing">
          <Origin type="Pre-existing">AE.AEENDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
      </Dataset>
      
      <!-- VS - Vital Signs -->
      <Dataset name="VS" label="Vital Signs" class="FINDS" 
               structure="record" purpose="Tabulation" templateType="VS">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">VS.USUBJID</Origin>
        </Variable>
        <Variable name="VSTESTCD" label="Vital Signs Test Code" dataType="text" 
                  length="8" sdtmRole="topic">
          <Origin type="Pre-existing">VS.VSTESTCD</Origin>
        </Variable>
        <Variable name="VSTEST" label="Vital Signs Test Name" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">VS.VSTEST</Origin>
        </Variable>
        <Variable name="VSORRES" label="Original Result" dataType="float" 
                  length="200" sdtmRole="result">
          <Origin type="Pre-existing">VS.VSORRES</Origin>
        </Variable>
        <Variable name="VSORRESU" label="Original Units" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">VS.VSORRESU</Origin>
        </Variable>
        <Variable name="VSTESTCAT" label="Category for Test Name" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">VS.VSTESTCAT</Origin>
        </Variable>
        <Variable name="VSBLFL" label="Baseline Flag" dataType="text" length="1" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">VS.VSBLFL</Origin>
        </Variable>
        <Variable name="VSDTC" label="Date/Time of Vital Signs" dataType="datetime" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">VS.VSDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
      </Dataset>
      
      <!-- LB - Laboratory Results -->
      <Dataset name="LB" label="Laboratory Results" class="FINDS" 
               structure="record" purpose="Tabulation" templateType="LB">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">LB.USUBJID</Origin>
        </Variable>
        <Variable name="LBTESTCD" label="Lab Test Code" dataType="text" 
                  length="8" sdtmRole="topic">
          <Origin type="Pre-existing">LB.LBTESTCD</Origin>
        </Variable>
        <Variable name="LBTEST" label="Lab Test Name" dataType="text" length="200" 
                  sdtmRole="topic">
          <Origin type="Pre-existing">LB.LBTEST</Origin>
        </Variable>
        <Variable name="LBORRES" label="Original Result" dataType="float" 
                  length="200" sdtmRole="result">
          <Origin type="Pre-existing">LB.LBORRES</Origin>
        </Variable>
        <Variable name="LBORRESU" label="Original Units" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">LB.LBORRESU</Origin>
        </Variable>
        <Variable name="LBNRIND" label="Reference Range" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">LB.LBNRIND</Origin>
        </Variable>
        <Variable name="LBBLFL" label="Baseline Flag" dataType="text" length="1" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">LB.LBBLFL</Origin>
        </Variable>
        <Variable name="LBDTC" label="Date/Time of Lab Result" dataType="datetime" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">LB.LBDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
        <Variable name="LBSTRESC" label="Standardized Result (Char)" dataType="text" 
                  length="200" sdtmRole="result">
          <Origin type="Pre-existing">LB.LBSTRESC</Origin>
        </Variable>
        <Variable name="LBSTRESN" label="Standardized Result (Num)" dataType="float" 
                  length="200" sdtmRole="result">
          <Origin type="Pre-existing">LB.LBSTRESN</Origin>
        </Variable>
        <Variable name="LBSTRESU" label="Standardized Units" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">LB.LBSTRESU</Origin>
        </Variable>
      </Dataset>
      
      <!-- EX - Exposure -->
      <Dataset name="EX" label="Exposure" class="EX" 
               structure="record" purpose="Tabulation" templateType="EX">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">EX.USUBJID</Origin>
        </Variable>
        <Variable name="EXTRT" label="Name of Actual Treatment" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">EX.EXTRT</Origin>
        </Variable>
        <Variable name="EXDOSE" label="Dose per Administration" dataType="float" 
                  length="200" sdtmRole="result">
          <Origin type="Pre-existing">EX.EXDOSE</Origin>
        </Variable>
        <Variable name="EXDOSU" label="Dose Units" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">EX.EXDOSU</Origin>
        </Variable>
        <Variable name="EXDOSFRM" label="Dose Form" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">EX.EXDOSFRM</Origin>
        </Variable>
        <Variable name="EXDOSFRQ" label="Dose Frequency" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">EX.EXDOSFRQ</Origin>
        </Variable>
        <Variable name="EXROUTE" label="Route of Administration" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Pre-existing">EX.EXROUTE</Origin>
        </Variable>
        <Variable name="EXSTDTC" label="Start Date/Time of Exposure" dataType="datetime" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">EX.EXSTDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
        <Variable name="EXENDTC" label="End Date/Time of Exposure" dataType="datetime" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">EX.EXENDTC</Origin>
          <Display name="BESTDTC"/>
        </Variable>
      </Dataset>
      
      <!-- ==================== ADaM 数据集 ==================== -->
      
      <!-- ADSL - Subject Level Analysis Dataset -->
      <Dataset name="ADSL" label="Subject Level Analysis Dataset" 
               class="ADSL" structure="record" purpose="Analysis">
        <Variable name="STUDYID" label="Study Identifier" dataType="text" 
                  length="200" sdtmRole="identifier">
          <Origin type="Assigned">Study ID from protocol</Origin>
        </Variable>
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">DM.USUBJID</Origin>
        </Variable>
        <Variable name="SITEID" label="Site Identifier" dataType="text" 
                  length="8" sdtmRole="identifier">
          <Origin type="Pre-existing">DM.SITEID</Origin>
        </Variable>
        <Variable name="TRT01P" label="Planned Treatment Group" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">DM.ARM</Origin>
        </Variable>
        <Variable name="TRT01A" label="Actual Treatment Group" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">DM.ARM</Origin>
        </Variable>
        <Variable name="TRTSDT" label="First Date of Treatment" dataType="date" 
                  length="200" sdtmRole="timing">
          <Origin type="Derived" 
                  desc="First date of any treatment from EX domain">EX.EXSTDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="TRTEDT" label="Last Date of Treatment" dataType="date" 
                  length="200" sdtmRole="timing">
          <Origin type="Derived" 
                  desc="Last date of any treatment from EX domain">EX.EXENDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="AGE" label="Age" dataType="integer" length="8" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.AGE</Origin>
        </Variable>
        <Variable name="SEX" label="Sex" dataType="text" length="1" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.SEX</Origin>
        </Variable>
        <Variable name="RACE" label="Race" dataType="text" length="200" 
                  sdtmRole="result">
          <Origin type="Pre-existing">DM.RACE</Origin>
        </Variable>
        <Variable name="DTHFL" label="Subject Death Flag" dataType="text" 
                  length="1" sdtmRole="qualifier">
          <Origin type="Pre-existing">DM.DTHFL</Origin>
        </Variable>
        <Variable name="DTHDT" label="Date of Death" dataType="date" length="200" 
                  sdtmRole="timing">
          <Origin type="Pre-existing">DM.DTHDT</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="EOSSTT" label="End of Study Status" dataType="text" 
                  length="200" sdtmRole="qualifier">
          <Origin type="Derived" 
                  desc="Derived from DS domain disposition records">DS.DSDECOD</Origin>
        </Variable>
      </Dataset>
      
      <!-- ADAE - Adverse Events Analysis Dataset -->
      <Dataset name="ADAE" label="Adverse Events Analysis Dataset" 
               class="ADAE" structure="record" purpose="Analysis">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">AE.USUBJID</Origin>
        </Variable>
        <Variable name="AETERM" label="Adverse Event Term" dataType="text" 
                  length="200" sdtmRole="topic">
          <Origin type="Pre-existing">AE.AETERM</Origin>
        </Variable>
        <Variable name="AESER" label="Serious Adverse Event" dataType="text" 
                  length="1" sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AESER</Origin>
        </Variable>
        <Variable name="AEREL" label="Causality" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AEREL</Origin>
        </Variable>
        <Variable name="AESEV" label="Severity/Intensity" dataType="text" length="8" 
                  sdtmRole="qualifier">
          <Origin type="Pre-existing">AE.AESEV</Origin>
        </Variable>
        <Variable name="ASTDT" label="Start Date of Adverse Event" dataType="date" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">AE.AESTDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="AENDT" label="End Date of Adverse Event" dataType="date" 
                  length="200" sdtmRole="timing">
          <Origin type="Pre-existing">AE.AEENDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="TRTEMFL" label="Treatment Emergent Flag" dataType="text" 
                  length="1" sdtmRole="qualifier">
          <Origin type="Derived" 
                  desc="Y if AE start date is on or after TRTSDT and before or on TRTEDT">
            ADSL.TRTSDT, ADSL.TRTEDT, AE.AESTDTC
          </Origin>
        </Variable>
      </Dataset>
      
      <!-- ADVS - Vital Signs Analysis Dataset -->
      <Dataset name="ADVS" label="Vital Signs Analysis Dataset" 
               class="ADVS" structure="record" purpose="Analysis">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">VS.USUBJID</Origin>
        </Variable>
        <Variable name="PARAMCD" label="Parameter Code" dataType="text" length="8" 
                  sdtmRole="identifier">
          <Origin type="Derived" 
                  desc="Mapped from VSTESTCD (SYSBP, DIABP, PULSE, etc.)">VS.VSTESTCD</Origin>
        </Variable>
        <Variable name="PARAM" label="Parameter Name" dataType="text" length="200" 
                  sdtmRole="topic">
          <Origin type="Derived" 
                  desc="Mapped from VSTEST">VS.VSTEST</Origin>
        </Variable>
        <Variable name="AVAL" label="Analysis Value" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Pre-existing">VS.VSORRES</Origin>
        </Variable>
        <Variable name="BASE" label="Baseline Value" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Derived" 
                  desc="First non-missing value before or at baseline visit">VS.VSORRES</Origin>
        </Variable>
        <Variable name="CHG" label="Change from Baseline" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Derived" desc="AVAL - BASE"/>
        </Variable>
        <Variable name="PCHG" label="Percent Change from Baseline" dataType="float" 
                  length="200" sdtmRole="result">
          <Origin type="Derived" desc="(AVAL - BASE) / BASE * 100"/>
        </Variable>
        <Variable name="ADT" label="Analysis Date" dataType="date" length="200" 
                  sdtmRole="timing">
          <Origin type="Pre-existing">VS.VSDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="AVISIT" label="Visit" dataType="text" length="200" 
                  sdtmRole="timing">
          <Origin type="Derived" 
                  desc="Derived from VSDTC relative to TRTSDT"/>
        </Variable>
        <Variable name="TRT01P" label="Treatment Group" dataType="text" length="200" 
                  sdtmRole="topic">
          <Origin type="Pre-existing">ADSL.TRT01P</Origin>
        </Variable>
      </Dataset>
      
      <!-- ADLB - Laboratory Analysis Dataset -->
      <Dataset name="ADLB" label="Laboratory Analysis Dataset" 
               class="ADLB" structure="record" purpose="Analysis">
        <Variable name="USUBJID" label="Unique Subject Identifier" 
                  dataType="text" length="200" sdtmRole="identifier">
          <Origin type="Pre-existing">LB.USUBJID</Origin>
        </Variable>
        <Variable name="PARAMCD" label="Parameter Code" dataType="text" length="8" 
                  sdtmRole="identifier">
          <Origin type="Derived" 
                  desc="Mapped from LBTESTCD (ALT, AST, CR, etc.)">LB.LBTESTCD</Origin>
        </Variable>
        <Variable name="PARAM" label="Parameter Name" dataType="text" length="200" 
                  sdtmRole="topic">
          <Origin type="Derived" 
                  desc="Mapped from LBTEST">LB.LBTEST</Origin>
        </Variable>
        <Variable name="AVAL" label="Analysis Value" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Pre-existing">LB.LBORRES</Origin>
        </Variable>
        <Variable name="BASE" label="Baseline Value" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Derived" 
                  desc="First non-missing value at baseline visit">LB.LBORRES</Origin>
        </Variable>
        <Variable name="CHG" label="Change from Baseline" dataType="float" length="200" 
                  sdtmRole="result">
          <Origin type="Derived" desc="AVAL - BASE"/>
        </Variable>
        <Variable name="ABLFL" label="Baseline Flag" dataType="text" length="1" 
                  sdtmRole="qualifier">
          <Origin type="Derived" desc="Y if record is at baseline visit"/>
        </Variable>
        <Variable name="ANRIND" label="Abnormal Flag" dataType="text" length="200" 
                  sdtmRole="qualifier">
          <Origin type="Derived" 
                  desc="HIGH/LOW/NORMAL based on reference range (LBNRIND)"/>
        </Variable>
        <Variable name="ADT" label="Analysis Date" dataType="date" length="200" 
                  sdtmRole="timing">
          <Origin type="Pre-existing">LB.LBDTC</Origin>
          <Display name="DATE9."/>
        </Variable>
        <Variable name="TRT01P" label="Treatment Group" dataType="text" length="200" 
                  sdtmRole="topic">
          <Origin type="Pre-existing">ADSL.TRT01P</Origin>
        </Variable>
      </Dataset>
      
      <!-- ==================== 代码列表 ==================== -->
      
      <CodeList name="CL.ARM" label="Treatment Arm" DataType="text">
        <EnumeratedValue value="A" label="Drug X - 50mg"/>
        <EnumeratedValue value="B" label="Drug X - 100mg"/>
        <EnumeratedValue value="C" label="Placebo"/>
      </CodeList>
      
      <CodeList name="CL.SEX" label="Sex" DataType="text">
        <EnumeratedValue value="M" label="Male"/>
        <EnumeratedValue value="F" label="Female"/>
        <EnumeratedValue value="U" label="Unknown"/>
      </CodeList>
      
      <CodeList name="CL.RACE" label="Race" DataType="text">
        <EnumeratedValue value="WHITE" label="White"/>
        <EnumeratedValue value="BLACK" label="Black or African American"/>
        <EnumeratedValue value="ASIAN" label="Asian"/>
        <EnumeratedValue value="AMIND" label="American Indian or Alaska Native"/>
        <EnumeratedValue value="NAPIAN" label="Native Hawaiian or Other Pacific Islander"/>
        <EnumeratedValue value="MULTI" label="Multiracial"/>
        <EnumeratedValue value="OTH" label="Other"/>
      </CodeList>
      
      <CodeList name="CL.AESEV" label="Severity/Intensity" DataType="text">
        <EnumeratedValue value="1" label="Mild"/>
        <EnumeratedValue value="2" label="Moderate"/>
        <EnumeratedValue value="3" label="Severe"/>
      </CodeList>
      
      <CodeList name="CL.AESER" label="Serious Adverse Event" DataType="text">
        <EnumeratedValue value="Y" label="Yes"/>
        <EnumeratedValue value="N" label="No"/>
      </CodeList>
      
      <CodeList name="CL.AEREL" label="Causality" DataType="text">
        <EnumeratedValue value="RELATED" label="Related"/>
        <EnumeratedValue value="POSSIBLE" label="Possible"/>
        <EnumeratedValue value="UNLIKELY" label="Unlikely"/>
        <EnumeratedValue value="NOT RELATED" label="Not Related"/>
      </CodeList>
      
      <CodeList name="CL.ANRIND" label="Abnormal Flag" DataType="text">
        <EnumeratedValue value="HIGH" label="High"/>
        <EnumeratedValue value="LOW" label="Low"/>
        <EnumeratedValue value="NORMAL" label="Normal"/>
      </CodeList>
      
      <CodeList name="CL.EOSSTT" label="End of Study Status" DataType="text">
        <EnumeratedValue value="COMPLETED" label="Completed"/>
        <EnumeratedValue value="DISCONTINUED" label="Discontinued"/>
        <EnumeratedValue value="DECEASED" label="Deceased"/>
        <EnumeratedValue value="LOST TO FOLLOW-UP" label="Lost to Follow-up"/>
        <EnumeratedValue value="WITHDRAWAL" label="Withdrawal by Subject"/>
      </CodeList>
      
    </MetaDataVersion>
  </Study>
</DefineXML>
```

### 6.3 变量标签规格表模板（Excel）

| Dataset | Variable | Label | Type | Length | Format | Origin | Origin_Type |
|---------|----------|-------|------|--------|--------|--------|-------------|
| DM | STUDYID | Study Identifier | text | 200 | | Study ID from protocol | Assigned |
| DM | USUBJID | Unique Subject Identifier | text | 200 | | DM.USUBJID | Pre-existing |
| DM | SITEID | Site Identifier | text | 8 | | DM.SITEID | Pre-existing |
| DM | SUBJID | Subject Identifier | text | 8 | | DM.SUBJID | Pre-existing |
| DM | ARM | Description of Arm | text | 200 | | DM.ARM | Pre-existing |
| DM | ARMCD | Arm Code | text | 8 | | DM.ARMCD | Pre-existing |
| DM | AGE | Age | integer | 8 | | DM.AGE | Pre-existing |
| DM | AGEU | Age Units | text | 200 | | DM.AGEU | Pre-existing |
| DM | RACE | Race | text | 200 | | DM.RACE | Pre-existing |
| DM | SEX | Sex | text | 1 | | DM.SEX | Pre-existing |
| DM | ETHNIC | Ethnicity | text | 200 | | DM.ETHNIC | Pre-existing |
| DM | DTHFL | Subject Death Flag | text | 1 | | DM.DTHFL | Pre-existing |
| DM | RFSTDTC | Subject Reference Start Date | datetime | 200 | BESTDTC | DM.RFSTDTC | Pre-existing |
| DM | RFENDTC | Subject Reference End Date | datetime | 200 | BESTDTC | DM.RFENDTC | Pre-existing |
| AE | USUBJID | Unique Subject Identifier | text | 200 | | AE.USUBJID | Pre-existing |
| AE | AESEQ | Sequence Number | integer | 8 | | AE.AESEQ | Pre-existing |
| AE | AETERM | Reported Term for the Adverse Event | text | 200 | | AE.AETERM | Pre-existing |
| AE | AESEV | Severity/Intensity | text | 8 | | AE.AESEV | Pre-existing |
| AE | AESER | Serious Adverse Event | text | 1 | | AE.AESER | Pre-existing |
| AE | AEREL | Causality | text | 200 | | AE.AEREL | Pre-existing |
| AE | AEACN | Action Taken with Drug | text | 200 | | AE.AEACN | Pre-existing |
| AE | AESTDTC | Start Date/Time of Adverse Event | datetime | 200 | BESTDTC | AE.AESTDTC | Pre-existing |
| AE | AEENDTC | End Date/Time of Adverse Event | datetime | 200 | BESTDTC | AE.AEENDTC | Pre-existing |
| VS | USUBJID | Unique Subject Identifier | text | 200 | | VS.USUBJID | Pre-existing |
| VS | VSTESTCD | Vital Signs Test Code | text | 8 | | VS.VSTESTCD | Pre-existing |
| VS | VSTEST | Vital Signs Test Name | text | 200 | | VS.VSTEST | Pre-existing |
| VS | VSORRES | Original Result | float | 200 | | VS.VSORRES | Pre-existing |
| VS | VSORRESU | Original Units | text | 200 | | VS.VSORRESU | Pre-existing |
| VS | VSTESTCAT | Category for Test Name | text | 200 | | VS.VSTESTCAT | Pre-existing |
| VS | VSBLFL | Baseline Flag | text | 1 | | VS.VSBLFL | Pre-existing |
| VS | VSDTC | Date/Time of Vital Signs | datetime | 200 | BESTDTC | VS.VSDTC | Pre-existing |
| LB | USUBJID | Unique Subject Identifier | text | 200 | | LB.USUBJID | Pre-existing |
| LB | LBTESTCD | Lab Test Code | text | 8 | | LB.LBTESTCD | Pre-existing |
| LB | LBTEST | Lab Test Name | text | 200 | | LB.LBTEST | Pre-existing |
| LB | LBORRES | Original Result | float | 200 | | LB.LBORRES | Pre-existing |
| LB | LBORRESU | Original Units | text | 200 | | LB.LBORRESU | Pre-existing |
| LB | LBNRIND | Reference Range | text | 200 | | LB.LBNRIND | Pre-existing |
| LB | LBBLFL | Baseline Flag | text | 1 | | LB.LBBLFL | Pre-existing |
| LB | LBDTC | Date/Time of Lab Result | datetime | 200 | BESTDTC | LB.LBDTC | Pre-existing |
| LB | LBSTRESC | Standardized Result (Char) | text | 200 | | LB.LBSTRESC | Pre-existing |
| LB | LBSTRESN | Standardized Result (Num) | float | 200 | | LB.LBSTRESN | Pre-existing |
| LB | LBSTRESU | Standardized Units | text | 200 | | LB.LBSTRESU | Pre-existing |
| EX | USUBJID | Unique Subject Identifier | text | 200 | | EX.USUBJID | Pre-existing |
| EX | EXTRT | Name of Actual Treatment | text | 200 | | EX.EXTRT | Pre-existing |
| EX | EXDOSE | Dose per Administration | float | 200 | | EX.EXDOSE | Pre-existing |
| EX | EXDOSU | Dose Units | text | 200 | | EX.EXDOSU | Pre-existing |
| EX | EXDOSFRM | Dose Form | text | 200 | | EX.EXDOSFRM | Pre-existing |
| EX | EXDOSFRQ | Dose Frequency | text | 200 | | EX.EXDOSFRQ | Pre-existing |
| EX | EXROUTE | Route of Administration | text | 200 | | EX.EXROUTE | Pre-existing |
| EX | EXSTDTC | Start Date/Time of Exposure | datetime | 200 | BESTDTC | EX.EXSTDTC | Pre-existing |
| EX | EXENDTC | End Date/Time of Exposure | datetime | 200 | BESTDTC | EX.EXENDTC | Pre-existing |
| ADSL | STUDYID | Study Identifier | text | 200 | | Study ID from protocol | Assigned |
| ADSL | USUBJID | Unique Subject Identifier | text | 200 | | DM.USUBJID | Pre-existing |
| ADSL | TRT01P | Planned Treatment Group | text | 200 | | DM.ARM | Pre-existing |
| ADSL | TRT01A | Actual Treatment Group | text | 200 | | DM.ARM | Pre-existing |
| ADSL | TRTSDT | First Date of Treatment | date | 200 | DATE9. | EX.EXSTDTC | Derived |
| ADSL | TRTEDT | Last Date of Treatment | date | 200 | DATE9. | EX.EXENDTC | Derived |
| ADSL | AGE | Age | integer | 8 | | DM.AGE | Pre-existing |
| ADSL | SEX | Sex | text | 1 | | DM.SEX | Pre-existing |
| ADSL | RACE | Race | text | 200 | | DM.RACE | Pre-existing |
| ADSL | DTHFL | Subject Death Flag | text | 1 | | DM.DTHFL | Pre-existing |
| ADSL | EOSSTT | End of Study Status | text | 200 | | DS.DSDECOD | Derived |
| ADAE | USUBJID | Unique Subject Identifier | text | 200 | | AE.USUBJID | Pre-existing |
| ADAE | AETERM | Adverse Event Term | text | 200 | | AE.AETERM | Pre-existing |
| ADAE | AESER | Serious Adverse Event | text | 1 | | AE.AESER | Pre-existing |
| ADAE | AEREL | Causality | text | 200 | | AE.AEREL | Pre-existing |
| ADAE | AESEV | Severity/Intensity | text | 8 | | AE.AESEV | Pre-existing |
| ADAE | ASTDT | Start Date of Adverse Event | date | 200 | DATE9. | AE.AESTDTC | Pre-existing |
| ADAE | AENDT | End Date of Adverse Event | date | 200 | DATE9. | AE.AEENDTC | Pre-existing |
| ADAE | TRTEMFL | Treatment Emergent Flag | text | 1 | | ADSL.TRTSDT, ADSL.TRTEDT, AE.AESTDTC | Derived |
| ADVS | USUBJID | Unique Subject Identifier | text | 200 | | VS.USUBJID | Pre-existing |
| ADVS | PARAMCD | Parameter Code | text | 8 | | VS.VSTESTCD | Derived |
| ADVS | PARAM | Parameter Name | text | 200 | | VS.VSTEST | Derived |
| ADVS | AVAL | Analysis Value | float | 200 | | VS.VSORRES | Pre-existing |
| ADVS | BASE | Baseline Value | float | 200 | | VS.VSORRES | Derived |
| ADVS | CHG | Change from Baseline | float | 200 | | AVAL - BASE | Derived |
| ADVS | PCHG | Percent Change from Baseline | float | 200 | | (AVAL - BASE) / BASE * 100 | Derived |
| ADVS | ADT | Analysis Date | date | 200 | DATE9. | VS.VSDTC | Pre-existing |
| ADVS | AVISIT | Visit | text | 200 | | Derived from VSDTC relative to TRTSDT | Derived |
| ADVS | TRT01P | Treatment Group | text | 200 | | ADSL.TRT01P | Pre-existing |
| ADLB | USUBJID | Unique Subject Identifier | text | 200 | | LB.USUBJID | Pre-existing |
| ADLB | PARAMCD | Parameter Code | text | 8 | | LB.LBTESTCD | Derived |
| ADLB | PARAM | Parameter Name | text | 200 | | LB.LBTEST | Derived |
| ADLB | AVAL | Analysis Value | float | 200 | | LB.LBORRES | Pre-existing |
| ADLB | BASE | Baseline Value | float | 200 | | LB.LBORRES | Derived |
| ADLB | CHG | Change from Baseline | float | 200 | | AVAL - BASE | Derived |
| ADLB | ABLFL | Baseline Flag | text | 1 | | Y if record is at baseline visit | Derived |
| ADLB | ANRIND | Abnormal Flag | text | 200 | | HIGH/LOW/NORMAL based on LBNRIND | Derived |
| ADLB | ADT | Analysis Date | date | 200 | DATE9. | LB.LBDTC | Pre-existing |
| ADLB | TRT01P | Treatment Group | text | 200 | | ADSL.TRT01P | Pre-existing |

---

## 七、资源与链接

### 7.1 官方文档

| 文档 | 链接 |
|------|------|
| **CDISC define.xml 3.1 标准** | [CDISC Library](https://www.cdisc.org/standards/foundational/define-xml) |
| **define.xml 3.1 实施指南** | [CDISC define-xml Implementation Guide](https://www.cdisc.org/standards/foundational/define-xml/define-xml-3-1) |
| **Pinnacle 21 Community** | [pinnacle21.com](https://pinnacle21.com/products/community) |
| **CDISC Validator** | [CDISC Validator](https://www.cdisc.org/tools/validator) |

### 7.2 R 包资源

| 包 | 说明 | 链接 |
|------|------|------|
| **{xportr}** | CDISC 官方 define.xml 生成包 | [GitHub](https://github.com/pharmaverse/xportr) |
| **{admiral}** | CDISC 官方 ADaM 构建包 | [GitHub](https://github.com/pharmaverse/admiral) |
| **{pharmaversesdtm}** | CDISC 示例数据 | [GitHub](https://github.com/pharmaverse/pharmaversesdtm) |
| **{haven}** | 读取/写入 .xpt 文件 | [CRAN](https://cran.r-project.org/package=haven) |

### 7.3 GitHub 实战项目

| 项目 | 说明 | 链接 |
|------|------|------|
| **LiamHobby/Admiral-Hackathon** | 完整 SDTM → ADaM → define.xml 流程 | [GitHub](https://github.com/LiamHobby/Admiral-Hackathon) |
| **rogerjdeangelis/utl-end-to-end-cdisc** | 端到端 CDISC 处理 | [GitHub](https://github.com/rogerjdeangelis/utl-end-to-end-cdisc-SDTM-ADaM-processing) |
| **pharmaverse/xportr** | define.xml 生成官方包 | [GitHub](https://github.com/pharmaverse/xportr) |

---

## 八、关键要点总结

| 要点 | 说明 |
|------|------|
| **define.xml 是必需文件** | FDA/EMA 提交必须包含，描述所有变量来源和类型 |
| **版本要求** | 当前 FDA 要求 define.xml 3.1 版本 |
| **追溯性** | 每个变量必须标注来源（Pre-existing/Derived/Assigned） |
| **R {xportr}** | CDISC 官方推荐工具，与 {admiral} 配套使用 |
| **SAS 宏** | 工业界 80%+ 使用，有成熟宏方案 |
| **Pinnacle 21** | 官方验证工具，免费社区版可用 |
| **变量标签** | 所有变量必须有 label，便于审核和复用 |
| **CodeList** | 代码化变量必须定义枚举值和标签 |

---

## 九、与现有笔记的关联

| 已有笔记 | define.xml 关联 |
|----------|----------------|
| [SDTM-详解.md](./SDTM-详解.md) | define.xml 描述 SDTM 数据集的变量定义和来源 |
| [ADaM-详解.md](./ADaM-详解.md) | define.xml 描述 ADaM 衍生变量的计算逻辑和追溯链 |

---

*最后更新：2026-06-25*  
*来源：CDISC 官方文档 + GitHub 实战项目 + Pinnacle 21 验证指南*  
*下一步：实践 generate_full_define_xml() 管道，生成实际项目的 define.xml*