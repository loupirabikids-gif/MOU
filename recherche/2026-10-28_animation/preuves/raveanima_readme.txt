EXTRAIT DOCUMENTAIRE — pas une copie intégrale
Source : https://raw.githubusercontent.com/vibecoderkz/raveanima/main/README.md
SHA256 de la réponse originale : 105f4242c3a0c698acf2999719666522d052fb8e4eaeea86269a1924f1799d62

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/readme-banner-dark.png">
    <img src="brand/readme-banner-light.png" alt="RaveAnima: a keyframe diamond with anime eyes" width="100%">
  </picture>
Desktop editor for 2D vector design and keyframe animation, built so that people and AI agents use the same tools.
An open-source, local-first alternative to Rive, with Lottie as a first-class export.
- **Draw**: rectangles, ellipses, polygons, stars, pen paths with editable points, text, images, groups, solid and gradient fills, strokes, trim paths. SVG import turns files into native editable shapes.
- **Animate**: timelines with loop / ping-pong, keyframes on any numeric or colour property, path morphing, easing presets and a cubic-bezier editor, auto-key in Animate mode, animation presets.
- **Export**: Lottie JSON (lottie-web, iOS, Android, Flutter, Skottie), a self-contained interactive HTML page, MP4, GIF, WebM with alpha, MOV, SVG, PNG.
- **For agents**: every action is a typed command with undo. Agents drive the open window live, or work headless without any window, through MCP or the CLI.
- Node.js 22.12 or newer and npm.
- `ffmpeg` on `PATH` for video and GIF export (CLI and desktop).
npx raveanima export hello.anima hello.png
npx raveanima export hello.anima hello.json     # Lottie
Commands: `new | inspect | run | batch | export | sheet | commands | guide | mcp`. The CLI bundle is committed at
`packages/headless/dist/anima.js`, so it works right after `npm install`; `npm run build` regenerates it.
## Agents (MCP)
claude mcp add raveanima -- node /path/to/raveanima/packages/headless/dist/anima.js mcp --live
claude mcp add raveanima-headless -- node /path/to/raveanima/packages/headless/dist/anima.js mcp
MCP tools: `anima_guide`, `command_list`, `command_run`, `command_batch`, `doc_inspect`, `doc_open`, `doc_import`,
`export`, `render_preview`, `render_contact_sheet`.
`raveanima export file.anima page.html` writes one self-contained page with the player inside. To embed it yourself,
Attributes: `src`, `state-machine`, `animation`, `fit` (`contain` or `cover`), `paused`.
`examples/` holds scripts that build documents only through commands, the same way an agent does over MCP:
| `packages/core` | Document model, command registry with undo, animation evaluation, state machines, renderer (Canvas2D API), SVG import, SVG and Lottie export. Pure TypeScript, no DOM needed. |
| `packages/headless` | Skia rendering (`@napi-rs/canvas`), ffmpeg video, the `raveanima` CLI and the MCP server. |
| `apps/desktop` | Tauri 2 app: React UI in the webview, Rust shell for files, video export and the agent bridge. |
| `replica/` | Clean-room recon of Rive (public docs and the MIT runtime only) and the feature matrix. |
`"format": "anima"` field, MCP tool names such as `anima_guide`, the `<anima-player>` element, the bundle path
`packages/headless/dist/anima.js`, and the bridge token path above.
MIT-licensed runtime sources; no Rive editor binary, code, assets or file was used. Rive is a trademark of its owner,
