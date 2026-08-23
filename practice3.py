


#ATM PROJECT

# a_c_data=["1234 5678 9012","5678 9012 3456","3456 7890 1234"]
# print("welcome to atm")
# ac_no=str(input("enter your a/c no:"))
# data = {"1234 5678 9012":{"pin":1234,"user":"xyz","balance":10000.00}
#         ,"3456 7890 1234":{"pin":3456,"user":"mno","balance":15000.00}
#         ,"4567 8901 2345":{"pin":5678,"user":"abc","balance":50000.00}}
# if ac_no in a_c_data:
#     pin=int(input("enter your pin:"))
#     if pin ==data[ac_no]["pin"]:
#         print("welcome customer",data[ac_no]["user"])
#         balance = data[ac_no]["balance"]
#         x="mini-statement"
#         y="deposit"
#         z="withdrawl"
#         user_choice=str(input("select from minin statement|deposit|withdrawl:"))
#         if user_choice==x:
#             print("welcome to mini statement")
#             print("your balance amount is",balance)
#         elif user_choice==y:
#             print("welcome to deposit")
#             deposit=float(input("enter amount to deposit:"))
#             balance+=deposit
#             print("your balance amount is",balance)
#         elif user_choice==z:
#             print("welcome to withdrawl space")
#             withdraw=float(input("enter withdrawl amount:"))
#             if balance>=withdraw:
#                 balance-=withdraw
#                 print("print collect cash of",withdraw)
#                 print("your balance amount is",balance)
#             else:
#                 print("sorry insufficient funds")
#                 print("your balance amount is ",balance)
#         else:
#             print("please select from mini-statement|deposit|withdrawl")
#     else:
#         print("please enter valid pin")
# else:
#     print("enter valid ac_no")




# x=1
# while x<10:
#     print(x)
#     x+=1




# x=10
# while x>=1:
#     print(x)
#     x-=1



# ['a', 'b', 100, 45.56, 100, 'hello', '100', '45.56']
# ['a', 'b', '*', 45.56, '*', 'hello', '100', '45.56']


# x=["a","b",100,45.56,100,"hello","100","45.56"]

# y=x[2]
# z=0
# m=len(x)
# print(x)
# while z<m:
#     if x[z]==y:
#         x[z]="*"
#     z+=1
# print(x)