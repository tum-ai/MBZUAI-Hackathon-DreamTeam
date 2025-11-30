"""
Test WebSocket streaming endpoint.
"""
import asyncio
import json
import sys
from pathlib import Path
import websockets

async def test_streaming():
    print("\n" + "="*60)
    print("Testing WebSocket Streaming Endpoint")
    print("="*60)
    
    uri = "ws://localhost:8000/plan-stream"
    
    try:
        print(f"\nConnecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✓ Connected!")
            
            # Send plan request
            request = {
                "type": "plan_request",
                "requestId": "test-request-1",
                "sessionId": "test-session-1",
                "text": "Click the Get Started button",
                "stepId": "test-step-1"
            }
            
            print(f"\nSending request: {request['text']}")
            await websocket.send(json.dumps(request))
            
            # Receive streaming responses
            step_count = 0
            print("\nReceiving responses...")
            print("-" * 60)
            
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    msg_type = data.get("type")
                    
                    if msg_type == "step_completed":
                        step_count += 1
                        print(f"\n✓ Step {step_count} completed:")
                        print(f"   Type: {data.get('stepType')}")
                        print(f"   Intent: {data.get('intent', '')[:60]}...")
                        print(f"   Result: {data.get('result', '')[:100]}...")
                        print(f"   Time: {data.get('executionTime', 0):.2f}s")
                        
                    elif msg_type == "plan_finished":
                        print(f"\n✓ Plan finished!")
                        print(f"   Total steps: {data.get('totalSteps')}")
                        print(f"   Total time: {data.get('totalTime', 0):.2f}s")
                        break
                        
                    elif msg_type == "error":
                        print(f"\n✗ Error: {data.get('error')}")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n⏱ Timeout waiting for response")
                    break
            
            print("\n" + "="*60)
            print("Test completed!")
            print("="*60)
            
            return step_count > 0
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("IMPORTANT: Make sure llm_new server is running!")
    print("Run: conda run -n mbzuai python -m llm_new.server")
    print("="*60)
    
    success = asyncio.run(test_streaming())
    sys.exit(0 if success else 1)
