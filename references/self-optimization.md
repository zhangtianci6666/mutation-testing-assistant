# Self-Optimization Hook (自动优化机制) — Full Steps

After every completed PIT run — whether on a new project or an existing one — execute this workflow. The skill learns from each project and grows its knowledge base automatically.

**Version number bumps ONLY ONCE per calendar day.** Multiple self-optimization cycles within the same day share the same version number. The changelog accumulates all same-day changes under that single version entry.

**⛔ CRITICAL: After project completion (all classes done), execute the FULL REFERENCE AUDIT (Step 5 new) — review ALL reference files for corrections, not just the file with new knowledge. Adding new knowledge without correcting existing errors accumulates rot.**

---

## Step 1: Run the Post-Mortem Analysis

Fill out this structured analysis template based on the completed PIT run:

```
## Post-Mortem: {PROJECT_NAME}

### Basic Stats
- Project: {name}
- Type: {algorithmic|GUI|CLI|data-structure|etc}
- Total mutants: {N}
- Killed: {N} ({X}%)
- Equivalent mutants identified: {N}
- Final mutation coverage: {X}%
- Time spent: {N} minutes

### Survivor Breakdown
| Mutator | Survived | Equivalent? | Pattern Match | Action |
|---------|----------|-------------|---------------|--------|

### New Discoveries (if any)
- [ ] New equivalent mutant pattern found?
- [ ] New killing technique discovered?
- [ ] Existing pattern needs correction?
- [ ] New test pattern invented?

### Skill Knowledge Gap Analysis
- Which survivors did the skill NOT predict? Why?
- Which predicted patterns were WRONG for this project?
- What project-specific knowledge should be generalized?

### Coverage Statistics Update
- New entry for project-data.json
```

## Step 2: Determine Update Type

| Condition | Action | Tool |
|-----------|--------|------|
| New equivalent pattern discovered | Add to references/survival-patterns.md, assign next Pattern ID | Edit |
| New killing technique found | Add to references/survival-patterns.md Killing Techniques section | Edit |
| Existing pattern confirmed correct | No change needed | - |
| Pattern description inaccurate | Update pattern section with correction | Edit |
| New test pattern invented | Add to references/test-patterns-catalog.md | Edit |
| New project completed | Add to references/project-case-studies.md, update stats | Edit |
| New project completed | Add entry to project-data.json | Edit |
| Common Mistakes table has gap | Add new row to references/common-mistakes.md | Edit |
| Quick Reference table has gap | Add new row to SKILL.md Quick Reference | Edit |

## Step 3: Execute the Update

For each action identified in Step 2, apply the edit IMMEDIATELY after the PIT run completes. Do NOT wait for user to ask.

## Step 4: Determine Version Bump

Follow **strict semantic versioning** (vMAJOR.MINOR.PATCH). Current version is in [project-data.json](../project-data.json) -> `skill_metadata.version`.

- **PATCH (vX.Y.Z -> vX.Y.Z+1):** Bug fixes, corrections, stats-only updates
- **MINOR (vX.Y.Z -> vX.Y+1.0):** New project case, new pattern, new test pattern
- **MAJOR (vX.Y.Z -> vX+1.0.0):** Fundamental restructuring, breaking changes

| Delta Type | Bump |
|-----------|------|
| Stats update only (new project, no new patterns) | PATCH |
| New project + confirmed existing patterns only | PATCH |
| Minor correction to existing pattern text | PATCH |
| New equivalent mutant pattern (Pattern N+1) | MINOR |
| New killing technique | MINOR |
| New test pattern in Test Patterns Catalog | MINOR |
| New Iron Rule or workflow restructure | MINOR |
| Multiple MINOR-level changes in one update | MINOR (once) |
| Breaking restructuring of entire sections | MAJOR |

**Rule:** Same-day session updates the version number ONLY ONCE. All changes within the same calendar day are grouped under a single version bump. Version numbers are strictly sequential.

## Step 5: PROJECT-COMPLETION FULL REFERENCE AUDIT (MANDATORY)

**After ALL classes in a project are done, BEFORE declaring project finished:**

