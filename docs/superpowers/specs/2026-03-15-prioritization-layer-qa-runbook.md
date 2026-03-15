# Prioritization Layer QA Runbook

Test the skill chains added by the prioritization layer. Each test is a prompt you type into a fresh swain session (or the current one). Verify the agent takes the expected action.

---

## Test 1: Meta-router recognizes Initiative

**Prompt:** `/swain create an initiative`

**Expected:** swain meta-router routes to swain-design. swain-design recognizes "initiative" as a valid artifact type and begins the creation workflow (asks for parent vision, title, etc.).

**Pass if:** swain-design responds with artifact creation questions, NOT with "I don't know what an initiative is" or routing to a wrong skill.

---

## Test 2: Initiative creation chains into brainstorming

**Prompt:** `I want to create an initiative to group my security epics`

**Expected:** swain-design detects Initiative as a full-ceremony artifact and invokes the brainstorming skill BEFORE drafting the artifact (per superpowers chaining rules in AGENTS.md).

**Pass if:** brainstorming skill is invoked first, asking clarifying questions about the strategic focus, scope, and child epics. NOT if swain-design skips brainstorming and immediately creates the artifact.

---

## Test 3: swain-status uses new recommendation format

**Prompt:** `/swain-status`

**Expected:** The agent summary leads with a Recommendation section that references vision context (not just unblock count). The recommendation should mention which vision the top item belongs to and its weight.

**Pass if:** Recommendation includes vision name/ID and weight context. NOT if it just says "Activate EPIC-017 — unblocks 1" without vision framing.

---

## Test 4: Focus lane routing

**Prompt:** `focus on security` or `I want to focus on VISION-001`

**Expected:** swain-session recognizes this as a focus lane request and invokes `swain-focus.sh set VISION-001` (or resolves "security" to the appropriate vision/initiative ID).

**Pass if:** Session state is updated (can verify with `swain-focus.sh` showing the set value). NOT if the agent just says "OK, noted" without actually setting the focus.

**Follow-up prompt:** `/swain-status`

**Expected:** Recommendations scoped to the focused vision. Other visions appear in "Meanwhile:" peripheral awareness.

**Pass if:** Recommendations are filtered. NOT if the full unscoped list appears.

---

## Test 5: Focus lane clear

**Prompt:** `clear my focus` or `stop focusing on security`

**Expected:** swain-session invokes `swain-focus.sh clear`.

**Pass if:** Focus is cleared (verify with `swain-focus.sh`).

---

## Test 6: swain-doctor migration advisory

**Prompt:** Start a new session (or invoke swain-doctor manually)

**Expected:** swain-doctor's preflight detects epics without `parent-initiative` and shows an advisory message like "23 epic(s) without parent-initiative — run initiative migration."

**Pass if:** Advisory appears in preflight output. NOT if it's silently ignored or causes a failure.

---

## Test 7: Vision weight update

**Prompt:** `set VISION-001 priority to high` or `update VISION-001 priority-weight to high`

**Expected:** swain-design updates the `priority-weight` field in VISION-001's frontmatter to `high`.

**Pass if:** Frontmatter is updated. Subsequent `/swain-status` shows items under VISION-001 with `vision_weight: 3` (high) in the recommendation scoring.

---

## Test 8: Mode inference

**Setup:** Have at least one spec in a review-needed state (agent completed implementation, needs sign-off).

**Prompt:** `/swain-status`

**Expected:** swain-status infers detail mode (specs awaiting review take priority per mode inference rules). Shows spec review recommendations instead of strategic vision-level decisions.

**Pass if:** Agent frames the output around specs needing review. NOT if it shows the full vision-mode strategic view when specs are pending.

**Note:** If no specs are in review state, vision mode is correct. This test requires specific artifact state to trigger.

---

## Test 9: Attention drift visibility

**Setup:** Ensure a Vision has `priority-weight: high` and no artifact transitions for 14+ days.

**Prompt:** `/swain-status`

**Expected:** Attention drift section appears in the output, noting the vision that hasn't been touched.

**Pass if:** Drift warning shows with days-since-activity and threshold.

**Note:** In a fresh project, this may not trigger. Test with `specgraph attention` CLI to verify the data pipeline works even if the threshold isn't met.

---

## Test 10: Peripheral awareness with focus

**Setup:** Set focus lane to VISION-001. Have decisions pending in other visions.

**Prompt:** `/swain-status`

**Expected:** After the recommendation (scoped to VISION-001), a "Meanwhile" section shows decision counts for other visions.

**Pass if:** Non-focus visions are summarized with decision counts. NOT if they're completely hidden or shown as full recommendations.

---

## Test 11: Artifact type selection — Initiative vs Epic vs Spec

The agent should infer the right artifact type from user intent without the user naming the type explicitly.

**Prompt A:** `I want to improve our security posture across the board`

**Expected:** Agent suggests creating an **Initiative** (strategic direction, likely spans multiple epics). NOT an Epic, NOT a Spec.

**Pass if:** Agent says something like "This sounds like a strategic initiative — let me create an Initiative artifact" or asks brainstorming questions framed around strategic focus.

---

**Prompt B:** `Build a vulnerability scanner that checks dependencies`

**Expected:** Agent suggests creating an **Epic** (single deliverable with specs). NOT an Initiative.

**Pass if:** Agent creates or offers to create an Epic.

---

**Prompt C:** `Add a --verbose flag to the specgraph recommend command`

**Expected:** Agent suggests creating a **Spec** (one implementation unit). NOT an Epic, NOT an Initiative.

**Pass if:** Agent creates or offers to create a Spec (possibly asks which Epic or Initiative to attach it to).

---

**Prompt D:** `I have EPIC-017, EPIC-023, and some upcoming security work — I want to group them together`

**Expected:** Agent suggests creating an **Initiative** and re-parenting the named Epics under it.

**Pass if:** Agent proposes an Initiative (not a Vision, not another Epic) and offers to add `parent-initiative` to the existing Epics.

---

**Prompt E:** `Fix the typo in the status output header`

**Expected:** Agent suggests creating a **Spec** with `type: bug`. May offer to attach to an Initiative as small work (no Epic needed).

**Pass if:** Agent creates a Spec, NOT an Epic or Initiative.

---

## Quick smoke test (covers Tests 1, 3, 4, 5)

Run these commands in sequence and verify each output:

```bash
# 1. Verify specgraph knows about Initiative
python3 skills/swain-design/scripts/specgraph.py status | grep INITIATIVE

# 2. Verify recommendation scoring works
python3 skills/swain-design/scripts/specgraph.py recommend

# 3. Verify focus lane works
bash skills/swain-session/scripts/swain-focus.sh set VISION-001
python3 skills/swain-design/scripts/specgraph.py recommend --focus VISION-001
bash skills/swain-session/scripts/swain-focus.sh clear

# 4. Verify attention tracking works
python3 skills/swain-design/scripts/specgraph.py attention

# 5. Verify swain-status includes priority data
bash skills/swain-status/scripts/swain-status.sh --refresh --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
p = d.get('priority', {})
print(f'Recommendations: {len(p.get(\"recommendations\", []))}')
print(f'Decision debt visions: {list(p.get(\"decision_debt\", {}).keys())}')
print(f'Drift alerts: {len(p.get(\"drift\", []))}')
print(f'Focus lane: {d.get(\"session\", {}).get(\"focus_lane\", \"none\")}')
"
```
