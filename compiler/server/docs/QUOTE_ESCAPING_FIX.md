# Quote Escaping Fix

## Problem

Vue parser error when content attributes contain special HTML characters like quotes:

```
[plugin:vite:vue] Attribute name cannot contain U+0022 ("), U+0027 ('), and U+003C (<).
```

### Example Error

```vue
<dd content="6.3" Super Retina XDR" style="...">6.3" Super Retina XDR</dd>
                    ^ unescaped quote breaks attribute parsing
```

## Root Cause

In `vue_generator.py`, line 357, content attribute values were being inserted directly without HTML escaping:

```python
props_map[key] = f'"{content}"'  # ❌ No escaping
```

When `content` contained special characters like `"`, `'`, `<`, `>`, or `&`, they would break HTML attribute parsing.

## Solution

Added HTML entity escaping using Python's built-in `html.escape()` function:

```python
import html

# ... in props handling ...
elif tag != "p":  # Put prop on element (e.g., <h1 content="...">)
    # Escape quotes in content for HTML attribute
    escaped_content = html.escape(content, quote=True)
    props_map[key] = f'"{escaped_content}"'
```

## What Gets Escaped

The `html.escape(content, quote=True)` function converts:

| Character | HTML Entity | Example |
|-----------|-------------|---------|
| `"` (double quote) | `&quot;` | `6.3"` → `6.3&quot;` |
| `'` (single quote) | `&#x27;` | `It's` → `It&#x27;s` |
| `<` (less than) | `&lt;` | `< 100` → `&lt; 100` |
| `>` (greater than) | `&gt;` | `> 90` → `&gt; 90` |
| `&` (ampersand) | `&amp;` | `A&B` → `A&amp;B` |

## After Fix

```vue
<dd content="6.3&quot; Super Retina XDR" style="...">6.3" Super Retina XDR</dd>
            ^^^^^^ properly escaped
```

## Verification

All 4 template variations now generate with properly escaped content attributes:

```bash
# Check all variations
for i in 0 1 2 3; do
  grep "6.3" /tmp/selection/$i/src/views/Specs.vue
done

# Output:
# content="6.3&quot; Super Retina XDR"  ✅
# content="6.3&quot; Super Retina XDR"  ✅
# content="6.3&quot; Super Retina XDR"  ✅
# content="6.3&quot; Super Retina XDR"  ✅
```

## Files Modified

- `compiler/server/src/vue_generator.py`:
  - Line 6: Added `import html`
  - Lines 356-358: Added `html.escape()` call for content attribute values

## Testing

1. **Regenerate templates:**
   ```bash
   cd compiler/server
   python test_selection.py
   ```

2. **Verify escaping:**
   ```bash
   grep "content=" /tmp/selection/*/src/views/*.vue | grep "&quot;"
   ```

3. **Start dev servers:**
   ```bash
   ./run_variations.sh
   ```

   All variations should compile without errors.

## Impact

- ✅ Fixes Vue parser errors for content with special characters
- ✅ No breaking changes - HTML entities are standard and supported everywhere
- ✅ Works for all component types (Text, Button, Card, etc.)
- ✅ Applies to both `content` and `text` props

## Notes

- Text content **inside** tags (between `>` and `</tag>`) doesn't need escaping - only attribute values do
- The fix uses `html.escape(content, quote=True)` which escapes both single and double quotes
- This is a standard HTML best practice and works in all browsers and frameworks
