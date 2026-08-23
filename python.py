name=str(input("enter either suresh | ramesh"))
if name=="suresh":
    print("hello suresh")
    x=str(input("enter in | out"))
    if x=="in":
        print("as he is available take suresh out ")

    elif x=="out":
        print("as he is not available make a call to suresh")

elif name=="ramesh":
    print("hello ramesh")
    x=str(input("enter in | out"))
    if x== "in":
        print("as he is available take ramesh out")

    elif x=="out":
        print("as he is not available make a call to ramesh")

else:
    print("please enter names in b/w suresh and ramesh only")
