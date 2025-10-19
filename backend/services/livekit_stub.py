def create_room_and_join_agent(caller_id: str):
    """Simulate LiveKit room creation and AI agent joining."""
    room_id = f"room_{caller_id}"
    print(f"[LiveKit] Simulated connection established for {caller_id} in {room_id}")
    return room_id
