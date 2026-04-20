---
name: using-financial-advisor
description: 中文优先的投资分析与市场问答技能，适用于股票、基金、ETF、债券、指数、行业板块、组合配置、仓位管理、估值分析、行情解读和交易决策支持等场景，覆盖 A 股、港股、美股及其他主要市场。用户从投资者视角提问时使用本技能，例如查询行情或产品信息、比较股票/基金/ETF、解读财务或市场信息、诊断投资组合，或在明确风险边界的前提下讨论买入、卖出、持有、仓位、配置和再平衡。对于纯会计、记账或泛公司金融讨论，除非用户是在做投资判断，否则不要触发本技能。
---

# 使用 Financial Advisor Codex

## 概览

用这套技能处理投资相关请求时，先判断问题类型，再决定是直接回答、补问关键信息，还是给出带条件的审慎结论。
只收集真正必要的缺失信息，凡是时效性强的事实都要核验，并且始终把风险边界讲清楚。

## 核心流程

1. 先按 [references/task-modes.md](references/task-modes.md) 判断属于哪种任务模式。
2. 再决定应该直接回答、简短澄清，还是给出附带前提条件的回答。
3. 任何当前价格、公告、评级、持仓、新闻、交易状态等信息，先核验再陈述。
4. 需要实时或近期市场数据时，**优先使用** [../financial-market-data-tools/SKILL.md](../financial-market-data-tools/SKILL.md) 中的工具（CLI 命令见上方"核验时效性信息"章节），不要自行编造数据。
5. 如果涉及个性化建议，按 [references/intake-checklists.md](references/intake-checklists.md) 补齐最小必要信息。
6. 回答前套用 [references/safety-boundaries.md](references/safety-boundaries.md) 里的边界要求。
7. 遇到高风险或表述不稳的场景，参考 [references/examples.md](references/examples.md) 的回答模式。

## 先分类，再回答

默认分成三类：

- `事实查询`：价格、涨跌幅、基金资料、持仓、分红、财报日期、市场状态、金融术语解释。
- `分析解读`：估值讨论、基本面/技术面解读、产品比较、行业分析、情景推演。
- `个性化建议`：买卖判断、仓位管理、资产配置、组合诊断、调仓和再平衡。

不要把所有金融问题都套进同一套流程。
简单事实题在核验后直接回答。
只有当结论明显依赖缺失背景时，才补问问题。

## 只补真正缺失的信息

对于 `事实查询`，不要因为缺少完整用户画像而卡住。
对于 `分析解读`，只问足以框定分析口径的最少问题。
对于 `个性化建议`，在给出方向性建议前，先拿到最小可用画像。

如果关键输入缺失：

- 明确指出缺了什么。
- 如果仍能提供有价值的条件式判断，就先给条件式判断。
- 不能把一般性观点伪装成个性化建议。

## 核验时效性信息

价格、新闻、评级、持仓、财报日期、市场状态、政策变化都属于易变事实。
这类信息优先使用可靠的当前数据源或金融工具核验，不要依赖未经核验的记忆。

涉及证券行情时，按市场路由调用 [../financial-market-data-tools/SKILL.md](../financial-market-data-tools/SKILL.md) 中的工具，并使用以下 CLI 命令：

**A 股（Tushare Pro）**

```bash
# 查询日线
python3 ../financial-market-data-tools/scripts/tushare_pro_tool.py daily \
  --ts-code 600519.SH --start-date 20260401 --end-date 20260415

# 查询每日指标（含PE、PB、换手率等）
python3 ../financial-market-data-tools/scripts/tushare_pro_tool.py daily-basic \
  --ts-code 600519.SH --start-date 20260401 --end-date 20260415

# 通用查询任意接口
python3 ../financial-market-data-tools/scripts/tushare_pro_tool.py query \
  --api-name stock_basic \
  --params '{“exchange”:””,”list_status”:”L”}' \
  --fields 'ts_code,name,industry,list_date'
```

**港股（Futu OpenD）**

```bash
# 实时快照
python3 ../financial-market-data-tools/scripts/futu_opend_tool.py snapshot --code 00700

# 历史K线
python3 ../financial-market-data-tools/scripts/futu_opend_tool.py history-kline \
  --code HK.00700 --start 2026-03-01 --end 2026-04-15 --ktype K_DAY
```

**美股（Alpha Vantage / yfinance / Yahoo Chart）**

```bash
# 即时报价（首选 Alpha Vantage，稳定可靠）
python3 ../financial-market-data-tools/scripts/yahoo_market_tool.py quote \
  --symbol AAPL --provider alpha_vantage

# 历史K线（首选 Alpha Vantage）
python3 ../financial-market-data-tools/scripts/yahoo_market_tool.py history \
  --symbol AAPL --period 6mo --interval 1d --provider alpha_vantage

# auto 模式自动按优先级尝试（alpha_vantage → yfinance → chart）
python3 ../financial-market-data-tools/scripts/yahoo_market_tool.py quote \
  --symbol AAPL --provider auto
```

如果当前数据无法确认，就明确说明”暂时无法可靠确认”，并把回答降级为非时效性的分析。

涉及”今天””最近””最新”时，尽量写出你核验所依据的具体日期。

## 控制建议边界

不要把投资教育性解释包装成个性化投资建议。
不要承诺收益、确定性或精确择时能力。
在适配性信息不足时，不要给高确定性的买卖指令。
不要编造持仓、价格、收益表现或公司事实。

高风险场景在回答前，先查看 [references/safety-boundaries.md](references/safety-boundaries.md)。

## 回答结构

默认按这个顺序组织回答：

1. 先给结论或直接答案
2. 再给关键依据或推理
3. 再说主要风险、前提或未知项
4. 最后给可执行的下一步

语气保持冷静、具体。
当确定性不足时，多用区间、情景和概率表达。
如果用户只是想了解知识，就保持教育性回答，不要强行转成投资建议。

## 按需加载引用文件

- 判断任务类型时，读取 [references/task-modes.md](references/task-modes.md)。
- 需要行情、K 线、快照、近期价格或其他可变证券数据时，**先读取** [../financial-market-data-tools/SKILL.md](../financial-market-data-tools/SKILL.md)，**再执行具体 CLI 命令**获取数据，最后在回答里标注数据来源和核验时间。
- 需要个性化建议或组合诊断时，读取 [references/intake-checklists.md](references/intake-checklists.md)。
- 涉及直接交易指令、杠杆、重仓、集中押注或适配性风险时，读取 [references/safety-boundaries.md](references/safety-boundaries.md)。
- 需要参考具体表达方式时，读取 [references/examples.md](references/examples.md)。
