# D2 Diagram Generation Skill

You are an expert at creating professional architecture diagrams, flowcharts, system maps, and visual documentation using D2 — a text-based diagram language.

## When to Use This Skill

Activate when the user asks you to:
- Create or update a diagram, flowchart, system map, architecture overview, or visual documentation
- Visualize a pipeline, data flow, org chart, funnel, or process
- Map out how components connect in a system
- Generate a visual representation of anything structural

## Requirements

- **D2 CLI** must be installed (`brew install d2` on macOS, or `curl -fsSL https://d2lang.com/install.sh | sh -` on Linux)
- Diagrams are saved as `.d2` text files in a `diagrams/` folder
- Rendered to `.png` via the render script

## The Workflow

Every diagram follows this loop:

1. **Author** — Write a `.d2` source file in `diagrams/`
2. **Render** — Run `bash scripts/generate_diagrams.sh` to convert all `.d2` → `.png`
3. **Validate** — Read the `.png` output using vision to check accuracy and layout
4. **Iterate** — If anything looks wrong, edit the `.d2` and re-render

Always validate visually. Never ship a diagram without checking the PNG output.

## Render Script

The render script is at `scripts/generate_diagrams.sh`. It auto-discovers all `.d2` files in `diagrams/` and renders them.

```bash
bash scripts/generate_diagrams.sh          # Default: ELK layout, theme 0
bash scripts/generate_diagrams.sh dagre 0  # Dagre layout (simpler, faster)
bash scripts/generate_diagrams.sh elk 6    # ELK layout, Grape Soda theme
```

**Parameters:**
- Layout `elk` (recommended — clean hierarchical layouts) or `dagre` (default D2, faster)
- Theme `0` (neutral professional), `1` (grey), `3` (Terrastruct), `4` (cool classics), `5` (berry blue), `6` (grape soda), `100` (origami/hand-drawn)
- Padding: 40px (hardcoded in script)

---

## D2 Language Reference

### Basic Structure

```d2
# Comments start with hash
direction: down  # or: right

# Simple node
my_node: My Label

# Connection
node_a -> node_b: relationship label

# Node with explicit shape
database: My Database {
  shape: cylinder
}
```

### Direction

Controls the overall flow of the diagram.

```d2
direction: down   # Top to bottom (default) — good for funnels, hierarchies
direction: right  # Left to right — good for pipelines, data flows, timelines
```

**Rule of thumb:** Use `right` for pipelines and sequential processes. Use `down` for hierarchies, funnels, and org charts.

### Shapes

```d2
box: Default Box                          # rectangle (default)
db: Database {shape: cylinder}            # cylinder — databases, storage
doc: Report {shape: document}             # document — files, outputs
hex: External System {shape: hexagon}     # hexagon — external entities
person: User {shape: person}              # person — human actors
label: Annotation {shape: text}           # text — floating labels (no border)
pg: Config File {shape: page}             # page — files, configs
pkg: Module {shape: package}              # package — grouped modules
oval: Process {shape: oval}               # oval — processes, decisions
diamond: Decision {shape: diamond}        # diamond — decision points
```

### Styling

Apply styles directly to any node or connection.

```d2
node: My Node {
  style.fill: "#2563eb"           # Background color (hex, quoted)
  style.font-color: "#ffffff"     # Text color
  style.stroke: "#1d4ed8"         # Border color
  style.stroke-width: 2           # Border thickness
  style.stroke-dash: 5            # Dashed border (for planned/future items)
  style.bold: true                # Bold text
  style.italic: true              # Italic text
  style.font-size: 18             # Text size (default ~14)
  style.border-radius: 12         # Rounded corners
  style.opacity: 0.8              # Transparency (0-1)
  style.shadow: true              # Drop shadow
}
```

### Connections

```d2
# Basic directed arrow
a -> b: sends data

# Bidirectional
a <-> b: syncs

# Undirected (line, no arrow)
a -- b: relates to

# Styled connection
a -> b: critical path {
  style.stroke: "#ef4444"         # Arrow color
  style.stroke-width: 3           # Arrow thickness
  style.stroke-dash: 5            # Dashed arrow
  style.font-size: 13             # Label size
  style.font-color: "#6b7280"    # Label color
  style.animated: true            # Animated flow (SVG only)
}
```

