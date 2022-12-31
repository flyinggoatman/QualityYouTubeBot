print("List")

# Open the file in read mode
with open('channels.txt', 'r') as file:
  
  # Read the contents of the file into a list
  lines = []
  for line in file:
    lines.append(line.strip())

# Now you can use the list `lines` in your program
for line in lines:
  print(line)