from npc_system import NPCSystem


def main():
    system = NPCSystem()
   
    print("🌟 NPC Relationship System 🌟")
    print("Available NPCs:")
    for i in range(1, 8):
        npc = system.get_npc(i)
        print(f"{i}. {npc.name} - {npc.get_personality_description()} ({npc.get_gang_affiliation()})")
   
    while True:
        try:
            choice = input("\nChoose an NPC to talk to (1-7), 'log' for status, or 'quit': ")
            if choice.lower() in ['quit', 'exit']:
                break
               
            if choice.lower() == 'log':
                system.show_logs()
                continue
               
            npc_id = int(choice)
            if 1 <= npc_id <= 7:
                system.converse_with_npc(npc_id)
            else:
                print("Please enter a number between 1 and 7")
               
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()