f = open("message2.txt", "a")
for i in range(1456*6):
  numAsString = str(i)
  res =""
  for j in range(15 - len(numAsString)):
    res+="*"
  res+=numAsString
  res+="\n"
  f.write(res)
f.close()