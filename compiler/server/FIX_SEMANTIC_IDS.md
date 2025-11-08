# Fix Summary - Semantic IDs in Function Names

## Problem

When generating Vue components with semantic IDs containing dots (e.g., `page-root.faq-section.faq-item-1`), these dots were being used directly in JavaScript function names, which is invalid:

```javascript
// ❌ INVALID - dots in function name
function onpage_root.faq_section.faq_item_1_click() {
  // ...
}
```

This caused compilation error:
```
[ERROR] Expected "(" but found "."
  function onpage_root.faq_section.faq_item_1_click() {
                      ^
```

## Root Cause

The `_generate_functions()` method in `vue_generator.py` was only replacing hyphens with underscores:

```python
# OLD CODE
func_name = f"on{node_id.replace('-', '_')}_{event_name}"
```

But semantic IDs now contain **both dots and hyphens**, so dots were left in the function names.

## Solution

Updated the function to sanitize both dots and hyphens:

```python
# NEW CODE
sanitized_id = node_id.replace('.', '_').replace('-', '_')
func_name = f"on{sanitized_id}_{event_name}"
```

Now generates valid function names:
```javascript
// ✅ VALID - all special chars replaced with underscores
function onpage_root_faq_section_faq_item_1_click() {
  faqOpen.value = !faqOpen.value;
}
```

## Additional Fix

Also fixed the `!` (negation) operator not being recognized as "pure code":

```python
# Added ! to the pure_code_pattern regex
pure_code_pattern = re.compile(r"^[\w.()+\-*/%!\s\d]+$")
```

This ensures expressions like `!${state.faqOpen}` are correctly converted to `!faqOpen.value` instead of being wrapped in backticks.

## Changes Made

**File**: `compiler/server/src/vue_generator.py`

1. **Line ~218**: Updated `_generate_functions()` to sanitize dots
2. **Line ~197**: Added `!` to pure code pattern regex

## Testing

Regenerate and test:
```powershell
cd compiler\server
python test_ast_directly.py tests\test-enhanced.json Home

cd ..\output\my-new-site
npm run dev
```

Result: ✅ Compiles successfully, app runs on http://localhost:5178

## Impact

- ✅ All semantic IDs now work correctly in event handlers
- ✅ Function names are valid JavaScript identifiers
- ✅ No breaking changes to existing code
- ✅ Maintains the hierarchical ID benefits for data attributes

The semantic IDs are still preserved in the `data-component-id` and `data-nav-id` attributes for browser automation and LLM understanding, only the function names are sanitized.
