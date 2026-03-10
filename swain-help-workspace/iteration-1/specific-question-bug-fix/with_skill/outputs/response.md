## Filing a Bug and Tracking the Fix

Two skills work together here: **swain-design** creates the bug artifact, and **swain-do** tracks the fix tasks.

### Step 1 -- File the bug

Say something like:

```
/swain file a bug: login fails when password contains special characters
```

Swain-design creates a **BUG-NNN** artifact in `docs/bug/Reported/` with severity, reproduction steps, and affected artifacts filled in from your description.

### Step 2 -- Plan the fix

When the bug moves from **Reported** to **Active**, swain automatically invokes swain-do to create a tracked plan with tasks. The first task it creates is always a **failing regression test** that reproduces the bug -- this anchors the fix to observable behavior.

You can also trigger the transition yourself:

```
/swain move BUG-001 to Active
```

### Step 3 -- Work the fix

Ask swain what to do next:

```
/swain what should I work on?
```

Swain-do returns the next unblocked task from the plan. Claim it, write the code, and mark it complete. Repeat until all tasks are done.

### Step 4 -- Resolve and verify

Once the fix is in place:

```
/swain move BUG-001 to Fixed
```

After you (or someone else) confirms the fix works:

```
/swain move BUG-001 to Verified
```

### Step 5 -- Commit

```
/swain push
```

### The full lifecycle at a glance

**Reported** --> **Active** (plan created, work begins) --> **Fixed** (code done) --> **Verified** (confirmed working)

There are also terminal states **Declined** (wontfix / by-design) and **Abandoned** (no longer relevant) if the bug doesn't need a fix.

---

Want me to file a bug now? Just describe the problem and I will hand it off to swain-design.
