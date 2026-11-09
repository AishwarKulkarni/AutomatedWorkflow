---
name: update-instructions
description: Research and revise existing Notch app guides in instructions/ when an app, interface, shortcut, workflow, or target changes. Preserve useful content and verify claims against current authoritative sources.
---

# Update Existing Notch App Instructions

Use this skill when the user asks to update, modify, correct, refresh, or extend an existing app guide in `instructions/`. This skill maintains existing guides; use `create-automation` when the user wants a new app guide.

## Inspect the existing guide and app support

1. Identify the exact guide or guides the user means. Read each whole file before editing. If the user asks to update all existing guides, inventory the directory and process them individually.
2. Check the guide's frontmatter, filename, scope, and links to related instruction files. Preserve its identity and valid metadata unless the app identity has changed or the user asked for a rename.
3. Inspect `.agents/context/ahk_manifest.md` and `src/automation/autohotkey/apps.ahk` for the registered target, window matcher, launch path, and supported actions. Inspect related runtime code only when the requested change depends on how instructions are loaded or used.
4. Identify what changed: app/product identity, version/platform, interface, shortcuts, feature behavior, safety constraints, or the local app target. Avoid rewriting unrelated parts of the guide.

## Research before changing factual guidance

- Research app behavior and keyboard shortcuts against current, authoritative sources. Prefer official vendor documentation, release notes, and shortcut references. Browse when the change may have occurred since the guide was written or official material is not already available.
- Verify that each shortcut belongs to the exact product surface and operating system in the guide. Apps with similarly named desktop, web, IDE, CLI, or classic/new versions require separate treatment.
- Include direct source links in the guide near a Sources section. State platform/version limits and mark uncertain or customizable mappings. Do not preserve an outdated claim merely because it is already in the guide.
- When official sources do not cover a detail, use a reputable secondary source only if needed, label it, and avoid relying on it for consequential steps when uncertainty remains.

## Make a focused, safe edit

- Update only the requested guide and necessary supporting references. Preserve accurate, useful material and the guide's established naming/frontmatter contract.
- Keep instructions app-focused: explain the interface, reusable operations, verified shortcuts, and recovery/safety conditions. Do not turn an app guide into blanket authorization for every task in that app.
- Name only app targets and actions that exist in the manifest and implementation. If the guide concerns an unregistered application, keep that limitation explicit. Add a target or action only when the user requests onboarding or supplies clear authorization and the implementation details are known.
- Keep separate products separate even when they share a brand, codebase, or similar interface. Never transfer shortcuts or operating steps across products without confirmation from product-specific sources.
- Preserve fail-fast desktop safety: confirm app focus and relevant project/document/account before action; stop when the next operation could affect the wrong context or data.
- If requested updates reveal that two guides substantially duplicate one another, preserve the useful content and propose or make a minimal consolidation only when the user's scope clearly includes structure cleanup. Do not delete an existing guide merely to simplify the directory.

## Keep project context accurate

When the edit changes app targets, actions, runtime behavior, dependencies, or architectural boundaries, update `.agents/context/ahk_manifest.md`, `CONTEXT.md`, or other source-of-truth docs required by `AGENTS.md`. A guide-only correction normally needs no architecture update.

## Review before finishing

Check that the edited guide:

- Has valid single-line `name` and `description` frontmatter, with its filename and name still aligned.
- Covers the intended product and platform, without mixing separate app surfaces.
- Has current, sourced shortcut and behavior claims with version/platform limits where relevant.
- Uses registered targets/actions accurately and includes safe, clear operation and stop conditions.
- Contains no stale links or contradictory duplicate statements introduced by the edit.

Summarize which guides changed and the research sources used. State any app support limitation or unverified assumption plainly. Do not claim runtime verification unless it was performed.
