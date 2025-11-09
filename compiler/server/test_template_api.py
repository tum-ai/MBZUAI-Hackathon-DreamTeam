#!/usr/bin/env python3
"""
Test script for the template generation API endpoint.
Demonstrates generating 4 variations of different template types.
"""

import requests
import json
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"

def test_blog_template():
    """Test generating 4 blog template variations."""
    print("\n" + "="*60)
    print("Testing Blog Template Generation")
    print("="*60)
    
    payload = {
        "template_type": "blog",
        "variables": {
            "blogName": "Tech Insights",
            "tagline": "Exploring the Future of Technology",
            "authorName": "Jane Smith",
            "about": "A blog dedicated to sharing insights about emerging technologies, programming best practices, and the future of AI.",
            "posts": [
                {
                    "title": "The Future of AI in 2025",
                    "date": "November 5, 2025",
                    "excerpt": "Exploring the latest trends in artificial intelligence and what they mean for developers.",
                    "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800"
                },
                {
                    "title": "Building Scalable Web Applications",
                    "date": "October 28, 2025",
                    "excerpt": "Best practices for creating applications that can handle millions of users.",
                    "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800"
                },
                {
                    "title": "Introduction to Machine Learning",
                    "date": "October 15, 2025",
                    "excerpt": "A beginner's guide to understanding ML concepts and getting started with your first model.",
                    "image": "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=800"
                }
            ]
        }
    }
    
    response = requests.post(f"{API_BASE}/generate-template-variations", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Success!")
        print(f"  Template: {result['template_type']}")
        print(f"  Selection Dir: {result['selection_dir']}")
        print(f"\n  Generated {len(result['variations'])} variations:")
        for var in result['variations']:
            print(f"    [{var['index']}] {var['palette']} palette + {var['font']} font")
            print(f"        Path: {var['path']}")
            print(f"        Pages: {', '.join(var['pages'])}")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def test_product_template():
    """Test generating 4 product showcase template variations."""
    print("\n" + "="*60)
    print("Testing Product Showcase Template Generation")
    print("="*60)
    
    payload = {
        "template_type": "product",
        "variables": {
            "productName": "iPhone 16 Pro",
            "tagline": "Titanium. So strong. So light. So Pro.",
            "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1200",
            "features": [
                {
                    "title": "A18 Pro Chip",
                    "description": "The most powerful chip ever in a smartphone. Blazing-fast performance for everything you do."
                },
                {
                    "title": "Advanced Camera System",
                    "description": "48MP main camera with 2x Telephoto. Capture stunning photos in any light."
                },
                {
                    "title": "All-Day Battery",
                    "description": "Up to 29 hours of video playback. Power through your entire day."
                }
            ],
            "specs": [
                {"label": "Display", "value": "6.3\" Super Retina XDR"},
                {"label": "Chip", "value": "A18 Pro"},
                {"label": "Camera", "value": "48MP Main, 12MP Ultra Wide"},
                {"label": "Battery", "value": "Up to 29 hours video"},
                {"label": "Storage", "value": "128GB, 256GB, 512GB, 1TB"}
            ],
            "galleryImages": [
                "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600",
                "https://images.unsplash.com/photo-1695048133364-1d2b3a8b4a0f?w=600",
                "https://images.unsplash.com/photo-1695048071832-bec9b1c5e6f3?w=600"
            ]
        }
    }
    
    response = requests.post(f"{API_BASE}/generate-template-variations", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Success!")
        print(f"  Template: {result['template_type']}")
        print(f"  Selection Dir: {result['selection_dir']}")
        print(f"\n  Generated {len(result['variations'])} variations:")
        for var in result['variations']:
            print(f"    [{var['index']}] {var['palette']} palette + {var['font']} font")
            print(f"        Path: {var['path']}")
            print(f"        Pages: {', '.join(var['pages'])}")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def test_gallery_template():
    """Test generating 4 gallery template variations."""
    print("\n" + "="*60)
    print("Testing Gallery Template Generation")
    print("="*60)
    
    payload = {
        "template_type": "gallery",
        "variables": {
            "name": "Emma Wilson",
            "tagline": "Fine Art Photographer",
            "heroImage": "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=1200",
            "galleryImages": [
                "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=600",
                "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=600",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
                "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600",
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600",
                "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600"
            ],
            "about": "Fine art photographer specializing in landscape and architectural photography. Based in San Francisco, capturing the beauty of nature and urban environments."
        }
    }
    
    response = requests.post(f"{API_BASE}/generate-template-variations", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Success!")
        print(f"  Template: {result['template_type']}")
        print(f"  Selection Dir: {result['selection_dir']}")
        print(f"\n  Generated {len(result['variations'])} variations:")
        for var in result['variations']:
            print(f"    [{var['index']}] {var['palette']} palette + {var['font']} font")
            print(f"        Path: {var['path']}")
            print(f"        Pages: {', '.join(var['pages'])}")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def test_ecommerce_template():
    """Test generating 4 e-commerce template variations."""
    print("\n" + "="*60)
    print("Testing E-commerce Template Generation")
    print("="*60)
    
    payload = {
        "template_type": "ecommerce",
        "variables": {
            "storeName": "Modern Home",
            "tagline": "Curated Furniture for Modern Living",
            "heroImage": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200",
            "products": [
                {
                    "name": "Modern Sofa",
                    "price": "$1,299",
                    "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
                },
                {
                    "name": "Oak Dining Table",
                    "price": "$899",
                    "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=400"
                },
                {
                    "name": "Leather Armchair",
                    "price": "$649",
                    "image": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=400"
                },
                {
                    "name": "Minimalist Desk",
                    "price": "$449",
                    "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400"
                }
            ],
            "about": "We curate the finest modern furniture pieces to transform your living spaces. Quality craftsmanship meets contemporary design."
        }
    }
    
    response = requests.post(f"{API_BASE}/generate-template-variations", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Success!")
        print(f"  Template: {result['template_type']}")
        print(f"  Selection Dir: {result['selection_dir']}")
        print(f"\n  Generated {len(result['variations'])} variations:")
        for var in result['variations']:
            print(f"    [{var['index']}] {var['palette']} palette + {var['font']} font")
            print(f"        Path: {var['path']}")
            print(f"        Pages: {', '.join(var['pages'])}")
        return True
    else:
        print(f"\n✗ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False


def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{API_BASE}/project", timeout=2)
        return response.status_code in [200, 404]  # Either is fine, means server is up
    except:
        return False


def main():
    print("="*60)
    print("Template Generation API Test")
    print("="*60)
    
    # Check if server is running
    if not check_server():
        print("\n✗ Error: Server is not running!")
        print(f"  Please start the server first:")
        print(f"  cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server")
        print(f"  python run_server.py")
        return
    
    print("\n✓ Server is running")
    
    # Run tests
    results = []
    
    results.append(("Blog", test_blog_template()))
    results.append(("Product", test_product_template()))
    results.append(("Gallery", test_gallery_template()))
    results.append(("E-commerce", test_ecommerce_template()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status} - {name} Template")
    
    # Check generated files
    selection_dir = Path("/tmp/selection")
    if selection_dir.exists():
        print(f"\n✓ Generated files in: {selection_dir}")
        for i in range(4):
            variant_dir = selection_dir / str(i)
            if variant_dir.exists():
                print(f"  [{i}] {variant_dir}")
                print(f"      - project.json: {(variant_dir / 'project.json').exists()}")
                inputs_dir = variant_dir / "inputs"
                if inputs_dir.exists():
                    page_count = len(list(inputs_dir.glob("*.json")))
                    print(f"      - Page ASTs: {page_count} files")
    else:
        print(f"\n✗ Selection directory not found: {selection_dir}")


if __name__ == "__main__":
    main()