### Containers (Grouping)

Nest nodes inside containers to create visual groups.

```d2
backend: Backend Services {
  style.fill: "#eef2ff"          # Light background for the group
  style.font-size: 16
  style.bold: true

  api: REST API {
    style.fill: "#2563eb"
    style.font-color: "#ffffff"
  }
  worker: Background Worker {
    style.fill: "#2563eb"
    style.font-color: "#ffffff"
  }
  db: PostgreSQL {
    shape: cylinder
    style.fill: "#1a1a2e"
    style.font-color: "#ffffff"
  }

  # Internal connections
  api -> worker: queues jobs
  worker -> db: writes results
}

frontend: Frontend {
  style.fill: "#fef3c7"

  app: React App {
    style.fill: "#d97706"
    style.font-color: "#ffffff"
  }
}

# Cross-container connection
frontend.app -> backend.api: HTTP requests
```

### Titles

```d2
title: |md
  # My Diagram Title
| {
  near: top-center
  shape: text
  style.font-size: 28
  style.bold: true
}
```

### Multiline Labels

```d2
# Use \n for line breaks
server: Web Server\n4 instances\nUS-East {
  style.fill: "#2563eb"
  style.font-color: "#ffffff"
}
```

### Positioning Hints

```d2
# Place a text label at a specific position
footer: Source: internal data {
  shape: text
  style.font-size: 14
  style.font-color: "#6b7280"
  near: bottom-center
}
```

Valid `near` values: `top-center`, `top-left`, `top-right`, `bottom-center`, `bottom-left`, `bottom-right`, `center-left`, `center-right`.

### Inline Syntax (Compact)

For simple nodes, you can use semicolons:

```d2
small: Small Node {shape: rectangle; style.fill: "#fef3c7"; style.font-size: 12}
```

---

## Design Patterns

### Pattern 1: Simple Flow (Pipeline / Process)

Best for: data pipelines, user journeys, deployment processes.

```d2
direction: right

title: |md
  # Data Processing Pipeline
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

ingest: Ingest\nRaw Data {
  style.fill: "#3b82f6"
  style.font-color: "#ffffff"
  style.bold: true
}

transform: Transform\n& Validate {
  style.fill: "#8b5cf6"
  style.font-color: "#ffffff"
  style.bold: true
}

store: Store\nin Database {
  shape: cylinder
  style.fill: "#1a1a2e"
  style.font-color: "#ffffff"
  style.bold: true
}

serve: Serve\nvia API {
  style.fill: "#059669"
  style.font-color: "#ffffff"
  style.bold: true
}

ingest -> transform: validates
transform -> store: writes
store -> serve: reads
```

### Pattern 2: Hub-and-Spoke (Architecture Overview)

Best for: system architecture, ecosystem maps, org charts.

```d2
direction: down

title: |md
  # System Architecture
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

core: Core Platform {
  shape: rectangle
  style.fill: "#1a1a2e"
  style.font-color: "#ffffff"
  style.bold: true
  style.font-size: 18
}

service_a: Auth Service {
  style.fill: "#3b82f6"
  style.font-color: "#ffffff"
}

service_b: Payment Service {
  style.fill: "#8b5cf6"
  style.font-color: "#ffffff"
}

service_c: Notification Service {
  style.fill: "#059669"
  style.font-color: "#ffffff"
}

service_d: Analytics Service {
  style.fill: "#d97706"
  style.font-color: "#ffffff"
}

core -> service_a
core -> service_b
core -> service_c
core -> service_d

users: Users {
  shape: person
  style.fill: "#6b7280"
  style.font-color: "#ffffff"
}

users -> core: requests
```

### Pattern 3: Multi-Layer Architecture (Complex Systems)

Best for: data pipelines with multiple stages, microservice architectures, infrastructure diagrams.

