# What to send back

Three things. **The written explanation matters more to us than the patch.**

---

## 1. Your code

Push your work to a fork of this repo, or open a pull request against it — either is
fine. Include whatever you used to prove the fix works.

## 2. Your AI session transcript

Whatever your tool exports: a Claude Code session log, an exported Cursor or Copilot
chat, a saved conversation. Commit it as `TRANSCRIPT.md` or attach it to your email. If
your tool can't export cleanly, paste your prompts into a text file as you go.

To be clear about why we're asking: we are **not** checking whether you used AI. We
assume you did, and we would be more concerned if you hadn't. We're interested in how
you *direct* it — where you gave it context, where you pushed back, where you decided to
do something yourself. None of that is visible in a finished diff, and it's the skill
this team actually runs on.

## 3. `NOTES.md`

In the repo root. A few paragraphs, no particular format:

**1. Why did the bug happen?**
Explain the mechanism — what the code was doing, and why that broke once more than one
worker was running. Not the fix; the cause. *This is the question we read first and
think about hardest.* A correct patch with a hand-wavy explanation tells us less than a
partial fix you can explain precisely.

**2. How did you prove your fix works?**
What convinced you, and what would convince a skeptical reviewer?

**3. What else did you notice that you decided *not* to change?**
There are other things in this code worth commenting on. We're interested in what you
spotted and why you left it alone.

**4. What's still wrong after your fix?**
Something always is. Under real production conditions, what would still bite?

---

Send everything to **[your email]** by the date in your invitation. If you have a
question about the exercise, just ask — asking is not a mark against you.
