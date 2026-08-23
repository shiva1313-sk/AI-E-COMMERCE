# name=str(input("enter either suresh | ramesh"))
# if name=="suresh":
#     print("hello suresh")
#     x=str(input("enter in | out"))
#     if x=="in":
#         print("as he is available take suresh out ")

#     elif x=="out":
#         print("as he is not available make a call to suresh")

# elif name=="ramesh":
#     print("hello ramesh")
#     x=str(input("enter in | out"))
#     if x== "in":
#         print("as he is available take ramesh  out")

#     elif x=="out":
#         print("as he is not available make a call to ramesh")

# else:
#     print("please enter names in b/w suresh and ramesh only")

# ac_data=["1234 5678 8900","1234 5678 8901","1234 5678 9012"]
# print("welcome to ATM")
# ac_no=str(input("enter your a/c no: "))
# if ac_no in ac_data:
#     pin=str(input("enter your pin:"))
#     balance=5000.0
#     if ac_no!=" " and pin!=" ":
#        print("welcome customer xyz")
#        x="mini statment"
#        y="deposit"
#        z="withdrawl"
#        user_choice=(str(input("select from mini statement | deposit |withdrawl")))
#     if user_choice==x:
#        print("welcome to mini statemnet")
#        print("your balance amount is ",balance)

#     elif user_choice==y:
#         print("welcome to deposit")
#         deposit=float(input("enter amount to deposit"))
#         balance+=deposit
#         print("your balance amount is",balance)

#     elif user_choice==z:
#         print("welcome to withdrawl")
#         withdraw=float(input("enter withdraw amount:"))
#         if balance<=withdraw:
#             balance-=withdraw
#             print("collect your cash",withdraw)
#             print("check your balance",balance)
#         else:
#             print("insufficent funds")
#             print("your balance is :",balance)
#     else:
#         print("please select from the list")
# else:
#     print("please enter a valid a/c no and pin")




a={"1235 5678 9012";"pin":1234;"user":"xyz";"balance":10000.00}
   ,"3456 7890 1234":{"pin":3456,"user":"abc","balance":15000.00}
print(a["1234 5678 9012"][0])
print(a["3456 7890 1234"]["pin"])