Review EVERY reference file — not just the one with new knowledge. For each file, answer:
- Is anything WRONG based on what we learned?
- Is anything MISSING that this project revealed?
- Are cross-references between files still consistent?

| File | Check |
|------|-------|
| `survival-patterns.md` | Any pattern description inaccurate? Missing variant? Wrong action? |
| `killing-strategies.md` | Any strategy insufficient? Code example doesn't actually kill? Missing sub-technique? |
| `test-patterns-catalog.md` | Any pattern code buggy? Missing critical rule? New pattern to add? |
| `common-mistakes.md` | Any mistake we made not listed? Any listed fix wrong? Red flags complete? |
| `bplustree-testing.md` | (if tree project) Rules need refinement? New assertion level? |
| `awt-gui-testing.md` | (if GUI project) Patterns wrong? New headless workaround? |
| `pit-metrics.md` | Diagnostic matrix accurate? Project comparison table updated? |
| `SKILL.md` | Quick Reference table correct? Overview counts accurate? Iron Rules complete? |
| `project-data.json` | Version bumped? Stats recalculated? Changelog accurate? |
| `README.md` | Counts accurate? Project table updated? Outdated claims corrected? |
| `CHANGELOG.md` | New version entry complete? Corrections listed, not just additions? |

**"Nothing to fix" is valid ONLY after you've actually READ and VERIFIED each file.**

## Step 6: Update CHANGELOG.md

Append a changelog entry with the correct bumped version:

```
## [v{NEW_VERSION}] - {DATE}
### Added
- {Project} project case study ({N} mutants, {X}% killed)
- Pattern {N}: {name} ({category})

### Changed
- {What was modified and why}

### Verified
- {Which existing patterns were confirmed by this project}
```

## Step 7: Update README.md

**Every time** the skill is modified, update these README.md fields:

| README Field | When to Update |
|-------------|---------------|
| Header: "X 个项目、Y 个变异体" | New project added |
| "提炼自 X 个真实 Java 项目" | New project added |
| "N 个已知存活模式" | New pattern added (MINOR bump) |
| "N 个测试模式" | New test pattern added |
| "N 种真等价变异体" | New equivalent pattern added |
| "N 条 Iron Rules" | New Iron Rule added |
| Project data table | Stats change |
| `skill.md (XXXX 行)` | skill.md line count changes |
| `N 步完整工作流` | Workflow steps change |
| `N+ 个高频踩坑点` | Common Mistakes grow |

## Step 8: Update project-data.json version

In `skill_metadata.version`, set the new version string and update `last_updated` to the current timestamp.

---

## Auto-Optimization Trigger Checklist

After EVERY completed PIT run, verify in order:
- [ ] Post-mortem template filled
- [ ] All survivors matched to known patterns OR new patterns created
- [ ] Equivalent mutants documented with proof (Iron Rule 9 format)
- [ ] Version bump determined (semantic versioning)
- [ ] CHANGELOG.md updated with new version entry
- [ ] project-data.json updated (new project stats + version + timestamp)
- [ ] If new pattern: references/survival-patterns.md + SKILL.md Quick Reference updated
- [ ] If new test pattern: references/test-patterns-catalog.md updated
- [ ] Overview statistics recalculated
- [ ] README.md updated (all affected fields)

## Delta Detection: When to Actually Edit the Skill

You ONLY need to edit when there's a DELTA — something the skill doesn't already know:

| Situation | Delta? | Action | Version |
|-----------|--------|--------|---------|
| Survivor matches Pattern 1-20 exactly | NO | Document in post-mortem only | PATCH |
| Survivor matches a pattern but with a new sub-type | YES | Add sub-type to existing pattern | PATCH |
| Survivor requires a completely new pattern | YES | Create Pattern N+1, update README | MINOR |
| All survivors already covered by skill | NO | Just update project-data.json stats | PATCH |
| Skill's prediction was wrong for a mutant | YES | Correct the pattern description | PATCH |
| Found a more efficient killing method | YES | Update the pattern's killing strategy | MINOR |

**Iron Rule for self-optimization: Add knowledge, don't duplicate it.** If the skill already explains how to handle a situation, don't add another explanation.
