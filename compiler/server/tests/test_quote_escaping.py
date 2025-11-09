#!/usr/bin/env python3
"""
Test to verify that HTML special characters in content attributes are properly escaped.
This prevents Vue parser errors like:
  "Attribute name cannot contain U+0022 ("), U+0027 ('), and U+003C (<)"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vue_generator import VueGenerator

def test_content_with_quotes():
    """Test that content with quotes is properly escaped."""
    generator = VueGenerator('../manifests')
    
    # Test AST with content containing quotes
    ast = {
        "type": "Text",
        "props": {
            "content": '6.3" Super Retina XDR',  # Contains unescaped quote
            "style": {"fontSize": "1rem"}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    # Check that quotes are escaped in content attribute
    assert 'content="6.3&quot; Super Retina XDR"' in vue_code, \
        "Quotes in content attribute should be escaped as &quot;"
    
    # Check that unescaped quotes don't appear in attributes
    assert 'content="6.3" Super' not in vue_code, \
        "Unescaped quotes should not appear in content attribute"
    
    print("✅ Test passed: Quotes properly escaped in content attribute")

def test_content_with_less_than():
    """Test that < is properly escaped."""
    generator = VueGenerator('../manifests')
    
    ast = {
        "type": "Text",
        "props": {
            "content": 'Price < $100',
            "style": {}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    assert 'content="Price &lt; $100"' in vue_code, \
        "< in content attribute should be escaped as &lt;"
    
    print("✅ Test passed: < properly escaped in content attribute")

def test_content_with_greater_than():
    """Test that > is properly escaped."""
    generator = VueGenerator('../manifests')
    
    ast = {
        "type": "Text",
        "props": {
            "content": 'Score > 90',
            "style": {}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    assert 'content="Score &gt; 90"' in vue_code, \
        "> in content attribute should be escaped as &gt;"
    
    print("✅ Test passed: > properly escaped in content attribute")

def test_content_with_ampersand():
    """Test that & is properly escaped."""
    generator = VueGenerator('../manifests')
    
    ast = {
        "type": "Text",
        "props": {
            "content": 'A&B Company',
            "style": {}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    assert 'content="A&amp;B Company"' in vue_code, \
        "& in content attribute should be escaped as &amp;"
    
    print("✅ Test passed: & properly escaped in content attribute")

def test_content_with_single_quote():
    """Test that single quotes are properly escaped."""
    generator = VueGenerator('../manifests')
    
    ast = {
        "type": "Text",
        "props": {
            "content": "It's amazing",
            "style": {}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    # Single quotes should be escaped as &#x27; or &apos;
    assert ('content="It&#x27;s amazing"' in vue_code or 
            'content="It&apos;s amazing"' in vue_code), \
        "Single quotes in content attribute should be escaped"
    
    print("✅ Test passed: Single quotes properly escaped in content attribute")

def test_multiple_special_chars():
    """Test content with multiple special characters."""
    generator = VueGenerator('../manifests')
    
    ast = {
        "type": "Text",
        "props": {
            "content": '6.3" screen & 256GB < 512GB',
            "style": {}
        }
    }
    
    vue_code = generator.generate({"root": ast}, {}, [])
    
    # All special chars should be escaped
    assert '&quot;' in vue_code, "Quotes should be escaped"
    assert '&amp;' in vue_code, "Ampersands should be escaped"
    assert '&lt;' in vue_code, "Less-than should be escaped"
    
    # Original unescaped chars should not appear in attributes
    assert 'content="6.3"' not in vue_code, "Unescaped quote should not appear"
    
    print("✅ Test passed: Multiple special characters properly escaped")

if __name__ == '__main__':
    print("Testing HTML special character escaping in content attributes...")
    print("=" * 60)
    
    try:
        test_content_with_quotes()
        test_content_with_less_than()
        test_content_with_greater_than()
        test_content_with_ampersand()
        test_content_with_single_quote()
        test_multiple_special_chars()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("\nThe fix ensures that:")
        print("  • Double quotes → &quot;")
        print("  • Single quotes → &#x27; or &apos;")
        print("  • Less than → &lt;")
        print("  • Greater than → &gt;")
        print("  • Ampersand → &amp;")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
