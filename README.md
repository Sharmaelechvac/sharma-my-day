# Sharma My Day

Sanjay's daily route sheet: https://sharmaelechvac.github.io/sharma-my-day/ (GitHub Pages, served from `docs/`).

The page is behind the same passcode lock as Sharma AR and Sharma P&L (`docs/lock.js`).
All day data is published only as `docs/day.enc.json` (AES-GCM 256, key from PBKDF2-SHA256,
600,000 iterations). After 5 wrong codes, and every 5 after that, office@ gets a Formspree email
with the app name, time and device. The code is never stored in this repo. Sanjay gives it out.

**Never commit or upload** `data.json`, `tasks.json`, `archive/*.json` or a PDF to `docs/`.
Those URLs are public. Plain files only live in `private/`, which is in `.gitignore`.

## How to publish a day

1. Decrypt the current data into `private/`:
   `SHARMA_PASSCODE=... python3 tools/encrypt.py --decrypt`
   (or leave the variable unset and type the code at the hidden prompt)
2. Edit the plain files, same schema as before:
   - `private/data.json`: `date`, `dayLabel`, `start`, `updatedAt`, `stops[]`
     (`title`, `address`, `start`, `end`, `driveFromPrev` minutes from the previous stop, or from
     `start` for the first stop, `note`, `who`, `materials[]`, optional `trackUrl`, `livingSf`,
     `underRoofSf`, and a new optional `purpose`), `inspections[]` (`time`, `type`, `address`,
     `permit`, `inspector`, `contact`, `note`)
   - `private/tasks.json`: `{ "date": ..., "tasks": [{ "text": ... }] }`
   - To save a day for the week picker: `private/archive/<date>.json` = `{ "data": ..., "tasks": ... }`
     and add it to `private/archive/index.json` (`liveDate`, `days[]`).
3. Encrypt: `SHARMA_PASSCODE=... python3 tools/encrypt.py` writes `docs/day.enc.json`.
4. Commit **only** `docs/day.enc.json`.

Page rules: a stop with no `who`, no `purpose` and no real note shows a gold
"Purpose / contact not set" flag. A task that repeats an inspection's permit # is hidden
(the inspection shows under Inspections). Personal items (insurance, bank, policy numbers)
don't belong on this page.

Paper sheet: `python3 make_pdf.py` reads `private/data.json` and writes the PDF to `private/`
(local only). On the phone, the Print / PDF button prints the page itself.
