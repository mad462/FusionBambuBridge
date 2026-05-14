# Contributing

## Local Workflow

1. Edit files in this repository.
2. Refresh the installed Fusion add-in copy.
3. Run the add-in from Fusion.
4. Use the Text Commands window or message boxes to inspect behavior.

## Recommended Priorities

1. Add user-configurable settings storage in `lib/services/settings_service.py`.
2. Polish the Fusion command dialog to feel closer to the native print flow.
3. Add tests for pure-Python helper code before adding more features.
4. Tighten edge-case handling for unusual Fusion selection combinations.

## Coding Boundaries

- Keep Fusion API event handlers small.
- Put Windows-specific path and process logic in `bambu_launcher.py`.
- Do not let command modules grow into service modules.
- Prefer adding one small helper file over one giant add-in file.

## Testing Strategy

Not every part of a Fusion add-in is easy to automate outside Fusion, so keep the pure-Python surface area large:

- launcher behavior should stay unit-testable,
- settings parsing should stay unit-testable,
- export naming and selection normalization should stay unit-testable where possible.
