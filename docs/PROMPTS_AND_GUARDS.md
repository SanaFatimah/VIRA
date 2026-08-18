# Prompts, Manipulators, and guards

The executable prompts are retained directly in the agent source files so the
artifact does not provide a lossy prose reconstruction.

| Component | Source |
|---|---|
| Generator prompts | `src/agents/generator.py` |
| Attacker prompts | `src/agents/attacker.py` |
| Analyst prompts | `src/agents/analyst.py` |
| Vec-A and Vec-B templates | `src/agents/manipulator.py` |
| Machine-readable templates | `config/manipulator_templates.json` |
| Condition presets | `config/conditions.json` and `src/main.py` |

The no-evidence short circuit runs before the Analyst model when attacks,
CodeQL results, and previous findings are all absent. Guard A is distinct: it
operates after the Analyst model and validates its report against upstream
evidence. Guard B sanitizes patch feedback after the Vec-B interface and before
the next Generator prompt.
