# 🎤 MBZUAI-Hackathon

---

## 1️⃣ What We're Building (The Vision)

We are building a **voice-first, generative web development tool**. The user interacts with a "Bixby-like" assistant popup using only their voice.

The tool responds to natural language commands (e.g., *"Add a hero section with a title and a signup button"*) and dynamically generates a new web page (or modifies the existing one) in real-time. This process is powered by an ultra-fast LLM that "thinks" and generates a structured representation of the UI, not just raw code.

---

## 2️⃣ The Core Workflow (How Information is Shared)

This is the end-to-end data flow for a single user interaction. Every team must understand this flow, as it defines how our services interact.

### 1. Intent Capture (Voice Client)

The user speaks. A real-time, on-device Voice Recognition system captures the audio and transcribes it into a **Prompt Text** (a string).

### 2. "Thinking" (The LLM Compiler)

The Prompt Text is sent to the **"LLM AST Compiler"**. This service's job is to:

- Analyze the user's intent.
- Compare that intent to the current UI state (which it knows by having the AST).
- Output a structured command (like a JSON Patch) to modify the AST.

### 3. State Update (The Source of Truth)

This structured command is applied to our master `ui-tree.json` (the AST). This file is the **single source of truth** for the entire application's UI. We never edit generated code directly.

### 4. Generation (The Codebase Compiler)