```d2
direction: right

title: |md
  # Multi-Layer Data Architecture
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

sources: Data Sources {
  style.fill: "#f8f9fa"
  style.font-size: 16
  style.bold: true

  api_a: REST API\nService A {
    style.fill: "#3b82f6"
    style.font-color: "#ffffff"
  }
  api_b: Webhook\nService B {
    style.fill: "#3b82f6"
    style.font-color: "#ffffff"
  }
  api_c: Database\nService C {
    shape: cylinder
    style.fill: "#3b82f6"
    style.font-color: "#ffffff"
  }
}

processing: Processing Layer {
  style.fill: "#eef2ff"
  style.font-size: 16
  style.bold: true

  collector: Collector\nScript {
    style.fill: "#8b5cf6"
    style.font-color: "#ffffff"
  }
  transformer: Transform\n& Enrich {
    style.fill: "#8b5cf6"
    style.font-color: "#ffffff"
  }
}

storage: Storage {
  style.fill: "#f0fdf4"
  style.font-size: 16
  style.bold: true

  db: PostgreSQL {
    shape: cylinder
    style.fill: "#1a1a2e"
    style.font-color: "#ffffff"
    style.bold: true
  }
  cache: Redis Cache {
    shape: cylinder
    style.fill: "#ef4444"
    style.font-color: "#ffffff"
  }
}

outputs: Outputs {
  style.fill: "#fef3c7"
  style.font-size: 16
  style.bold: true

  dashboard: Dashboard {
    style.fill: "#d97706"
    style.font-color: "#ffffff"
  }
  api: Public API {
    style.fill: "#d97706"
    style.font-color: "#ffffff"
  }
  reports: Reports {
    shape: document
    style.fill: "#d97706"
    style.font-color: "#ffffff"
  }
}

# Source → Processing
sources.api_a -> processing.collector
sources.api_b -> processing.collector
sources.api_c -> processing.collector
processing.collector -> processing.transformer

# Processing → Storage
processing.transformer -> storage.db: writes
processing.transformer -> storage.cache: caches hot data

# Storage → Outputs
storage.db -> outputs.dashboard: queries
storage.db -> outputs.api: serves
storage.db -> outputs.reports: generates
storage.cache -> outputs.api: fast reads
```

### Pattern 4: Before/After or Comparison

Best for: migration plans, tool comparisons, process improvements.

```d2
direction: right

title: |md
  # Before vs After Migration
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

before: Before {
  style.fill: "#fee2e2"
  style.font-size: 18
  style.bold: true

  manual: Manual Process\n4 hours/day {
    style.fill: "#ef4444"
    style.font-color: "#ffffff"
  }
  spreadsheet: Spreadsheets\nError-prone {
    style.fill: "#ef4444"
    style.font-color: "#ffffff"
  }
  email: Email Reports\nDelayed {
    style.fill: "#ef4444"
    style.font-color: "#ffffff"
  }

  manual -> spreadsheet -> email
}

arrow: " " {
  shape: text
  style.font-size: 40
}

after: After {
  style.fill: "#dcfce7"
  style.font-size: 18
  style.bold: true

  automated: Automated Pipeline\n5 minutes {
    style.fill: "#059669"
    style.font-color: "#ffffff"
  }
  db: Central Database\nSingle source of truth {
    shape: cylinder
    style.fill: "#059669"
    style.font-color: "#ffffff"
  }
  dashboard: Live Dashboard\nReal-time {
    style.fill: "#059669"
    style.font-color: "#ffffff"
  }

  automated -> db -> dashboard
}

before -> arrow
arrow -> after
```

### Pattern 5: Funnel / Hierarchy

Best for: sales funnels, conversion paths, hierarchical structures.

```d2
direction: down

title: |md
  # Conversion Funnel
| {near: top-center; shape: text; style.font-size: 28; style.bold: true}

awareness: Awareness\nBlog, Social, Ads\n10,000 visitors/mo {
  style.fill: "#3b82f6"
  style.font-color: "#ffffff"
  style.bold: true
  style.font-size: 16
}

interest: Interest\nEmail Signup, Free Trial\n2,000 leads/mo {
  style.fill: "#8b5cf6"
  style.font-color: "#ffffff"
  style.bold: true
  style.font-size: 16
}

consideration: Consideration\nDemo, Sales Call\n500 qualified/mo {
  style.fill: "#d97706"
  style.font-color: "#ffffff"
  style.bold: true
  style.font-size: 16
}

purchase: Purchase\nNew Customers\n100 deals/mo {
  style.fill: "#059669"
  style.font-color: "#ffffff"
  style.bold: true
  style.font-size: 16
}

awareness -> interest: 20% convert {style.font-size: 13}
interest -> consideration: 25% convert {style.font-size: 13}
consideration -> purchase: 20% convert {style.font-size: 13}
```

