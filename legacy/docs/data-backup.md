# Data backup and export

The tracker keeps its database in the add-on's `/data` directory. Nothing in
the normal tracking workflow is sent to an external service.

## Profile export

Open **Settings** and choose **Download Profile Export**. The downloaded JSON
contains the active profile, cycles, temperatures, signs, symptoms, and
computed insights. Store it somewhere encrypted and private.

Exports are intended for recovery and portability. Import is deliberately not
available yet; it will be added only with validation and an explicit preview
to prevent accidental overwrites.

## Full add-on backup

Use a Home Assistant backup that includes this add-on. That preserves the
complete `/data/bbt.db` database, including every profile. Test restoration on
a non-production Home Assistant installation before relying on a backup.

Do not share raw exports or database files: they contain sensitive
reproductive-health information.
