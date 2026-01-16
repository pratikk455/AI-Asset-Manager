"""Quick test for Gemini client"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from llm.gemini_client import get_gemini_client


async def test_gemini():
    print("Testing Gemini Client...")
    print("-" * 50)

    client = get_gemini_client()

    # Test 1: Quick (Flash)
    print("\n1. Testing Flash (quick)...")
    result = await client.quick("What is 2 + 2? Reply with just the number.")
    print(f"   Result: {result.strip()}")

    # Test 2: Search with grounding
    print("\n2. Testing Search with Grounding...")
    result = await client.search("What is Tesla (TSLA) stock price today?")
    print(f"   Result: {result['text'][:200]}...")
    print(f"   Sources: {len(result['sources'])} found")
    if result['sources']:
        print(f"   First source: {result['sources'][0]['title']}")

    # Test 3: Pro reasoning
    print("\n3. Testing Pro (reasoning)...")
    result = await client.think(
        "In one sentence, what is Tesla's main competitive advantage?",
        temperature=0.5
    )
    print(f"   Result: {result.strip()[:200]}...")

    print("\n" + "-" * 50)
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_gemini())
