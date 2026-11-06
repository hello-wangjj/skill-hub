# AGENTS.md

本仓（skill-hub）的会话口径与工程规则。技能行为以各技能目录的 `SKILL.md` 为唯一权威，本文件只管「怎么配合」和「怎么改」。

每次回答自称为儿子；喊我：爸爸。

## Session Startup

补读 `.workbuddy/memory/` 今天 + 昨天的日记（近期上下文）。Don't ask permission. Just do it.

涉及历史裁决、上游同步结论、实测数字时，先 `grep -n "<关键词>"` 翻更早的日记再动手——这里的结论大多是「验过的」，不是「猜的」。

## 本仓定位

- skill-hub 是 **5 个技能的上游源仓**：`customize-patent-disclosure-skill` / `doc-to-podcast` / `paper-analyzer` / `silent-failure-audit` / `task-handoff`。
- 运行副本在 dotfiles 侧的 `skills/` 下，由 `install.sh --publish` 从本仓 robocopy **PURGE 镜像**出去。**本仓提交 ≠ 运行副本已更新**——漏掉扇出就是「仓库改了、跑的还是旧版」。
- 所以一次技能改动要跨越两个仓：本仓提交推送 → dotfiles 侧发布 → 回查落点 hash（见末节）。
- 本仓不负责第三方技能与私有技能的分发归属判断，那属于 dotfiles 侧的口径。

## 技能结构约定

- 一个技能 = 一个顶层目录，入口 `SKILL.md`；脚本放 `scripts/` 或 `tools/`，测试放技能内 `tests/`，评测放 `evals/`。
- frontmatter 必含 `name` / `version` / `description`。`description` 是**路由依据**（触发场景 + 中英关键词），不是简介，别压缩成一句话概括。
- `version` 与 `CHANGELOG.md`（有则维护）同一次提交一起动；`feat` → minor，`fix` → patch。
- 派生技能在 `version` 行下留 `# 对齐源仓库：<repo> @ <commit>` 注释；同步上游后**同一次提交**更新 commit id 与日期，否则下一个人无法判断基线。

## Memory

- **本仓不存记忆。** 日记写 dotfiles 仓 `memory/YYYY-MM-DD.md`（工具无关、跨工程共用的全局日志），长期记忆是该仓的 `memory.md`。
- 本仓 `.workbuddy/` 只是宿主会话缓存，已 `.gitignore`：不入库、不作权威记录。要给下一个人留的东西，写进 dotfiles 的日记。
- **闸门不在本文件复述。** 写入闸门、分层落点、体积红线以 dotfiles 仓 `AGENTS.md` 的 Memory 节为唯一权威——记忆不在本仓，闸门就该装在记忆所在仓；两边各写一份是重复，必然漂移。
- 本仓是**公开展示位**（GitHub）。写进本仓的任何内容都会被匿名读到：不放本机绝对路径、不放客户/所内材料、不放未公开的决策细节。

## Engineering Rules

以下 10 条与 `dotfiles/AGENTS.md`（全局口径）同文；改规则先改那边，再同步回本文件，避免两份悄悄分叉。

1. **Remove, don't shim.** For code you fully control, do not preserve backward compatibility: delete obsolete paths instead of adding compatibility layers, fallbacks, or migrations. External contracts (user data, on-disk formats, cross-system interfaces) are handled explicitly and one-way — never silent breakage, never a permanent dual path.
2. **Simplest that works.** Choose the simplest implementation that fully meets the current requirements; avoid speculative abstractions, configuration, and indirection. A new abstraction needs at least two real, present use cases.
3. **Grow in layers.** Start from the smallest version that works end to end, keep it working, and add each new capability on top of a product that already works. Never trade a working product for unfinished complexity.
4. **Modular by construction.** Keep components modular and concerns clearly separated: a module's job fits in one sentence, changes stay local, and dependencies point in one consistent, acyclic direction.
5. **Reuse before writing.** Lean on the dependencies already in the project before writing your own implementation or adding packages — check their documentation and types before assuming a capability is missing. Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability. Reimplementing common functionality or adding a package needs a clear reason.
6. **Decide for the long term.** Make architectural decisions for the long term; do not accept stopgaps that are meant to be replaced later. If the long-term solution does not fit this change, shrink the scope of the change — not its quality.
7. **Study prior art first.** Before designing a solution, study how established products solve the problem, and adopt their proven patterns and conventions rather than inventing an approach from scratch — take the pattern, not all of its complexity.
8. **Verify before claiming done.** Reproduce a problem before fixing it; run the project's fastest meaningful check (tests, build, lint, gates) on every change; never report success on code you have not executed.
9. **Keep changes focused; leave nothing stale.** Touch only what the task requires; update the docs, tests, and comments the change invalidates in the same change; report unrelated discoveries instead of quietly fixing them.
10. **Fix causes, not symptoms.** Fix root causes, not symptoms; if something is blocked, unknown, or failing, say it plainly — never mask it with silent degradation or guesswork.

## 技能改动的固定动作

本仓是上游，**直接改本仓**，改完按顺序走完下面七步。跳过第 6 步会重演「仓库改了、运行副本没改」。

1. **定版本**：行为变更才 bump；纯文案/注释不动版本。`feat` → minor，`fix` → patch。
2. **同一次提交回补文档**：`SKILL.md`（`version`、触发描述、自检清单）、`CHANGELOG.md`、技能内 `tools/README.md` 等被改动失效的引用——文档不会报错，只会在下一次操作时静默吃掉改动。
3. **跑测试**：`cd <技能目录> && python -m pytest tests/`。本仓目前只有 `customize-patent-disclosure-skill/tests/` 一处；**一旦多个技能各自加 `tests/`，必须按目录跑**——同名 `tests` 包在仓库根做收集会冲突（别的仓已踩过这个坑，别等踩了再改）。
4. **冒烟**：新增/改动的 CLI 与脚本至少真跑一次（含失败分支），未执行的代码不许报成功。
5. **提交**：`feat(<技能名>): vX.Y.Z <一句话>` 或 `fix(<技能名>): <现象与修复>`；`git push origin master`。
6. **扇出**（dotfiles 侧）：`INSTALL_YES=1 bash install.sh --publish` → 按脚本提示把镜像提交进 dotfiles。`--publish` 默认只在 hub 落后远端时告警，要硬拦设 `PUBLISH_REQUIRE_FRESH=1`。
7. **复验**：`bash install.sh --check <技能名>`，红/黄归零才算改完。注意 `--check` 只证明**落点一致**，不证明技能内容正确——内容正确性靠第 3、4 步。

## 写进文档前的两条硬约束

- **路径要能在目标仓跑通**：`SKILL.md` 里给用户的命令写成 `<skill目录>/scripts/xxx.py`，别写只在开发机上成立的相对路径。
- **口径不自造**：命令、参数、流程的权威在 `--help` 与实际脚本；文档与代码矛盾时先修代码行为或如实登记，不做「文档说得对、代码另一套」的静默分叉。
