f = open("message2.txt", "a")
for i in range(2049):
  numAsString = str(i)
  res =""
  for j in range(15 - len(numAsString)):
    res+="*"
  res+=numAsString
  res+="\n"
  f.write(res)
f.close()