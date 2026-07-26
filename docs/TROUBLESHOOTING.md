# Troubleshooting

## White page / blank screen

If the Web UI shows a blank white page after the add-on starts:
1. Wait 10 seconds for the add-on to fully initialize
2. Refresh the page
3. Check the add-on logs in Home Assistant Supervisor

## "No active profile found"

Create a profile first:
1. Go to Profiles in the navigation
2. Click "New Profile"
3. Enter a name and select temperature unit
4. Click Create

## API errors / "Unable to load"

This usually means no data exists yet. Log your first entry:
1. Go to Log Entry
2. Enter today's temperature
3. Optionally add signs (mucus, OPK, symptoms)
4. Click Save

## Entity not showing in Home Assistant

Entities are published after each entry is logged. To force a refresh:
1. Go to Settings
2. Click "Reanalyze Insights"
3. Entities will update within a few seconds

## BYRD_SECRET_KEY warning

If you see a warning about the default secret key, add a custom key:
1. Stop the add-on
2. Add to add-on options or set environment variable `BYRD_SECRET_KEY`
3. Start the add-on
