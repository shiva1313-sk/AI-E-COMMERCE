# x="*"
# for i in range(5): #range(0,5,+1)
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(x,end=" ")

#     print() 


# x=1
# for i in range(5): #range(0,5,+1)
#      for j in range(i+1):#range(0,i+1=1,1)
#         print(x,end=" ")
#         x=x+1
#      print()




# x=1
# for i in range(5): #range(0,5,+1)
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(x,end=" ")
#     x=x+1
#     print()



# x=97
# for i in range(5): #range(0,5,+1)
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(chr(x),end=" ")
#         x+=1
#     print()



# x=97
# for i in range(5): #range(0,5,+1)
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(chr(x),end=" ")
#     x=x+1
#     print()



# for i in range(5): #range(0,5,+1)
#     x=1
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(x,end=" ")
#         x=x+1
#     print()


# for i in range(5): #range(0,5,+1)
#     x=97
#     for j in range(i+1):#range(0,i+1=1,1)
#         print(chr(x),end=" ")
#         x=x+1
#     print()



# x="*"
# for i in range(5):
#     for i in range(2*i+1):
#         print(x,end=" ")
     
#     print()


#negatives .....!
''
# * * * * *
# * * * *
# * * *
# * *
# *
''
# x="*"
# for i in range(5,0,-1):
#     for i in range(i):
#         print(x,end=" ")
        
      
#     print()
''
# a b c d e 
# f g h i 
# j k l 
# m n 
# o 
''

# x=97
# for i in range(5,0,-1):
#     for i in range(i):
#         print(chr(x),end=" ")
#         x+=1
      
#     print()
''
# a a a a a 
# b b b b 
# c c c
# d d
# e
''
# x=97
# for i in range(5,0,-1):
#     for i in range(i):
#         print(chr(x),end=" ")
#     x+=1
      
#     print()
''
# 1 2 3 4 5 
# 6 7 8 9 
# 10 11 12
# 13 14
# 15
''
# x=1
# for i in range(5,0,-1):
#     for i in range(i):
#         print(x,end=" ")
#         x+=1
      
#     print()
""
# 1 1 1 1 1 
# 2 2 2 2 
# 3 3 3
# 4 4
# 5
""

# x=1
# for i in range(5,0,-1):
#     for i in range(i):
#         print(x,end=" ")
#     x+=1
      
#     print()

"""
# 5 5 5 5 5 
# 4 4 4 4 
# 3 3 3
# 2 2
# 1
"""

# x=5
# for i in range(5,0,-1):
#     for i in range(i):
#         print(x,end=" ")
#     x-=1
      
#     print()

# x="*"
# for i in range(4,0,-1):
#     for j in range(2*i-1):
#         print(x,end=" ")

#     print()

# 1 2 3 4 5 
# 2 3 4 5 1 
# 3 4 5 1 2 
# 4 5 1 2 3 
# 5 1 2 3 4 

# for i in range(1,6):
#     for j in range(i,i+5):
#      if j<=5:
#         print(j,end=" ")
#      else:
#         print(j-5,end=" ")
#     print()


# ''
# a b c d e 
# b c d e a 
# c d e a b 
# d e a b c 
# e a b c d 

# ''


# for i in range(97,102):
#     for j in range(i,i+5):
#      if j<=101:
#         print(chr(j),end=" ")
#      else:
#         print(chr(j-5),end=" ")
    
#     print()

#     ''   * 
#        * * 
#      * * *
#    * * * *
#  * * * * *  ''
   
# for i in range(5):
#     print(" "*(5-i-1)*2,end=" ")
#     print("* "*(i+1))



#          * 
#        * * * 
#      * * * * *
#    * * * * * * *
#  * * * * * * * * *

# for i in range(5,0,-1):
#     print(" "*(5-i)*2,end="")
#     print("* "*(i))


# * * * * * 
#   * * * * 
#     * * * 
#       * * 
#         * 


# for i in range(5,0,-1):
#     print(" "*(5-i)*2,end="")
#     print("* "*(i))

#   * * * * * * * * * 
#     * * * * * * * 
#       * * * * *
#         * * *
#           *


# for i in range(5,0,-1):
#     print(" "*(5-i)*2,end="")
#     print("* "*(2*i-1))

#         * 
#       * * * 
#     * * * * * 
#   * * * * * * * 
# * * * * * * * * * 
#   * * * * * * * 
#     * * * * * 
#       * * * 
#         *



# for i in range(5):
#     print(" "*(5-i-1)*2,end="")
#     print("* "*(2*i+1))
# for j in range(4,0,-1):
#     print(" "*(5-j)*2,end="")
#     print("* "*(2*j-1))


# # # # # * # # # # 
# # # # * * * # # # 
# # # * * * * * # # 
# # * * * * * * * # 
# * * * * * * * * * 
# # * * * * * * * # 
# # # * * * * * # # 
# # # # * * * # # # 
# # # # # * # # # #

# for i in range(5):
#     print("# "*(5-i-1),end="")
#     print("* "*(2*i+1),end="")
#     print("# "*(5-i-1))
# for j in range(4,0,-1):
#     print("# "*(4-j+1),end="")
#     print("* "*(2*j-1),end="")
#     print("# "*(4-j+1))

#         * 
#       * * 
#     * * * 
#   * * * * 
# * * * * * 
#   * * * * 
#     * * * 
#       * * 
#         *

# for i in range(5):
#     print(" "*(5-i-1)*2,end="")
#     print("* "*(i+1))
# for j in range(4,0,-1):
#     print(" "*(4-j+1)*2,end="")
#     print("* "*(j+1-1))