A Deterministic Python Generator (which we'll build) is watching the `ui-tree.json` file. When it detects a change, it:

- Deletes the old generated code (e.g., `header.tsx`, `body.tsx`).
- Regenerates the entire codebase from scratch by compiling the new AST.

### 5. Render (The View)

A Server (also watching the output directory) detects the newly generated files and pushes them to the **frontend browser frame**, triggering a hot-reload. The user sees their change appear instantly.

### 6. Feedback Loop (The "Eyes")

- If the user's command is ambiguous (*"change the button"*), the LLM can use the Playwright tool to read the DOM.
- The Playwright tool looks for special `data-component-id` attributes that our Generator adds to the HTML.
- This ID allows the LLM to map a visual element back to its exact node in the AST, allowing it to ask a clarifying **"Prompt-back"** question (e.g., *"Do you mean the 'Submit' button or the 'Cancel' button?"*).

---

## 3️⃣ Core Principles (How We'll Build It)

These are the architectural rules we will follow to ensure the product is scalable, deterministic, and not-brittle.

### 🔑 Principle 1: The AST is the Single Source of Truth

- **What:** The `ui-tree.json` (our name for the AST) defines 100% of the UI, its state, and its logic.
- **Why:** This prevents state drift. We avoid the diff/patch method entirely. To change the UI, you must change the AST.

### 🔑 Principle 2: The Generator is Deterministic

- **What:** Our Python Code Generator must be a "pure function." The exact same `ui-tree.json` input must always produce the exact same (e.g.) Vue/Angular code output.
- **Why:** This makes our architecture solid, predictable, and testable.

### 🔑 Principle 3: We Use a Component Manifest (Schema-Driven)

- **What:** To support 80-90% of a framework (like Vue), we will not hardcode components into our generator. Instead, we will create a Component Manifest system (a folder of JSON files).
- **How:** Each JSON file will describe a framework component (e.g., `v-card`): its props, its slots, and its events. Our generator will be a manifest processor that learns to build components by reading these files.
- **Why:** This lets us add new components (e.g., `v-data-table`) just by adding a new JSON file, not by rewriting the core generator.

### 🔑 Principle 4: We Use Stable IDs for Feedback

- **What:** The generator is responsible for creating a unique ID for every node in the AST and rendering it into the final HTML (e.g., `<div data-component-id="hero-123">...</div>`).
- **Why:** This is the essential link that closes the feedback loop. It's how Playwright and the LLM can "see" the screen and map it back to the AST.

### 🔑 Principle 5: We Abstract Logic

- **What:** We will not let the LLM generate raw JavaScript for `onClick` events. We will create a "Logic AST"—a simple JSON structure that describes an action (e.g., `action:setState`, `action:showAlert`).
- **Why:** Our Deterministic Generator will then compile this safe, abstract JSON into the correct, secure, and framework-specific JavaScript. This prevents code-injection and ensures reliability.

---

## 📐 Project Architecture: Schemas & Data Flow

This section defines the "language" our modules speak. Getting this right is the key to a scalable and deterministic system.

There are **three core schemas** that define our entire application:

1. **The Component Manifest:** What can be built (e.g., a `v-btn` exists).
2. **The AST (`ui-tree.json`):** What is currently built (e.g., a specific `v-btn` instance exists).
3. **The Action AST:** What the application does (e.g., what happens when that button is clicked).

---

### 1. The Component Manifest Schema

This is a `*.manifest.json` file. We create one of these for each Vue/Angular component we want to support. This is our "plugin" system.

#### `v-btn.manifest.json` (Example for a Vuetify Button)

```json
{
  "componentName": "v-btn",
  "friendlyName": "Button",
  "module": "vuetify/components",
  "props": {
    "color": {
      "type": "string",
      "default": "primary"
    },
    "disabled": {
      "type": "boolean",
      "default": false
    },
    "text": {
      "type": "string"
    },
    "icon": {
      "type": "string"
    }
  },
  "slots": [
    "default"
  ],
  "events": [
    "click"
  ]
}
```

**Schema Fields:**

- **`componentName`:** The exact name to use in code (e.g., `<v-btn>`).
- **`friendlyName`:** What the LLM can call it (e.g., "a button", "a primary button").
- **`props`:** A whitelist of allowed properties and their types. This is crucial for validation.
- **`slots`:** An array of named slots this component provides. `default` is for children.
- **`events`:** A list of events (like `click`) that our Action AST can bind to.

---

### 2. The Core AST (`ui-tree.json`)

This is the **single source of truth** for the application's UI. It is a tree of component instances. It also defines the application's state.

#### `ui-tree.json` (Example)

```json
{
  "state": {
    "clickCount": {
      "type": "number",
      "defaultValue": 0
    },
    "userName": {
      "type": "string",
      "defaultValue": "Guest"
    }
  },
  "tree": {
    "id": "root",
    "type": "v-layout",
    "props": {},
    "slots": {
      "default": [
        {
          "id": "title-1",
          "type": "Text",
          "props": {
            "variant": "h1",
            "content": {
              "type": "expression",
              "value": "Welcome, ${state.userName}!"
            }
          },
          "slots": {}
        },
        {
          "id": "btn-1",
          "type": "v-btn",
          "props": {
            "color": "primary"
          },
          "slots": {
            "default": [
              {
                "id": "btn-text-1",
                "type": "Text",
                "props": {
                  "content": {
                    "type": "expression",
                    "value": "You clicked me ${state.clickCount} times"
                  }
                },
                "slots": {}
              }
            ]
          },
          "events": {
            "click": [
              {
                "type": "action:setState",
                "stateKey": "clickCount",
                "newValue": {
                  "type": "expression",
                  "value": "${state.clickCount} + 1"
                }
              }
            ]
          }
        }
      ]
    }
  }
}
```

**AST Structure:**

- **`state`:** A simple key-value store defining all reactive state variables.
- **`tree`:** The root component.
- **`id`:** The Stable ID we use to link the DOM (`data-component-id="btn-1"`) back to this node.
- **`type`:** The component name (must match a `componentName` in a manifest).
- **`props`:** Key-value pairs. Notice the `content` prop for `title-1` is an object. This is a State Binding.
- **`slots`:** An object where keys are slot names (from the manifest) and values are arrays of child components.
- **`events`:** An object where keys are event names (from the manifest) and values are arrays of Actions.

---

### 3. The Action AST Schema

This is the small, safe, JSON-based "language" we use to describe logic. It lives inside the `events` array in the AST. This is how we avoid writing raw JavaScript.

#### Action: `action:setState`

```json
{
  "type": "action:setState",
  "stateKey": "clickCount",
  "newValue": {
    "type": "expression",
    "value": "${state.clickCount} + 1"
  }
}
```

#### Action: `action:showAlert`

```json
{
  "type": "action:showAlert",
  "message": "Hello from the AST!"
}
```

#### Action: `action:navigate`

```json
{
  "type": "action:navigate",
  "url": "/profile"
}
```

Our Python generator will be a compiler that knows how to turn `action:setState` into the correct Vue (`clickCount.value = ...`) or Angular code.

---

### 4. LLM Prompts & Outputs

The LLM never touches the AST directly. It only outputs a **JSON Patch (RFC 6902)** to modify the AST.

#### System Prompt (The LLM's)

> You are an expert AI assistant that modifies a UI's Abstract Syntax Tree (AST). You will be given the user's request and the current AST as a JSON object.
>
> Your only job is to generate a valid JSON Patch (RFC 6902) array that safely applies the user's changes to the AST.
>
> - ❌ **Do NOT** output code (no HTML, JS, or CSS).
> - ❌ **Do NOT** explain your reasoning.
> - ✅ **ONLY** output the JSON Patch array.
> - To add a new component, use the `add` operation. The path should point to a slots array (e.g., `/tree/slots/default/-` to add to the end).
> - A new component must have a unique `id`, a valid `type` (e.g., `v-btn`), and default `props` and `slots`.
> - To change a prop, use the `replace` operation (e.g., `path: /tree/slots/default/0/props/content`).
> - To add an action, use the `add` operation (e.g., `path: /tree/slots/default/1/events/click/-`).
> - You must adhere to the provided Action & Component Schemas.

---

## 5️⃣ End-to-End Workflow: Adding a Button

Here is the complete data flow for a single request:

### Step 1: User Speaks

**User:** *"Add a new button next to the first one that shows an alert."*

### Step 2: Voice Client

- Transcribes the audio into a string: `"Add a new button next to the first one that shows an alert."`
- Sends this text to the "LLM Compiler" service.

### Step 3: LLM Compiler "Thinks"

- **Input:** The prompt string and the current `ui-tree.json` (from above).
- **Reasoning (Internal):**
  1. "The user wants a new button."
  2. "The `ui-tree.json` has one button (`btn-1`) in `/tree/slots/default` at index 1."
  3. "The user wants to add another button next to it. I will add it to `/tree/slots/default` at the end (using the index)."
  4. "I'll need a new unique ID, like `btn-2`."
  5. "The type will be `v-btn`."
  6. "The user wants it to 'show an alert'. I need to add an `action:showAlert` to its `events.click` array."

- **LLM Output** (This is all it sends back):

```json
[
  {
    "op": "add",
    "path": "/tree/slots/default/-",
    "value": {
      "id": "btn-2",
      "type": "v-btn",
      "props": {
        "color": "secondary",
        "text": "Show Alert"
      },
      "slots": {},
      "events": {
        "click": [
          {
            "type": "action:showAlert",
            "message": "You clicked the new button!"
          }
        ]
      }
    }
  }
]
```

### Step 4: AST State Manager

- Receives the JSON Patch array.
- Applies the patch to the `ui-tree.json` file.
- Saves the file. The new AST is now the source of truth.

### Step 5: Python Code Generator

- A file watcher (e.g., `watchdog`) detects the change to `ui-tree.json`.
- It triggers a full rebuild.
- The generator deletes the old `/dist` folder.
- It loads the new `ui-tree.json` and its Component Manifests.
- It recursively walks the new AST and generates the full Vue codebase from scratch.

#### Example Generated `App.vue` (Simplified)

```vue
<template>
  <v-layout>
    <h1 data-component-id="title-1">
      Welcome, {{ userName }}!
    </h1>

    <v-btn
      color="primary"
      @click="onBtn1Click"
      data-component-id="btn-1"
    >
      <span data-component-id="btn-text-1">
        You clicked me {{ clickCount }} times
      </span>
    </v-btn>

    <v-btn
      color="secondary"
      @click="onBtn2Click"
      data-component-id="btn-2"
    >
      Show Alert
    </v-btn>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue';

// Compiled from state
const clickCount = ref(0);
const userName = ref("Guest");

// Compiled from btn-1's events
function onBtn1Click() {
  clickCount.value = clickCount.value + 1;
}

// Compiled from btn-2's events
function onBtn2Click() {
  alert("You clicked the new button!");
}
</script>
```

### Step 6: Server & View

- The server's file watcher sees the new files in the `/dist` folder.
- It triggers a hot-reload of the browser.
- The user instantly sees their new button appear on the screen.

---
