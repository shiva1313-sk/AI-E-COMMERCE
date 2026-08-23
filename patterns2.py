
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
#      print(" "*(5-i-1)*2,end="")
#      print("* "*(i+1))
# for j in range(4,0,-1):
#      print(" "*(4-j+1)*2,end="")
#      print("* "*(j+1-1))


# for i in range(5,0,-1):
#      print("* "*(i))


# a b c d e 
#   f g h i 
#     j k l 
#       m n 
#         o 

# x=97
# for i in range(5,0,-1):
#     print(" "*(5-i)*2,end="")
#     for j in range(i):
#         print(chr(x),end=" ")
#         x+=1
        

#     print()


#         1 
#       1 2 3 
#     1 2 3 4 5 
#   1 2 3 4 5 6 7 
# 1 2 3 4 5 6 7 8 9 



# for i in range(5):
#     x=1
#     print(" "*(5-i-1)*2,end="")
#     for j in range(2*i+1):
#         print(x,end=" ")
#         x+=1
#     print()



#         1 
#       1 2 
#     1 2 3 
#   1 2 3 4 
# 1 2 3 4 5 

# for i in range(5):
#     x=1
#     print(" "*(5-i-1)*2,end="")
#     for j in range(i+1):
#         print(x,end=" ")
#         x+=1
#     print()

# #       1  
#        1  1  
#       1  2  1  
#      1  3  3  1  
#     1  4  6  4  1  
#    1  5  10  10  5  1  
#   1  6  15  20  15  6  1

# for i in range(7):
#     x=1
#     print(" "*(7-i),end=" ")
#     for j in range(i+1):
#         print(x,end="  ")
#         x=x*(i-j)//(j+1)
#     print()


# 1
# 1^2
# 1^2^3
# 1^2^3^4
# 1^2^3^4^5

# for i in range(5):
#     x=1
#     m=""
#     for j in range(i+1):
#         m+=(str(x)+"^")
#         x+=1
#     print(m.rstrip("^"))

