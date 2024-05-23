print("Hello Ocean!")
print("Josh sagt: Orcas rule!")
print("The One Piece is Orcas")
print("just wanna go home now!!!")
print("Good bye work PC, hello home PC!")

def whale():
    orca_array = ["Free Willy #1", "Free Willy #2", "Free Willy #3", "Free Willy #n"]
    for each in orca_array: print(f"Jump, {each}!")

def fish(limit):
    flying_fish = {"Captain": "Oscar", "Admiral": "Rudi", "Rear Admiral": "Carl", "Drunken Sailor": "Alan"}
    for key, value in flying_fish.items(): print(f"Fly, {key} {value}!")
    for i in range(0, limit):
        for each in flying_fish.values(): print(each[0])

whale()
print("----")
fish(1)