---

## Recommended Color Palettes

Use consistent colors to create semantic meaning. Pick one palette and stick with it across all diagrams in a project.

### Professional (Blue/Gray)

| Element | Color | Hex |
|---------|-------|-----|
| Primary | Blue | `#2563eb` |
| Secondary | Indigo | `#4f46e5` |
| Accent | Amber | `#d97706` |
| Success | Green | `#059669` |
| Warning | Red | `#ef4444` |
| Infrastructure | Dark | `#1a1a2e` |
| External | Gray | `#6b7280` |
| Group backgrounds | Light variants | `#eef2ff`, `#f0fdf4`, `#fef3c7` |

### Vibrant (High Contrast)

| Element | Color | Hex |
|---------|-------|-----|
| Primary | Red | `#e74c3c` |
| Secondary | Purple | `#8e44ad` |
| Tertiary | Blue | `#2980b9` |
| Quaternary | Green | `#27ae60` |
| Accent | Orange | `#f39c12` |
| Infrastructure | Dark | `#1a1a2e` |
| External | Gray | `#95a5a6` |

### Muted (Pastel)

| Element | Color | Hex |
|---------|-------|-----|
| Primary | Soft Blue | `#93c5fd` |
| Secondary | Soft Purple | `#c4b5fd` |
| Tertiary | Soft Green | `#86efac` |
| Accent | Soft Orange | `#fdba74` |
| Text | Dark | `#1e293b` |

**Rule:** White text (`#ffffff`) on dark/saturated backgrounds. Dark text on light/pastel backgrounds.

---

## Conventions

### Visual Indicators

- **Solid borders** = live, active, currently running
- **Dashed borders** (`style.stroke-dash: 5`) = planned, future, not yet built
- **Cylinders** = databases, storage, caches
- **Hexagons** = external entities, third-party systems
- **Person shapes** = human actors, users, team members
- **Document shapes** = files, reports, generated outputs
- **Text shapes** = annotations, footnotes, legends (no border)

### Naming

- Use `snake_case` for node IDs: `auth_service`, `user_db`
- Use Title Case or natural language for labels: `Auth Service`, `User Database`
- Keep labels short — 2-4 words. Use `\n` for secondary info on the next line

### Special Characters

- **Dollar sign `$` is reserved** in D2 for variable substitution. Never use `$` in labels. Write `9,500 NZD` not `$9,500 NZD`.
- Quotes around hex colors: `style.fill: "#2563eb"` (always quote)
- Labels with special characters may need quoting: `node: "Label: with colon"`

### Layout Tips

- Keep diagrams focused — one concept per diagram. Split complex systems into multiple diagrams.
- Use containers to group related nodes — it dramatically improves readability.
- Limit to 3-4 levels of nesting maximum.
- For wide diagrams, use `direction: right`. For tall diagrams, use `direction: down`.
- Cross-container connections (`group_a.node -> group_b.node`) help show system boundaries.
- Use lighter fill colors for container backgrounds so child nodes stand out.
- Add a title using `|md # Title |` with `near: top-center` for every diagram.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `d2: command not found` | Install D2: `brew install d2` (macOS) or `curl -fsSL https://d2lang.com/install.sh \| sh -` (Linux) |
| Diagram layout is messy | Switch to ELK layout: `bash scripts/generate_diagrams.sh elk` |
| Nodes overlap | Add containers to group nodes, or split into multiple diagrams |
| `$` in label causes error | D2 reserves `$` for variables — remove dollar signs from labels |
| Arrow going wrong direction | Check `direction:` setting. Rearrange node declaration order. |
| Text too small in PNG | Increase `style.font-size` (minimum 14 for readability) |
| Container background too dark | Use light pastels for container backgrounds: `#eef2ff`, `#f0fdf4`, `#fef3c7` |
| PNG not regenerating | Make sure the `.d2` file is in the `diagrams/` folder |
| Colors look wrong | Hex values must be quoted: `"#2563eb"` not `#2563eb` |
